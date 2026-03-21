

from agents.agent_data_models import OrchRouteQuery,EditFilesRouteQuery,ChatRouterQuery
from langchain_core.prompts import ChatPromptTemplate
import os
from typing import Literal
from pydantic import BaseModel, Field
from services.llm_client.llm_client import LLMClient
from typing import Union,Literal,Dict,Any
from agents.prompts.router_prompts import DECOMPOSE_ROUTER_SYS_PROMPT,EDIT_FILES_ROUTER_SYS_PROMPT

from dotenv import load_dotenv
load_dotenv()

class RouterAgents:

    router_llm = os.getenv("ROUTER_LLM", 'llama3.1:8b')
    chat_router_llm = os.getenv("CHAT_ROUTER_LLM", 'llama3.1:8b')


    def __init__(self,provider: Literal["ollama","openai","anthropic"],**values):
        self.llm_client = LLMClient()
        self.provider = provider
        self.language_model = os.getenv("DEFAULT_OLLAMA_MODEL", 'llama3.1:8b')
        self.default_model = 'llama3.1:8b'
        super().__init__(**values)
        

        # this is a router to decide whether to decompose the task or require more information
    def planner_router_llm_f(self,query: str, chat_context: str|None = "")-> Union[OrchRouteQuery, Dict[str, Any]]:
        router_llm = self.llm_client.init_ollama(
                provider=self.provider,
                model=self.router_llm or self.default_model, # this the default value
                temperature=0,
                reasoning=None
                )
        
        structured_llm_router = router_llm.with_structured_output(OrchRouteQuery)

        system_prompt = DECOMPOSE_ROUTER_SYS_PROMPT

        human_message = "User query: {query} \n chat context: {chat_context}"

        router_prompt = ChatPromptTemplate.from_messages(
            [
                ('system',system_prompt),
                ('human',human_message)
            ]
        )

        question_router = router_prompt | structured_llm_router

        route = question_router.invoke(
            {"query": query, "chat_context": chat_context}
        )

        return route

    # this is a router to decide wether the task require the editing of files or not
    def edit_files_router_llm_f(self,query: str)-> Union[EditFilesRouteQuery, Dict[str, Any]]:
        router_llm = self.llm_client.init_ollama(
                provider=self.provider,
                model=self.router_llm or self.default_model,
                temperature=0,
                reasoning=None
            )
        
        structured_llm_router = router_llm.with_structured_output(EditFilesRouteQuery)

        system_prompt = EDIT_FILES_ROUTER_SYS_PROMPT

        human_message = "Plan to analyze: {query}"

        router_prompt = ChatPromptTemplate.from_messages(
            [
                ('system',system_prompt),
                ('human',human_message)
            ]
        )

        question_router = router_prompt | structured_llm_router

        route = question_router.invoke(
            {"query": query}
        )

        return route

    def chat_router_llm_f(self,query: str, context: str)-> Union[ChatRouterQuery, Dict[str, Any]]:
            
            chat_router_llm = self.llm_client.init_ollama(
                    provider=self.provider,
                    model=self.chat_router_llm or self.default_model,
                    temperature=0,
                    reasoning=None
                )
            structured_llm_router = chat_router_llm.with_structured_output(ChatRouterQuery)

            system_prompt = """
            You are a router that decides whether the user query is a agentic or a chat.
            If the user query requires multiple steps to verify the answer, then it is a agentic.
            If the user query can be answered in a single step, then it is a chat.
            If to anwer the users query requires the use of tools, then it is a agentic.
            If the user query is a question, then it is a agentic.
            If the user query is a command, then it is a agentic.
            If the user query is a request, then it is a agentic.
            If the user query is a statement, then it is a agentic.
            
            EXAMPLES:
            User query: "hello"
            Chat history: ""
            Route: "chat"

            User query: "what is the capital of France?"
            Chat history: ""
            Route: "agentic"

            User query: "write a python program to sort a list and save the file as sorted.py"
            Chat history: "you are a python expert"
            Route: "agentic"

            User query: "what is the capital of France?"
            Chat history: "hello"
            Route: "agentic"

            
            """

            user_message = "The user query is: {query}\n The chat history is: {context}"
        
            router_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", user_message),
                ]
            )
            chat_router = router_prompt | structured_llm_router

            route = chat_router.invoke(
                {"query": query, "context": context}
            )
            return route   

            
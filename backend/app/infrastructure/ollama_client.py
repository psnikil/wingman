import subprocess
import time
import sys
import os
import socket

from fastapi import APIRouter, HTTPException
from langchain_ollama import OllamaLLM as Ollama
from langchain_core.prompts import ChatPromptTemplate
import ollama

# OLLAMA_URL = "http://localhost:11434"


def is_ollama_running(host="localhost", port=11434):
    """Check if the Ollama server is listening on the default port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        return sock.connect_ex((host, port)) == 0
    
def start_ollama():
    """Start Ollama in the background."""
    print("Starting Ollama server...")
    try:
        if os.name == 'nt':  # Windows
            subprocess.Popen("start ollama serve", shell=True)
            return True
        else:  # macOS/Linux
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error starting Ollama: {e}")
        sys.exit(1)

def list_ollama_models():
    """List available models in Ollama."""
    models_names = []
    try:
        models = ollama.list()['models']
        # print(f'current model val is',models)
        # print(f"Found {len(models)} models.")
        if not models:
            print("⚠️ No models found. Please run: `ollama pull llama3` or similar.")
            return []
        print("📦 Available models:",models[0]['model'])
        
        for model in models:
            print(f"{model['model']}")
            models_names.append(model['model'])
        return models_names
    except Exception as e:
        print(f"Error listing models: {e}")
        return []

def wait_for_ollama(timeout=15):
    """Wait until Ollama is ready."""
    print("Waiting for Ollama to be ready...")
    for _ in range(timeout):
        if is_ollama_running():
            print("✅ Ollama is running.")
            models = list_ollama_models()
            print("Available models:", models)
            return True
        time.sleep(1)
    print("❌ Ollama did not start in time.")
    return False

def get_available_models():
    """Get a list of available models."""
    if not is_ollama_running():
        if not wait_for_ollama():
            print("❌ Failed to start Ollama.")
            return []
    return list_ollama_models()

def chat_with_model(model_name, sys_prompt=" You are a helpful assistant. Answer the user's question based on the provided context."):
    """Send a prompt to the selected model."""
    template = '''
    System prompt: {sys_prompt}
    Context: {context}  
    User's question: {question}
    Answer:
    '''
    context = ''
    try:
        chat_model = Ollama(model=model_name)
        prompt_template = ChatPromptTemplate.from_template(template)
        chain = prompt_template | chat_model
        print(f"\n💬 Starting chat with model `{model_name}`, type exit to quit")
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Exiting chat.")
                break


            print('sending user prompt')
            response = chain.invoke({
                "sys_prompt": sys_prompt,
                "context": context,
                "question": user_input
                })
            print(f"Model: {response}")
            context += f"\nUser: {user_input}\nModel: {response}"


        
    except Exception as e:
        return f"❌ Error during chat: {e}"
    
def generate_llm_response(prompt: str, model: str,context:str = '') -> str:
    """Send a prompt to the selected model."""
    template = '''
    System prompt: {sys_prompt}
    Context: {context}  
    User's question: {question}
    Answer:
    '''
    # context = ''
    print(f"Generating response for prompt: {prompt} using model: {model} and context: {context}")
    try:
        if not model:
            print("❌ No model specified. Please provide a valid model name.")
            raise HTTPException(status_code=404, detail=str(e))
        chat_model = Ollama(model=model)
        prompt_template = ChatPromptTemplate.from_template(template)
        chain = prompt_template | chat_model
        
        response = chain.invoke({
            "sys_prompt": "You are a helpful assistant. Answer the user's question based on the provided context.",
            "context": context,
            "question": prompt
            })
        return response
    
    except Exception as e:
        print(f"❌ Error during LLM generation: {e}")
        return str(e)   


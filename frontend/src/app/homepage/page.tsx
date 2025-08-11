/* 
This is the homepage of the user post the login/set up. This page shows the user their chats.
clicking on the chats should redirect the user to the chats page with the chat id and any other parameters. 
*/

import HomePageClient from './HomePageClient';

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  isLoading?: boolean;
}

export interface Chat {
  chatId: string;
  chatName: string;
  chatSummary: string;
  messages?: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Payload {
  data:any
}


// //Deprecated:this function generates a random 16byte hex value
// function NumberGenerator(){
//   const randomByteString = crypto.randomBytes(16).toString('hex');
//   return '/chatpage/'+ randomByteString;
// }

// //Create new chat from prompt
// function createNewChat(prompt: string) {

//     const addChat = useChatStore((state) => state.addChat);
//     const addMessage = useChatStore((state) => state.addMessage);

//     console.log("User prompt:", prompt);
    
//     let newMessage:Message = {
//       id: crypto.randomBytes(16).toString('hex'),
//       content: prompt,
//       role: 'user',
//       timestamp: new Date(),
//       isLoading: false
//     };
//     //Temporary logic to create a new chat
//     let newChat:Chat = {
//       chatId: crypto.randomBytes(16).toString('hex'),
//       chatName: `New Chat: ${prompt.substring(0, 6)}`,
//       chatSummary: prompt.substring(0, 20),
//       messages: [],
//       createdAt: new Date(),
//       updatedAt: new Date()
//     };
//     addChat(newChat) // Add new chat to the list
//     addMessage(newChat.chatId,newMessage);



// }


export default function Homepage() {
  return <HomePageClient />;
}
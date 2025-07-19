/* 
This is the homepage of the user post the login/set up. This page shows the user their chats.
clicking on the chats should redirect the user to the chats page with the chat id and any other parameters. 
*/

import crypto from 'crypto';

//this function generates a random 16byte hex value
function NumberGenerator(){
  const randomByteString = crypto.randomBytes(16).toString('hex');
  return '/chatpage/'+ randomByteString;
}
export default function Homepage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-background text-foreground">
      <h1 className="text-2xl font-bold">Welcome to the Homepage</h1>
      <p className="mt-4 text-lg">This is the main page after login.</p>
      <p className="mt-4 text-lg">Test: go to the chat page with a random id  <a href={NumberGenerator()} target="_blank" rel="noopener noreferrer"> CHATPAGE </a></p>
    </div>
  );
}
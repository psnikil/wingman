/* 
This is the chat page for a specific chatid.

*/

interface ChatPageProps {
    params: {
        chatID: string;
    }
}


export default function ChatPage({ params }: ChatPageProps) {
  const { chatID } = params;

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-background text-foreground">
      <h1 className="text-2xl font-bold">Chat Page</h1>
      <p className="mt-4 text-lg">You are viewing chat with ID: {chatID}</p>
      {/* Additional chat functionalities can be added here */}
    </div>
  );
}
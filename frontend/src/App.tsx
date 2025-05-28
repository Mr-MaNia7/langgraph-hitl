import { useState, useEffect } from 'react';
import axios from 'axios';
import { ChatResponse, Message, Plan } from './types';
import { Button } from './components/ui/button';
import { Send, Loader2 } from 'lucide-react';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState('');
  const [currentPlan, setCurrentPlan] = useState<Plan | null>(null);

  useEffect(() => {
    const initChat = async () => {
      try {
        const response = await axios.get<ChatResponse>('/api/chat_initiate', {
          params: { thread_id: Date.now().toString() }
        });
        setThreadId(response.data.messages[0]?.content || '');
        setMessages(response.data.messages);
        setCurrentPlan(response.data.current_plan || null);
      } catch (error) {
        console.error('Failed to initialize chat:', error);
      }
    };
    initChat();
  }, []);

  const handleSubmit = async () => {
    if (!input.trim()) return;

    setIsLoading(true);
    try {
      const response = await axios.get<ChatResponse>('/api/chat-continue', {
        params: {
          thread_id: threadId,
          response: input
        }
      });

      setMessages(response.data.messages);
      setCurrentPlan(response.data.current_plan || null);
      setInput('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-center mb-8">Confirmation Agent</h1>
          
          {/* Chat Messages */}
          <div className="bg-card rounded-lg shadow-lg p-4 mb-4 h-[60vh] overflow-y-auto">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`mb-4 p-3 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground ml-auto'
                    : 'bg-muted'
                } max-w-[80%] ${message.role === 'user' ? 'ml-auto' : 'mr-auto'}`}
              >
                <p className="text-sm">{message.content}</p>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-center my-4">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            )}
          </div>

          {/* Current Plan Display */}
          {currentPlan && (
            <div className="bg-card rounded-lg shadow-lg p-4 mb-4">
              <h2 className="text-xl font-semibold mb-2">Current Plan</h2>
              <div className="space-y-2">
                <p><strong>Goal:</strong> {currentPlan.goal}</p>
                <p><strong>Complexity:</strong> {currentPlan.analysis.complexity}</p>
                <p><strong>Estimated Time:</strong> {currentPlan.analysis.estimated_total_time}</p>
                
                <div className="mt-4">
                  <h3 className="font-semibold mb-2">Subtasks:</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {currentPlan.analysis.subtasks.map((subtask, index) => (
                      <li key={index}>
                        {subtask.description} ({subtask.estimated_time})
                      </li>
                    ))}
                  </ul>
                </div>

                {currentPlan.analysis.potential_risks.length > 0 && (
                  <div className="mt-4">
                    <h3 className="font-semibold mb-2">Potential Risks:</h3>
                    <ul className="list-disc pl-5 space-y-1">
                      {currentPlan.analysis.potential_risks.map((risk, index) => (
                        <li key={index} className="text-destructive">{risk}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
              placeholder="Type your message..."
              className="flex-1 px-4 py-2 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <Button
              onClick={handleSubmit}
              disabled={isLoading}
              className="flex items-center gap-2"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              Send
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App; 
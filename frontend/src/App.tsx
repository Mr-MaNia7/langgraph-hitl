import { useState, useEffect, MouseEvent } from 'react';
import axios from 'axios';
import { ChatResponse, Message, Plan } from './types';
import { Button } from './components/ui/button';
import { Send, Loader2 } from 'lucide-react';

function formatMessage(message: string, clarificationQuestions?: string[], concerns?: string[]) {
  // Try to parse as JSON, otherwise return as plain text
  try {
    const data = JSON.parse(message);
    // PLAN CARD
    if (data.type === 'plan') {
      return (
        <div className="bg-white/90 border border-border rounded-2xl shadow-sm p-5 space-y-4">
          <div className="font-bold text-xl text-primary mb-2">{data.title}</div>
          <div className="space-y-1">
            <div><span className="font-semibold">Goal:</span> {data.goal}</div>
            <div><span className="font-semibold">Complexity:</span> {data.analysis.complexity}</div>
            <div><span className="font-semibold">Estimated Time:</span> {data.analysis.estimated_time}</div>
            {data.analysis.resources && (
              <div><span className="font-semibold">Resources:</span> {data.analysis.resources.join(', ')}</div>
            )}
          </div>
          {data.actions && data.actions.length > 0 && (
            <div>
              <div className="font-semibold mb-2">Actions:</div>
              <div className="space-y-3">
                {data.actions.map((a: any, i: number) => (
                  <div
                    key={i}
                    className="bg-muted/60 border border-border rounded-lg p-3 text-sm font-mono"
                  >
                    <div className="font-bold text-primary mb-1">{a.type || a.description}</div>
                    <ul className="mb-1">
                      {Object.entries(a.parameters).map(([key, value]) => (
                        <li key={key}>
                          <span className="font-semibold">{key}:</span>{' '}
                          <span className="font-normal">{String(value)}</span>
                        </li>
                      ))}
                    </ul>
                    <div className="italic text-xs text-muted-foreground">({a.status})</div>
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className="pt-2">
            <span className="font-semibold">Status:</span> {data.status}
          </div>
        </div>
      );
    }
    // EXECUTION RESULTS CARD
    if (data.type === 'execution_results') {
      return (
        <div className="bg-green-50 border border-green-200 rounded-2xl shadow-sm p-5 space-y-3">
          <div className="font-bold text-lg text-green-800 flex items-center gap-2">
            <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"></polyline></svg>
            {data.title}
          </div>
          <div className="text-green-900 font-medium">Status: {data.status}</div>
          {data.results && data.results.length > 0 && (
            <div>
              <b>Results:</b>
              <ul className="list-disc pl-5 mt-1">
                {data.results.map((r: string, i: number) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          )}
          {data.summary && (
            <div className="text-xs text-green-800 mt-2">
              <b>Summary:</b> {data.summary.completed_actions} of {data.summary.total_actions} actions completed, {data.summary.failed_actions} failed.
            </div>
          )}
        </div>
      );
    }
    // CLARIFICATION CARD
    if (data.type === 'clarification' || data.type === 'clarification_request') {
      return (
        <div className="bg-yellow-50 border border-yellow-200 rounded-2xl shadow-sm p-5 space-y-3">
          <div className="font-bold text-lg text-yellow-700 mb-1">{data.title || 'Clarification Needed'}</div>
          {data.questions && data.questions.length > 0 && (
            <div>
              <b>Questions:</b>
              <ul className="list-disc pl-5 text-yellow-800">
                {data.questions.map((q: string, i: number) => (
                  <li key={i}>{q}</li>
                ))}
              </ul>
            </div>
          )}
          {data.concerns && data.concerns.length > 0 && (
            <div className="text-yellow-800 bg-yellow-100 rounded p-2 mt-2">
              <b>Concerns:</b>
              <ul className="list-disc pl-5">
                {data.concerns.map((c: string, i: number) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            </div>
          )}
          {data.suggestions && data.suggestions.length > 0 && (
            <div className="text-blue-700 bg-blue-50 rounded p-2 mt-2">
              <b>Suggestions:</b>
              <ul className="list-disc pl-5">
                {data.suggestions.map((s: string, i: number) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      );
    }
    // MODIFICATION REQUEST CARD
    if (data.type === 'modification_request') {
      return (
        <div className="bg-blue-50 border border-blue-200 rounded-2xl shadow-sm p-5 space-y-2">
          <div className="font-bold text-lg text-blue-700 mb-1">{data.title}</div>
          <div>{data.message}</div>
          {data.current_plan && <div className="text-xs text-blue-900"><b>Current Plan:</b> {data.current_plan}</div>}
        </div>
      );
    }
    // fallback for unknown types
    return <span>{data.message || message}</span>;
  } catch {
    // Not JSON, just return as plain text
    // If clarificationQuestions or concerns are present, show them
    return (
      <div>
        <span>{message}</span>
        {clarificationQuestions && clarificationQuestions.length > 0 && (
          <div className="mt-2 text-yellow-700">
            <b>Clarification Needed:</b>
            <ul className="list-disc pl-5">
              {clarificationQuestions.map((q, i) => (
                <li key={i}>{q}</li>
              ))}
            </ul>
          </div>
        )}
        {concerns && concerns.length > 0 && (
          <div className="mt-2 text-yellow-800 bg-yellow-50 rounded p-2">
            <b>Concerns:</b>
            <ul className="list-disc pl-5">
              {concerns.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState('');
  const [currentPlan, setCurrentPlan] = useState<Plan | null>(null);
  const [clarificationQuestions, setClarificationQuestions] = useState<string[] | undefined>(undefined);
  const [concerns, setConcerns] = useState<string[] | undefined>(undefined);

  useEffect(() => {
    const newThreadId = Date.now().toString();
    setThreadId(newThreadId);
    // Start a new chat session
    axios.get<ChatResponse>('/api/chat_initiate', {
      params: { thread_id: newThreadId }
    }).then(response => {
      setMessages(response.data.messages);
      setCurrentPlan(response.data.current_plan || null);
      setClarificationQuestions(response.data.clarification_questions);
      setConcerns(response.data.concerns);
    });
  }, []); // Empty dependency array means this runs once on mount

  const handleSubmit = async (message?: string) => {
    const msg = message || input.trim();
    if (!msg) return;

    setIsLoading(true);
    try {
      const response = await axios.get<ChatResponse>('/api/chat-continue', {
        params: {
          thread_id: threadId,
          response: msg
        }
      });

      setMessages(response.data.messages);
      setCurrentPlan(response.data.current_plan || null);
      setClarificationQuestions(response.data.clarification_questions);
      setConcerns(response.data.concerns);
      if (!message) {
        setInput('');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCommand = (command: string) => (e: MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    void handleSubmit(command);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Sticky Header */}
      <div className="sticky top-0 z-20 bg-background shadow-md py-4 mb-4">
        <h1 className="text-3xl font-bold text-center">Confirmation Agent</h1>
      </div>
      <div className="container mx-auto flex-1 flex flex-col md:flex-row relative">
        {/* Floating Plan Card */}
        {currentPlan && currentPlan.status !== "completed" && (
          <div
            className="md:fixed md:top-24 md:right-8 md:w-96 w-full z-30 md:rounded-xl md:shadow-2xl bg-card p-4 mb-4 md:mb-0"
            style={{ maxHeight: '80vh', overflowY: 'auto' }}
          >
            <div className="flex justify-between items-start mb-3">
              <h2 className="text-xl font-semibold">Current Plan</h2>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-1"
                  onClick={handleCommand("confirm")}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-check">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  Confirm
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-1"
                  onClick={handleCommand("modify")}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-sync">
                    <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path>
                    <path d="M21 3v5h-5"></path>
                    <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path>
                    <path d="M8 16H3v5"></path>
                  </svg>
                  Modify
                </Button>
              </div>
            </div>
            {/* Pills for plan meta info */}
            <div className="flex flex-wrap gap-2 mb-4">
              <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">Goal: {currentPlan.goal}</span>
              <span className="px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-xs font-semibold">Complexity: {currentPlan.analysis.complexity}</span>
              <span className="px-3 py-1 rounded-full bg-yellow-100 text-yellow-800 text-xs font-semibold">Estimated: {currentPlan.analysis.estimated_total_time}</span>
              <span className="px-3 py-1 rounded-full bg-gray-200 text-gray-800 text-xs font-semibold">Status: {currentPlan.status}</span>
            </div>
            {/* Subtasks as pills */}
            <div className="mb-2">
              <h3 className="font-semibold mb-1 text-sm">Subtasks</h3>
              <div className="flex flex-wrap gap-2">
                {currentPlan.analysis.subtasks.map((subtask, index) => (
                  <span key={index} className="px-3 py-1 rounded-full bg-muted/70 text-xs">
                    {subtask.description} <span className="text-muted-foreground">({subtask.estimated_time})</span>
                  </span>
                ))}
              </div>
            </div>
            {/* Risks as pills */}
            {currentPlan.analysis.potential_risks.length > 0 && (
              <div className="mb-2">
                <h3 className="font-semibold mb-1 text-sm">Potential Risks</h3>
                <div className="flex flex-wrap gap-2">
                  {currentPlan.analysis.potential_risks.map((risk, index) => (
                    <span key={index} className="px-3 py-1 rounded-full bg-destructive/10 text-destructive text-xs">
                      {risk}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        {/* Main Chat Area (with margin if plan card is floating) */}
        <div className="flex-1 flex flex-col md:pr-[420px]">
          {/* Chat Messages */}
          <div className="bg-background border rounded-lg flex-1 overflow-y-auto flex flex-col gap-1 p-2 md:p-3 mb-2">
            {messages.map((message, index) => (
              <div
                key={index}
                className="flex items-start"
              >
                <div className="max-w-[90%] px-3 py-1.5 rounded-xl shadow-sm bg-muted text-foreground text-sm leading-snug">
                  {formatMessage(message.content, clarificationQuestions, concerns)}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-center my-2">
                <Loader2 className="h-5 w-5 animate-spin" />
              </div>
            )}
          </div>
          {/* Sticky Input Area */}
          <div className="sticky bottom-0 left-0 right-0 bg-background pt-1 pb-2 z-10 border-t">
            <div className="flex gap-1">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
                placeholder="Type your message..."
                className="flex-1 px-3 py-1.5 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring text-sm"
              />
              <Button
                onClick={() => handleSubmit()}
                disabled={isLoading}
                className="flex items-center gap-1 px-3 py-1.5 text-sm"
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
    </div>
  );
}

export default App; 
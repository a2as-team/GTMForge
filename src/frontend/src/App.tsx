import { useState, useRef, useCallback, useEffect } from "react";
import { v4 as uuidv4 } from 'uuid';
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { ProgressDashboard } from "@/components/ProgressDashboard";
import { ChatMessagesView } from "@/components/ChatMessagesView";
import PageTransition from "@/components/animations/PageTransition";

// Update DisplayData to be a string type
type DisplayData = string | null;
interface MessageWithAgent {
  type: "human" | "ai";
  content: string;
  id: string;
  agent?: string;
  finalReportWithCitations?: boolean;
}



interface ProcessedEvent {
  title: string;
  data: Record<string, unknown>;
}

export default function App() {
  const agentName = import.meta.env.VITE_AGENT_NAME || "forge";
  const [userId, setUserId] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [appName, setAppName] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessageWithAgent[]>([]);
  const [displayData, setDisplayData] = useState<DisplayData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [messageEvents, setMessageEvents] = useState<Map<string, ProcessedEvent[]>>(new Map());
  const [websiteCount, setWebsiteCount] = useState<number>(0);
  const [isBackendReady, setIsBackendReady] = useState(false);
  const [isCheckingBackend, setIsCheckingBackend] = useState(true);
  const currentAgentRef = useRef('');
  const accumulatedTextRef = useRef("");
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const [showChat, setShowChat] = useState(false);

  const retryWithBackoff = useCallback(async (
    fn: () => Promise<unknown>,
    maxRetries: number = 10,
    maxDuration: number = 120000 // 2 minutes
  ): Promise<unknown> => {
    const startTime = Date.now();
    let lastError: Error;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      if (Date.now() - startTime > maxDuration) {
        throw new Error(`Retry timeout after ${maxDuration}ms`);
      }

      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;
        const delay = Math.min(1000 * Math.pow(2, attempt), 5000); // Exponential backoff, max 5s
        console.log(`Attempt ${attempt + 1} failed, retrying in ${delay}ms...`, error);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    throw lastError!;
  }, []);

  const createSession = useCallback(async (): Promise<{ userId: string, sessionId: string, appName: string }> => {
    const generatedSessionId = uuidv4();
    const response = await fetch(`/api/apps/${agentName}/users/u_999/sessions/${generatedSessionId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to create session: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return {
      userId: data.userId,
      sessionId: data.id,
      appName: data.appName
    };
  }, [agentName]);

  const checkBackendHealth = async (): Promise<boolean> => {
    try {
      // Use the docs endpoint or root endpoint to check if backend is ready
      const response = await fetch("/api/docs", {
        method: "GET",
        headers: {
          "Content-Type": "application/json"
        }
      });
      return response.ok;
    } catch (error) {
      console.log("Backend not ready yet:", error);
      return false;
    }
  };

  // Function to extract text and metadata from SSE data
  const extractDataFromSSE = (data: string) => {
    try {
      const parsed = JSON.parse(data);
      console.log('[SSE PARSED EVENT]:', JSON.stringify(parsed, null, 2)); // DEBUG: Log parsed event

      let textParts: string[] = [];
      let agent = '';
      let finalReportWithCitations = undefined;
      let functionCall = null;
      let functionResponse = null;
      let sources = null;

      // Check if content.parts exists and has text
      if (parsed.content && parsed.content.parts) {
        textParts = parsed.content.parts
          .filter((part: { text?: string }) => part.text)
          .map((part: { text: string }) => part.text);

        // Check for function calls
        const functionCallPart = parsed.content.parts.find((part: { functionCall?: unknown }) => part.functionCall);
        if (functionCallPart) {
          functionCall = functionCallPart.functionCall;
        }

        // Check for function responses
        const functionResponsePart = parsed.content.parts.find((part: { functionResponse?: unknown }) => part.functionResponse);
        if (functionResponsePart) {
          functionResponse = functionResponsePart.functionResponse;
        }
      }

      // Extract agent information
      if (parsed.author) {
        agent = parsed.author;
        console.log('[SSE EXTRACT] Agent:', agent); // DEBUG: Log agent
      }

      if (
        parsed.actions &&
        parsed.actions.stateDelta &&
        parsed.actions.stateDelta.final_report_with_citations
      ) {
        finalReportWithCitations = parsed.actions.stateDelta.final_report_with_citations;
      }

      // Extract website count from research agents
      let sourceCount = 0;
      if ((parsed.author === 'section_researcher' || parsed.author === 'enhanced_search_executor')) {
        console.log('[SSE EXTRACT] Relevant agent for source count:', parsed.author); // DEBUG
        if (parsed.actions?.stateDelta?.url_to_short_id) {
          console.log('[SSE EXTRACT] url_to_short_id found:', parsed.actions.stateDelta.url_to_short_id); // DEBUG
          sourceCount = Object.keys(parsed.actions.stateDelta.url_to_short_id).length;
          console.log('[SSE EXTRACT] Calculated sourceCount:', sourceCount); // DEBUG
        } else {
          console.log('[SSE EXTRACT] url_to_short_id NOT found for agent:', parsed.author); // DEBUG
        }
      }

      // Extract sources if available
      if (parsed.actions?.stateDelta?.sources) {
        sources = parsed.actions.stateDelta.sources;
        console.log('[SSE EXTRACT] Sources found:', sources); // DEBUG
      }


      return { textParts, agent, finalReportWithCitations, functionCall, functionResponse, sourceCount, sources };
    } catch (error) {
      // Log the error and a truncated version of the problematic data for easier debugging.
      const truncatedData = data.length > 200 ? data.substring(0, 200) + "..." : data;
      console.error('Error parsing SSE data. Raw data (truncated): "', truncatedData, '". Error details:', error);
      return { textParts: [], agent: '', finalReportWithCitations: undefined, functionCall: null, functionResponse: null, sourceCount: 0, sources: null };
    }
  };

  // Define getEventTitle here or ensure it's in scope from where it's used
  const getEventTitle = (agentName: string): string => {
    switch (agentName) {
      case "plan_generator":
        return "Planning Research Strategy";
      case "section_planner":
        return "Structuring Report Outline";
      case "section_researcher":
        return "Initial Web Research";
      case "research_evaluator":
        return "Evaluating Research Quality";
      case "EscalationChecker":
        return "Quality Assessment";
      case "enhanced_search_executor":
        return "Enhanced Web Research";
      case "research_pipeline":
        return "Executing Research Pipeline";
      case "iterative_refinement_loop":
        return "Refining Research";
      case "interactive_research_planner_agent":
      case agentName:
        return "Interactive Planning";
      default:
        return `Processing (${agentName || 'Unknown Agent'})`;
    }
  };

  const processSseEventData = useCallback((jsonData: string, aiMessageId: string) => {
    const { textParts, agent, finalReportWithCitations, functionCall, functionResponse, sourceCount, sources } = extractDataFromSSE(jsonData);

    if (sourceCount > 0) {
      console.log('[SSE HANDLER] Updating websiteCount. Current sourceCount:', sourceCount);
      setWebsiteCount(prev => Math.max(prev, sourceCount));
    }

    if (agent && agent !== currentAgentRef.current) {
      currentAgentRef.current = agent;
    }

    if (functionCall) {
      const functionCallTitle = `Function Call: ${functionCall.name}`;
      console.log('[SSE HANDLER] Adding Function Call timeline event:', functionCallTitle);
      setMessageEvents(prev => new Map(prev).set(aiMessageId, [...(prev.get(aiMessageId) || []), {
        title: functionCallTitle,
        data: { type: 'functionCall', name: functionCall.name, args: functionCall.args, id: functionCall.id }
      }]));
    }

    if (functionResponse) {
      const functionResponseTitle = `Function Response: ${functionResponse.name}`;
      console.log('[SSE HANDLER] Adding Function Response timeline event:', functionResponseTitle);
      setMessageEvents(prev => new Map(prev).set(aiMessageId, [...(prev.get(aiMessageId) || []), {
        title: functionResponseTitle,
        data: { type: 'functionResponse', name: functionResponse.name, response: functionResponse.response, id: functionResponse.id }
      }]));
    }

    if (textParts.length > 0 && agent !== "report_composer_with_citations") {
      if (agent !== agentName) {
        const eventTitle = getEventTitle(agent);
        console.log('[SSE HANDLER] Adding Text timeline event for agent:', agent, 'Title:', eventTitle, 'Data:', textParts.join(" "));
        setMessageEvents(prev => new Map(prev).set(aiMessageId, [...(prev.get(aiMessageId) || []), {
          title: eventTitle,
          data: { type: 'text', content: textParts.join(" ") }
        }]));
      } else { // Main agent text updates the main AI message
        for (const text of textParts) {
          accumulatedTextRef.current += text + " ";
          setMessages(prev => prev.map(msg =>
            msg.id === aiMessageId ? { ...msg, content: accumulatedTextRef.current.trim(), agent: currentAgentRef.current || msg.agent } : msg
          ));
          setDisplayData(accumulatedTextRef.current.trim());
        }
      }
    }

    if (sources) {
      console.log('[SSE HANDLER] Adding Retrieved Sources timeline event:', sources);
      setMessageEvents(prev => new Map(prev).set(aiMessageId, [...(prev.get(aiMessageId) || []), {
        title: "Retrieved Sources", data: { type: 'sources', content: sources }
      }]));
    }

    if (agent === "report_composer_with_citations" && finalReportWithCitations) {
      const finalReportMessageId = Date.now().toString() + "_final";
      setMessages(prev => [...prev, { type: "ai", content: finalReportWithCitations as string, id: finalReportMessageId, agent: currentAgentRef.current, finalReportWithCitations: true }]);
      setDisplayData(finalReportWithCitations as string);
    }
  }, [agentName]);

  const handleSubmit = useCallback(async (query: string, images?: File[]) => {
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      // Create session if it doesn't exist
      let currentUserId = userId;
      let currentSessionId = sessionId;
      let currentAppName = appName;

      if (!currentSessionId || !currentUserId || !currentAppName) {
        console.log('Creating new session...');
        const sessionData = await retryWithBackoff(createSession) as { userId: string; sessionId: string; appName: string };
        currentUserId = sessionData.userId;
        currentSessionId = sessionData.sessionId;
        currentAppName = sessionData.appName;

        setUserId(currentUserId);
        setSessionId(currentSessionId);
        setAppName(currentAppName);
        console.log('Session created successfully:', { currentUserId, currentSessionId, currentAppName });
      }

      // Add user message to chat
      const userMessageId = Date.now().toString();
      setMessages(prev => [...prev, { type: "human", content: query, id: userMessageId }]);

      // Create AI message placeholder
      const aiMessageId = Date.now().toString() + "_ai";
      currentAgentRef.current = ''; // Reset current agent
      accumulatedTextRef.current = ''; // Reset accumulated text

      setMessages(prev => [...prev, {
        type: "ai",
        content: "",
        id: aiMessageId,
        agent: '',
      }]);

      // Prepare message parts (images first, then text)
      const parts: any[] = [];
      if (images && images.length > 0) {
        const fileToBase64 = async (file: File): Promise<string> => {
          const buffer = await file.arrayBuffer();
          let binary = '';
          const bytes = new Uint8Array(buffer);
          const chunkSize = 0x8000;
          for (let i = 0; i < bytes.length; i += chunkSize) {
            const chunk = bytes.subarray(i, i + chunkSize);
            binary += String.fromCharCode.apply(null, Array.from(chunk) as unknown as number[]);
          }
          return btoa(binary);
        };

        const encodedImages = await Promise.all(images.map(async (img) => ({
          inline_data: {
            data: await fileToBase64(img),
            mime_type: img.type,
          }
        })));
        parts.push(...encodedImages);
      }
      parts.push({ text: query });

      // Send the message with retry logic
      const sendMessage = async () => {
        const response = await fetch("/api/run_sse", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            appName: currentAppName,
            userId: currentUserId,
            sessionId: currentSessionId,
            newMessage: {
              parts,
              role: "user"
            },
            streaming: false
          }),
        });

        if (!response.ok) {
          throw new Error(`Failed to send message: ${response.status} ${response.statusText}`);
        }

        return response;
      };

      const response = await retryWithBackoff(sendMessage) as Response;

      // Handle SSE streaming
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let lineBuffer = "";
      let eventDataBuffer = "";

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();

          if (value) {
            lineBuffer += decoder.decode(value, { stream: true });
          }

          let eolIndex;
          // Process all complete lines in the buffer, or the remaining buffer if 'done'
          while ((eolIndex = lineBuffer.indexOf('\n')) >= 0 || (done && lineBuffer.length > 0)) {
            let line: string;
            if (eolIndex >= 0) {
              line = lineBuffer.substring(0, eolIndex);
              lineBuffer = lineBuffer.substring(eolIndex + 1);
            } else { // Only if done and lineBuffer has content without a trailing newline
              line = lineBuffer;
              lineBuffer = "";
            }

            if (line.trim() === "") { // Empty line: dispatch event
              if (eventDataBuffer.length > 0) {
                // Remove trailing newline before parsing
                const jsonDataToParse = eventDataBuffer.endsWith('\n') ? eventDataBuffer.slice(0, -1) : eventDataBuffer;
                console.log('[SSE DISPATCH EVENT]:', jsonDataToParse.substring(0, 200) + "..."); // DEBUG
                processSseEventData(jsonDataToParse, aiMessageId);
                eventDataBuffer = ""; // Reset for next event
              }
            } else if (line.startsWith('data:')) {
              eventDataBuffer += line.substring(5).trimStart() + '\n'; // Add newline as per spec for multi-line data
            } else if (line.startsWith(':')) {
              // Comment line, ignore
            } // Other SSE fields (event, id, retry) can be handled here if needed
          }

          if (done) {
            // If the loop exited due to 'done', and there's still data in eventDataBuffer
            // (e.g., stream ended after data lines but before an empty line delimiter)
            if (eventDataBuffer.length > 0) {
              const jsonDataToParse = eventDataBuffer.endsWith('\n') ? eventDataBuffer.slice(0, -1) : eventDataBuffer;
              console.log('[SSE DISPATCH FINAL EVENT]:', jsonDataToParse.substring(0, 200) + "..."); // DEBUG
              processSseEventData(jsonDataToParse, aiMessageId);
              eventDataBuffer = ""; // Clear buffer
            }
            break; // Exit the while(true) loop
          }
        }
      }

      currentAgentRef.current = '';
      setIsLoading(false);

    } catch (error) {
      console.error("Error:", error);
      // Update the AI message placeholder with an error message
      const aiMessageId = Date.now().toString() + "_ai_error";
      setMessages(prev => [...prev, {
        type: "ai",
        content: `Sorry, there was an error processing your request: ${error instanceof Error ? error.message : 'Unknown error'}`,
        id: aiMessageId
      }]);
      setIsLoading(false);
    }
  }, [userId, sessionId, appName, createSession, processSseEventData]);

  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector(
        "[data-radix-scroll-area-viewport]"
      );
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight;
      }
    }
  }, [messages]);

  useEffect(() => {
    const checkBackend = async () => {
      setIsCheckingBackend(true);

      // Check if backend is ready with retry logic
      const maxAttempts = 60; // 2 minutes with 2-second intervals
      let attempts = 0;

      while (attempts < maxAttempts) {
        const isReady = await checkBackendHealth();
        if (isReady) {
          setIsBackendReady(true);
          setIsCheckingBackend(false);
          return;
        }

        attempts++;
        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds between checks
      }

      // If we get here, backend didn't come up in time
      setIsCheckingBackend(false);
      console.error("Backend failed to start within 2 minutes");
    };

    checkBackend();
  }, []);

  const handleCancel = useCallback(() => {
    setMessages([]);
    setDisplayData(null);
    setMessageEvents(new Map());
    setWebsiteCount(0);
    window.location.reload();
  }, []);



  const BackendLoadingScreen = () => (
    <div className="flex-1 flex flex-col items-center justify-center p-4 overflow-hidden relative">
      <div className="w-full max-w-2xl z-10 bg-white/15 backdrop-blur-lg p-8 rounded-2xl border border-white/30 shadow-2xl animate-glow-pulse">

        <div className="text-center space-y-6">
          <h1 className="text-4xl font-bold flex items-center justify-center gap-3">
            <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent animate-gradient-flow" style={{ backgroundSize: '200% 200%' }}>
              GTMForge
            </span>
          </h1>

          <div className="flex flex-col items-center space-y-4">

            <div className="relative">
              <div className="w-16 h-16 border-4 border-transparent border-t-purple-500 border-r-pink-500 rounded-full animate-spin"></div>
              <div className="absolute inset-0 w-16 h-16 border-4 border-transparent border-b-blue-500 border-l-orange-400 rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
            </div>

            <div className="space-y-2">
              <p className="text-xl text-gray-700 font-semibold">
                Initializing strategic systems...
              </p>
              <p className="text-sm text-gray-600">
                This may take a moment on first startup
              </p>
            </div>

            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce shadow-lg" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce shadow-lg" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-pink-500 rounded-full animate-bounce shadow-lg" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-background text-foreground font-sans antialiased dark relative overflow-hidden">
      <main className="flex-1 flex flex-col overflow-hidden w-full relative z-10">
        <div className={`flex-1 overflow-y-auto ${(messages.length === 0 || isCheckingBackend) ? "flex" : ""}`}>
          {isCheckingBackend ? (
            <BackendLoadingScreen />
          ) : !isBackendReady ? (
            <div className="flex-1 flex flex-col items-center justify-center p-4">
              <div className="w-full max-w-md bg-white/15 backdrop-blur-lg p-8 rounded-2xl border border-white/30 shadow-2xl text-center space-y-4">
                <h2 className="text-2xl font-bold text-gray-800">
                  Hit a creative roadblock. Let's pivot this idea and try again 🔄
                </h2>
                <p className="text-gray-600">
                  Can't reach the backend right now. Let's try again?
                </p>
                <button
                  onClick={() => window.location.reload()}
                  className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
                >
                  Retry
                </button>
              </div>
            </div>
          ) : messages.length === 0 ? (
            <PageTransition isActive={messages.length === 0}>
              <WelcomeScreen
                handleSubmit={handleSubmit}
                isLoading={isLoading}
                onCancel={handleCancel}
              />
            </PageTransition>
          ) : showChat ? (
            <PageTransition isActive={showChat}>
              <ChatMessagesView
                messages={messages}
                isLoading={isLoading}
                scrollAreaRef={scrollAreaRef}
                onSubmit={handleSubmit}
                onCancel={handleCancel}
                displayData={displayData}
                messageEvents={messageEvents}
                websiteCount={websiteCount}
                agentName={agentName}
              />
            </PageTransition>
          ) : (
            <PageTransition isActive={messages.length > 0}>
              <ProgressDashboard
                currentAgent={currentAgentRef.current}
                messages={messages}
                isLoading={isLoading}
                onCancel={handleCancel}
                sessionId={sessionId || undefined}
                onComplete={() => setShowChat(true)}
              />
            </PageTransition>
          )}
        </div>
      </main>
    </div>
  );
}

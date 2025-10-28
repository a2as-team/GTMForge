import type React from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Copy, CopyCheck } from "lucide-react";
import { InputForm } from "@/components/InputForm";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import ReactMarkdown, { Components } from "react-markdown";
import remarkGfm from 'remark-gfm';
import { cn } from "@/utils";
import { Badge } from "@/components/ui/badge";
import { ActivityTimeline } from "@/components/ActivityTimeline";
import DualVerticalGalleries from "@/components/animations/DualVerticalGalleries";

interface ProcessedEvent {
  title: string;
  data: Record<string, unknown>;
}

// Markdown components (from former ReportView.tsx)
const mdComponents: Partial<Components> = {
  h1: ({ className, children, ...props }) => (
    <h1 className={cn("text-2xl font-bold mt-4 mb-2", className)} {...props}>
      {children}
    </h1>
  ),
  h2: ({ className, children, ...props }) => (
    <h2 className={cn("text-xl font-bold mt-3 mb-2", className)} {...props}>
      {children}
    </h2>
  ),
  h3: ({ className, children, ...props }) => (
    <h3 className={cn("text-lg font-bold mt-3 mb-1", className)} {...props}>
      {children}
    </h3>
  ),
  p: ({ className, children, ...props }) => (
    <p className={cn("mb-3 leading-7", className)} {...props}>
      {children}
    </p>
  ),
  a: ({ className, children, href, ...props }) => (
    <Badge className="text-xs mx-0.5">
      <a
        className={cn("text-blue-400 hover:text-blue-300 text-xs", className)}
        href={href as string}
        target="_blank"
        rel="noopener noreferrer"
        {...props}
      >
        {children}
      </a>
    </Badge>
  ),
  ul: ({ className, children, ...props }) => (
    <ul className={cn("list-disc pl-6 mb-3", className)} {...props}>
      {children}
    </ul>
  ),
  ol: ({ className, children, ...props }) => (
    <ol className={cn("list-decimal pl-6 mb-3", className)} {...props}>
      {children}
    </ol>
  ),
  li: ({ className, children, ...props }) => (
    <li className={cn("mb-1", className)} {...props}>
      {children}
    </li>
  ),
  blockquote: ({ className, children, ...props }) => (
    <blockquote
      className={cn(
        "border-l-4 border-neutral-600 pl-4 italic my-3 text-sm",
        className
      )}
      {...props}
    >
      {children}
    </blockquote>
  ),
  code: ({ className, children, ...props }) => (
    <code
      className={cn(
        "bg-neutral-900 rounded px-1 py-0.5 font-mono text-xs",
        className
      )}
      {...props}
    >
      {children}
    </code>
  ),
  pre: ({ className, children, ...props }) => (
    <pre
      className={cn(
        "bg-neutral-900 p-3 rounded-lg overflow-x-auto font-mono text-xs my-3",
        className
      )}
      {...props}
    >
      {children}
    </pre>
  ),
  hr: ({ className, ...props }) => (
    <hr className={cn("border-neutral-600 my-4", className)} {...props} />
  ),
  table: ({ className, children, ...props }) => (
    <div className="my-3 overflow-x-auto">
      <table className={cn("border-collapse w-full", className)} {...props}>
        {children}
      </table>
    </div>
  ),
  th: ({ className, children, ...props }) => (
    <th
      className={cn(
        "border border-neutral-600 px-3 py-2 text-left font-bold",
        className
      )}
      {...props}
    >
      {children}
    </th>
  ),
  td: ({ className, children, ...props }) => (
    <td
      className={cn("border border-neutral-600 px-3 py-2", className)}
      {...props}
    >
      {children}
    </td>
  ),
};

// Props for HumanMessageBubble
interface HumanMessageBubbleProps {
  message: { content: string; id: string };
  mdComponents: typeof mdComponents;
}

// HumanMessageBubble Component
const HumanMessageBubble: React.FC<HumanMessageBubbleProps> = ({
  message,
  mdComponents,
}) => {
  return (
    <div className="rounded-2xl break-words max-w-[85%] lg:max-w-[70%] px-4 py-2.5 bg-gradient-to-br from-orange-400/20 to-pink-500/20 border-white/30 shadow-lg hover:shadow-xl transition-all duration-300">
      <div className="prose prose-sm max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
        <ReactMarkdown components={mdComponents} remarkPlugins={[remarkGfm]}>
          {message.content}
        </ReactMarkdown>
      </div>
    </div>
  );
};

// Props for AiMessageBubble
interface AiMessageBubbleProps {
  message: { content: string; id: string };
  mdComponents: typeof mdComponents;
  handleCopy: (text: string, messageId: string) => void;
  copiedMessageId: string | null;
  agent?: string;
  finalReportWithCitations?: boolean;
  processedEvents: ProcessedEvent[];
  websiteCount: number;
  isLoading: boolean;
  agentName: string;
}

// AiMessageBubble Component
const AiMessageBubble: React.FC<AiMessageBubbleProps> = ({
  message,
  mdComponents,
  handleCopy,
  copiedMessageId,
  agent,
  finalReportWithCitations,
  processedEvents,
  websiteCount,
  isLoading,
  agentName,
}) => {
  // Show ActivityTimeline if we have processedEvents (this will be the first AI message)
  const shouldShowTimeline = processedEvents.length > 0;
  
  // Condition for DIRECT DISPLAY (main agent OR final report)
  const shouldDisplayDirectly = 
    agent === agentName || 
    (agent === "report_composer_with_citations" && finalReportWithCitations);
  
  // Show loading animation when message is loading and has no content
  const isMessageLoading = isLoading && (!message.content || message.content.trim().length === 0);
  const hasContent = message.content && message.content.trim().length > 0;
  
  if (shouldDisplayDirectly) {
    // Direct display - show content with copy button, and timeline if available
    return (
      <div className="relative break-words flex flex-col w-full">
        {/* Show timeline for main agent if available */}
        {shouldShowTimeline && agent === agentName && (
          <div className="w-full mb-2">
            <ActivityTimeline 
              processedEvents={processedEvents}
              isLoading={isLoading}
              websiteCount={websiteCount}
            />
          </div>
        )}

        {isMessageLoading && (
          <div className="rounded-2xl break-words max-w-[85%] lg:max-w-[70%] px-4 py-2.5 border border-white/30 shadow-lg">
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <span className="text-sm text-gray-600">GTMForge is thinking...</span>
            </div>
          </div>
        )}

        {hasContent && !isMessageLoading && (
        <div 
          className="rounded-2xl break-words max-w-[85%] lg:max-w-[70%] px-4 py-2.5 border border-white/30 shadow-lg transition-all duration-500 ease-out"
          style={{
            animation: 'fadeInUp 0.5s ease-out',
          }}
        >
          <div className="flex items-start gap-3">
            <div className="flex-1 prose prose-sm max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
              <ReactMarkdown components={mdComponents} remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
            <button
              onClick={() => handleCopy(message.content, message.id)}
              className="p-1 hover:bg-white/20 rounded flex-shrink-0"
            >
              {copiedMessageId === message.id ? (
                <CopyCheck className="h-4 w-4 text-green-500" />
              ) : (
                <Copy className="h-4 w-4 text-gray-600" />
              )}
            </button>
          </div>
        </div>
        )}
      </div>
    );
  } else if (shouldShowTimeline) {
    // First AI message with timeline only (no direct content display)
    return (
      <div className="relative break-words flex flex-col w-full">
        <div className="w-full">
          <ActivityTimeline 
            processedEvents={processedEvents}
            isLoading={isLoading}
            websiteCount={websiteCount}
          />
        </div>
        {isMessageLoading && (
          <div className="rounded-2xl break-words max-w-[85%] lg:max-w-[70%] px-4 py-2.5 border border-white/30 shadow-lg mt-2">
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <span className="text-sm text-gray-600">GTMForge is thinking...</span>
            </div>
          </div>
        )}

        {message.content && message.content.trim() && agent !== agentName && !isMessageLoading && (
          <div className="rounded-2xl break-words max-w-[85%] lg:max-w-[70%] px-4 py-2.5 border border-white/30 shadow-lg mt-2">
            <div className="flex items-start gap-3">
              <div className="flex-1 prose prose-sm max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
                <ReactMarkdown components={mdComponents} remarkPlugins={[remarkGfm]}>
                  {message.content}
                </ReactMarkdown>
              </div>
              <button
                onClick={() => handleCopy(message.content, message.id)}
                className="p-1 hover:bg-white/20 rounded flex-shrink-0"
              >
                {copiedMessageId === message.id ? (
                  <CopyCheck className="h-4 w-4 text-green-500" />
                ) : (
                  <Copy className="h-4 w-4 text-gray-600" />
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    );
  } else {
    // Fallback for other messages - just show content
    return (
      <div className="relative break-words flex flex-col w-full">
        {isMessageLoading && (
          <div className="rounded-2xl break-words max-w-[85%] lg:max-w-[70%] px-4 py-2.5 border border-white/30 shadow-lg">
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <span className="text-sm text-gray-600">GTMForge is thinking...</span>
            </div>
          </div>
        )}

        {!isMessageLoading && message.content && (
          <div className="rounded-2xl break-words max-w-[85%] lg:max-w-[70%] px-4 py-2.5">
            <div className="flex items-start gap-3">
              <div className="flex-1 prose prose-sm max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
                <ReactMarkdown components={mdComponents} remarkPlugins={[remarkGfm]}>
                  {message.content}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }
};

interface ChatMessagesViewProps {
  messages: { type: "human" | "ai"; content: string; id: string; agent?: string; finalReportWithCitations?: boolean }[];
  isLoading: boolean;
  scrollAreaRef: React.RefObject<HTMLDivElement | null>;
  onSubmit: (query: string, images?: File[]) => void;
  onCancel: () => void;
  displayData: string | null;
  messageEvents: Map<string, ProcessedEvent[]>;
  websiteCount: number;
  agentName: string;
}

export function ChatMessagesView({
  messages,
  isLoading,
  scrollAreaRef,
  onSubmit,
  onCancel,
  messageEvents,
  websiteCount,
  agentName,
}: ChatMessagesViewProps) {
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);

  const handleCopy = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error("Failed to copy text:", err);
    }
  };

  const handleNewChat = () => { 
    window.location.reload();
  };

  const lastAiMessage = messages.slice().reverse().find(m => m.type === "ai");
  const lastAiMessageId = lastAiMessage?.id;

  return (
    <div className="flex flex-col h-full w-full relative animate-fadeIn" style={{ animationDuration: '1.5s' }}>

      <DualVerticalGalleries />

      <div className="p-4 shadow-lg mt-4 max-w-4xl mx-auto rounded-xl">
        <div className="flex gap-128 items-center justify-between px-5">
          <h1 className="text-lg font-semibold text-gray-800">
            <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Chat
            </span>
          </h1>

          <Button onClick={handleNewChat} variant="outline">
            New Chat
          </Button>
        </div>
      </div>


      <div className="flex-1 flex flex-col w-full">
        <ScrollArea ref={scrollAreaRef} className="flex-1 w-full">
          <div className="p-4 md:p-6 space-y-3 w-full max-w-5xl mx-auto">
            {messages.map((message) => { // Removed index as it's not directly used for this logic
              const eventsForMessage = message.type === "ai" ? (messageEvents.get(message.id) || []) : [];
              
              // Determine if the current AI message is the last one
              const isCurrentMessageTheLastAiMessage = message.type === "ai" && message.id === lastAiMessageId;

              return (
                <div
                  key={message.id}
                  className={`flex w-full ${message.type === "human" ? "justify-end" : "justify-start"}`}
                >
                  {message.type === "human" ? (
                    <HumanMessageBubble
                      message={message}
                      mdComponents={mdComponents}
                    />
                  ) : (
                    <AiMessageBubble
                      message={message}
                      mdComponents={mdComponents}
                      handleCopy={handleCopy}
                      copiedMessageId={copiedMessageId}
                      agent={message.agent}
                      finalReportWithCitations={message.finalReportWithCitations}
                      processedEvents={eventsForMessage}
                      // MODIFIED: Pass websiteCount only if it's the last AI message
                      websiteCount={isCurrentMessageTheLastAiMessage ? websiteCount : 0}
                      // MODIFIED: Pass isLoading only if it's the last AI message and global isLoading is true
                      isLoading={isCurrentMessageTheLastAiMessage && isLoading}
                      agentName={agentName}
                    />
                  )}
                </div>
              );
            })}
            {/* Loading animation for new AI messages */}
            {isLoading && messages.length > 0 && messages[messages.length -1].type === 'human' && (
              <div className="flex justify-start w-full">
                <div className="rounded-full px-4 py-2.5 bg-gradient-to-br from-blue-400/20 to-purple-500/20 border border-white/30 shadow-lg inline-flex">
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                      <div className="w-2 h-2 bg-pink-500 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                    </div>
                    <span className="text-sm text-gray-700">GTMForge is analyzing...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </div>
      <div className="p-4 w-full 10 shadow-lg">
        <div className="max-w-3xl mx-auto">
          <InputForm onSubmit={onSubmit} isLoading={isLoading} context="chat" />
          {isLoading && (
            <div className="mt-4 flex justify-center">
              <Button
                variant="outline"
                onClick={onCancel}
                className="text-red-600 hover:text-red-700"
              >
                Cancel
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
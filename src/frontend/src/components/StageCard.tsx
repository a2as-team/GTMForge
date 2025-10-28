import { cn } from "@/utils";
import { GlassCard } from "@/components/ui/glass-card";
import { ProgressBar } from "./ProgressBar";

export type StageStatus = "pending" | "in-progress" | "complete" | "error";

export interface Artifact {
  type: "report" | "image" | "video" | "document";
  url: string;
  name: string;
  preview?: string;
}

interface StageCardProps {
  stageNumber: number;
  name: string;
  icon: string;
  description: string;
  status: StageStatus;
  artifacts?: Artifact[];
  progress?: number;
  className?: string;
}

export function StageCard({
  stageNumber,
  name,
  icon,
  description,
  status,
  artifacts = [],
  progress = 0,
  className,
}: StageCardProps) {
  const isActive = status === "in-progress";
  const isComplete = status === "complete";
  const hasError = status === "error";
  const isPending = status === "pending";

  return (
    <GlassCard
      variant="liquid"
      className={cn(
        "transition-all duration-500",
        isActive && "ring-2 ring-purple-500 ring-offset-2 shadow-xl shadow-purple-500/20",
        isComplete && "bg-gradient-to-br from-green-50/50 to-blue-50/50",
        hasError && "bg-red-50/50",
        isPending && "opacity-60",
        className
      )}
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-4">
            <div
              className={cn(
                "text-4xl",
                isActive && "animate-bounce",
                isComplete && "scale-110"
              )}
            >
              {icon}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-gray-500">
                  STAGE {stageNumber}
                </span>
                {isComplete && (
                  <span className="text-green-600 text-xl">✓</span>
                )}
                {hasError && (
                  <span className="text-red-600 text-xl">✗</span>
                )}
              </div>
              <h3 className="text-xl font-bold text-gray-900">{name}</h3>
              <p
                className={cn(
                  "text-sm mt-1",
                  isActive ? "text-purple-600 font-medium" : "text-gray-600"
                )}
              >
                {description}
              </p>
            </div>
          </div>
        </div>

        {/* Progress Bar (only show when in progress) */}
        {isActive && (
          <div className="mb-4">
            <ProgressBar progress={progress} showPercentage={true} />
          </div>
        )}

        {/* Artifacts */}
        {artifacts.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">
              Generated Assets
            </h4>
            <div className="grid grid-cols-2 gap-3">
              {artifacts.map((artifact, idx) => (
                <a
                  key={idx}
                  href={artifact.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex items-center gap-2 p-3 bg-white/80 rounded-lg hover:bg-white transition-all border border-gray-200 hover:border-purple-300 hover:shadow-md"
                >
                  <span className="text-2xl">
                    {artifact.type === "report" && "📄"}
                    {artifact.type === "image" && "🎨"}
                    {artifact.type === "video" && "🎬"}
                    {artifact.type === "document" && "📋"}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate group-hover:text-purple-600">
                      {artifact.name}
                    </p>
                    <p className="text-xs text-gray-500">Click to view</p>
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Loading indicator for active stage */}
        {isActive && artifacts.length === 0 && (
          <div className="mt-4 flex items-center gap-3 text-gray-600">
            <div className="flex gap-1">
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
              <div className="w-2 h-2 bg-pink-500 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
            </div>
            <span className="text-sm">Processing...</span>
          </div>
        )}
      </div>
    </GlassCard>
  );
}


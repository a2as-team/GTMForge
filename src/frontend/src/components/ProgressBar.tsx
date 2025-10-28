import { cn } from "@/utils";

interface ProgressBarProps {
  progress: number; // 0-100
  className?: string;
  showPercentage?: boolean;
}

export function ProgressBar({ progress, className, showPercentage = true }: ProgressBarProps) {
  return (
    <div className={cn("w-full", className)}>
      <div className="relative h-3 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="absolute top-0 left-0 h-full bg-gradient-to-r from-purple-600 via-pink-500 to-blue-500 transition-all duration-500 ease-out rounded-full"
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
        >
          <div className="absolute inset-0 bg-white/20 animate-pulse" />
        </div>
      </div>
      {showPercentage && (
        <div className="mt-1 text-xs text-gray-600 text-right">
          {Math.round(progress)}%
        </div>
      )}
    </div>
  );
}


import * as React from "react";
import { cn } from "@/utils";

export interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "hover" | "glow" | "liquid";
  children?: React.ReactNode;
}

const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className, variant = "default", children, ...props }, ref) => {
    const variants = {
      default: "backdrop-blur-md bg-white/10 border border-white/20",
      hover: "backdrop-blur-md bg-white/10 border border-white/20 hover:bg-white/15 hover:border-white/30 hover:shadow-xl hover:shadow-purple-500/10 hover:scale-[1.01] transition-all duration-300",
      glow: "backdrop-blur-lg bg-white/15 border border-white/30 shadow-2xl shadow-purple-500/20 animate-glow-pulse",
      liquid: "backdrop-blur-xl bg-gradient-to-br from-white/20 via-white/10 to-white/20 border border-white/30 shadow-2xl relative overflow-hidden",
    };

    return (
      <div
        ref={ref}
        className={cn(
          "glass-card rounded-2xl p-6",
          variants[variant],
          className
        )}
        {...props}
      >
        {variant === "liquid" && (
          <>
            {/* Animated gradient overlay */}
            <div className="absolute inset-0 opacity-30 animate-gradient-flow" style={{
              background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(147, 51, 234, 0.2) 25%, rgba(236, 72, 153, 0.2) 50%, rgba(251, 146, 60, 0.2) 75%, rgba(59, 130, 246, 0.2) 100%)',
              backgroundSize: '200% 200%'
            }} />
            {/* Shimmer effect */}
            <div className="absolute inset-0 opacity-20">
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent animate-shimmer-slow" style={{
                backgroundSize: '200% 100%'
              }} />
            </div>
          </>
        )}
        <div className="relative z-10">
          {children}
        </div>
      </div>
    );
  }
);

GlassCard.displayName = "GlassCard";

export { GlassCard };


import { StageCard, StageStatus, Artifact } from "./StageCard";
import { ProgressBar } from "./ProgressBar";
import { Button } from "./ui/button";
import { ScrollArea } from "./ui/scroll-area";
import { useEffect, useState } from "react";

interface Stage {
  id: number;
  name: string;
  icon: string;
  description: string;
  agentNames: string[];
}

const STAGES: Stage[] = [
  {
    id: 1,
    name: "Deep Market Research",
    icon: "🔍",
    description: "Analyzing competitive landscape and market opportunities...",
    agentNames: ["express_market_research_wrapper", "plan_generator", "section_researcher", "research_evaluator", "enhanced_search_executor", "report_composer"],
  },
  {
    id: 2,
    name: "Extended Strategy Brief",
    icon: "📋",
    description: "Crafting your go-to-market strategy and positioning...",
    agentNames: ["ideation_agent"],
  },
  {
    id: 3,
    name: " Product Specification",
    icon: "⚙️",
    description: "Defining product requirements and website specs...",
    agentNames: ["website_spec_agent", "prd_agent"],
  },
  {
    id: 4,
    name: "UI Mockups",
    icon: "🎨",
    description: "Generating visual designs and mockups...",
    agentNames: ["mockups_agent", "mockup_prompt_extractor", "mockup_loop_orchestrator"],
  },
  {
    id: 5,
    name: "Promo Video",
    icon: "🎬",
    description: "Creating promotional video content...",
    agentNames: ["video_agent", "video_planner", "video_generation_worker"],
  },
];

interface ProgressDashboardProps {
  currentAgent: string;
  messages: Array<{ type: string; content: string; agent?: string; id: string }>;
  isLoading: boolean;
  onCancel: () => void;
}

export function ProgressDashboard({
  currentAgent,
  messages,
  isLoading,
  onCancel,
}: ProgressDashboardProps) {
  const [stageStatuses, setStageStatuses] = useState<Record<number, StageStatus>>(
    Object.fromEntries(STAGES.map((s) => [s.id, "pending" as StageStatus]))
  );
  const [stageArtifacts, setStageArtifacts] = useState<Record<number, Artifact[]>>(
    Object.fromEntries(STAGES.map((s) => [s.id, []]))
  );
  const [completedStages, setCompletedStages] = useState<Set<number>>(new Set());

  // Determine which stage is currently active
  const getCurrentStage = (agentName: string): number | null => {
    for (const stage of STAGES) {
      if (stage.agentNames.some((name) => agentName.includes(name))) {
        return stage.id;
      }
    }
    return null;
  };

  // Update stage statuses based on current agent
  useEffect(() => {
    if (!currentAgent && !isLoading) {
      // All done
      const newStatuses = { ...stageStatuses };
      STAGES.forEach((stage) => {
        if (newStatuses[stage.id] === "in-progress") {
          newStatuses[stage.id] = "complete";
        }
      });
      setStageStatuses(newStatuses);
      return;
    }

    if (currentAgent) {
      const activeStageId = getCurrentStage(currentAgent);
      if (activeStageId) {
        const newStatuses = { ...stageStatuses };
        
        // Mark previous stages as complete
        for (let i = 1; i < activeStageId; i++) {
          if (newStatuses[i] !== "complete") {
            newStatuses[i] = "complete";
            setCompletedStages((prev) => new Set([...prev, i]));
          }
        }
        
        // Mark current stage as in-progress
        newStatuses[activeStageId] = "in-progress";
        
        // Keep future stages as pending
        for (let i = activeStageId + 1; i <= STAGES.length; i++) {
          if (newStatuses[i] === "pending") {
            newStatuses[i] = "pending";
          }
        }
        
        setStageStatuses(newStatuses);
      }
    }
  }, [currentAgent, isLoading]);

  // Extract artifacts from messages
  useEffect(() => {
    const newArtifacts: Record<number, Artifact[]> = Object.fromEntries(
      STAGES.map((s) => [s.id, []])
    );

    messages.forEach((msg) => {
      if (msg.type === "ai" && msg.content) {
        // Look for asset URLs in message content
        const urlRegex = /http:\/\/localhost:8550\/[^\s)]+/g;
        const urls = msg.content.match(urlRegex) || [];
        
        urls.forEach((url) => {
          let artifactType: Artifact["type"] = "document";
          let artifactName = "Asset"; 
          let stageId = 1;

          // Determine artifact type and stage from URL
          if (url.includes("/reports/")) {
            artifactType = "report";
            artifactName = "Research Report";
            stageId = 1;
          } else if (url.includes("/briefs/")) {
            artifactType = "document";
            artifactName = "GTM Brief";
            stageId = 2;
          } else if (url.includes("/website_specs/")) {
            artifactType = "document";
            artifactName = "Website Spec";
            stageId = 3;
          } else if (url.includes("/prds/")) {
            artifactType = "document";
            artifactName = "Product Requirements";
            stageId = 3;
          } else if (url.includes("/mockups/")) {
            artifactType = "image";
            artifactName = url.split("/").pop() || "Mockup";
            stageId = 4;
          } else if (url.includes("/videos/")) {
            artifactType = "video";
            artifactName = "Promo Video";
            stageId = 5;
          }

          // Add artifact if not already present
          if (!newArtifacts[stageId].some((a) => a.url === url)) {
            newArtifacts[stageId].push({
              type: artifactType,
              url: url,
              name: artifactName,
            });
          }
        });
      }
    });

    setStageArtifacts(newArtifacts);
  }, [messages]);

  // Calculate overall progress
  const overallProgress = (() => {
    let completed = 0;
    STAGES.forEach((stage) => {
      if (stageStatuses[stage.id] === "complete") completed++;
      else if (stageStatuses[stage.id] === "in-progress") completed += 0.5;
    });
    return (completed / STAGES.length) * 100;
  })();

  const estimatedTimeRemaining = (() => {
    const completedCount = Array.from(completedStages).length;
    const remaining = STAGES.length - completedCount;
    const avgTimePerStage = 2; // minutes
    return remaining * avgTimePerStage;
  })();

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 animate-fadeIn" style={{ animationDuration: "1.5s" }}>
      {/* Header */}
      <div className="p-6 bg-white/80 backdrop-blur-lg border-b border-gray-200 shadow-sm">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-black mb-2">
            <span className="text-gray-900">GTM</span>
            <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Forge
            </span>
          </h1>
          <p className="text-gray-600 mb-4">
            Building your startup assets...
          </p>
          
          {/* Overall Progress */}
          <ProgressBar progress={overallProgress} className="mb-2" />
          
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>
              {Array.from(completedStages).length} of {STAGES.length} stages complete
            </span>
            {isLoading && estimatedTimeRemaining > 0 && (
              <span>~{estimatedTimeRemaining} minutes remaining</span>
            )}
          </div>
        </div>
      </div>

      {/* Stages */}
      <ScrollArea className="flex-1">
        <div className="p-6 max-w-6xl mx-auto space-y-4">
          {STAGES.map((stage) => (
            <StageCard
              key={stage.id}
              stageNumber={stage.id}
              name={stage.name}
              icon={stage.icon}
              description={stage.description}
              status={stageStatuses[stage.id]}
              artifacts={stageArtifacts[stage.id]}
              progress={stageStatuses[stage.id] === "in-progress" ? 50 : 0}
            />
          ))}
        </div>
      </ScrollArea>

      {/* Footer */}
      {isLoading && (
        <div className="p-4 bg-white/80 backdrop-blur-lg border-t border-gray-200 shadow-sm">
          <div className="max-w-6xl mx-auto flex justify-center">
            <Button
              variant="outline"
              onClick={onCancel}
              className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-300"
            >
              Cancel Build
            </Button>
          </div>
        </div>
      )}

      {/* Completion Message */}
      {!isLoading && overallProgress === 100 && (
        <div className="p-6 bg-gradient-to-r from-purple-600 to-pink-600 text-white">
          <div className="max-w-6xl mx-auto text-center">
            <h2 className="text-2xl font-bold mb-2">🎉 Your Startup Assets are Ready!</h2>
            <p className="text-purple-100">
              All assets have been generated. Scroll up to view and download your files.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}


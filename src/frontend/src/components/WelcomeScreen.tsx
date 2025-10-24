import { Button } from "@/components/ui/button";
import { InputForm } from "@/components/InputForm";
import { GlassCard } from "@/components/ui/glass-card";
import DualVerticalGalleries from "@/components/animations/DualVerticalGalleries";
import FadeContent from "@/components/animations/FadeContent";

interface WelcomeScreenProps {
  handleSubmit: (query: string) => void;
  isLoading: boolean;
  onCancel: () => void;
}

export function WelcomeScreen({
  handleSubmit,
  isLoading,
  onCancel,
}: WelcomeScreenProps) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 overflow-hidden relative">

      <div className="absolute inset-0 z-0 pointer-events-none">
        <DualVerticalGalleries />
      </div>

      <FadeContent delay={200} duration={800}>
        <GlassCard 
        variant="liquid" 
        className="w-full max-w-2xl z-20 p-8 animate-float-slow shadow-2xl relative"
        style={{
          boxShadow: '0 20px 60px rgba(147, 51, 234, 0.2), 0 0 60px rgba(236, 72, 153, 0.15), 0 0 100px rgba(59, 130, 246, 0.1)',
        }}
      >
        <div className="flex flex-col justify-center items-center h-full text-center space-y-6">
          <h1 className="text-5xl font-bold items-center justify-center gap-3 relative">
            <span 
              className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent animate-gradient-flow"
              style={{
                backgroundSize: '200% 200%',
              }}
            >
              GTMForge
            </span>
          </h1>
          <p className="text-lg text-gray-700 max-w-md mx-auto font-medium">
            Your startup accelerator and GTM mentor. What's your GTM idea? Let's forge something amazing!
          </p>
        </div>
        <div className="mt-8">
          <InputForm onSubmit={handleSubmit} isLoading={isLoading} context="homepage" />
          {isLoading && (
            <div className="mt-4 flex justify-center">
              <Button
                variant="outline"
                onClick={onCancel}
                className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-300"
              >
                Cancel
              </Button>
            </div>
          )}
        </div>
      </GlassCard>
      </FadeContent>
    </div>
  );
}
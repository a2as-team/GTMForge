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


interface BackgroundImage {
  src: string;
  top?: string;
  bottom?: string;
  left?: string;
  right?: string;
  rotate: number;
  scale: number;
  delay: number;
}

const backgroundImages: BackgroundImage[] = [
  { src: "/images/relay.jpg", top: "8%", left: "15%", rotate: -15, scale: 1, delay: 0 },
  { src: "/images/atlaspitch.jpg", top: "10%", right: "18%", rotate: 10, scale: 1, delay: 0.5 },
  { src: "/images/composer.jpg", top: "15%", left: "10%", rotate: 18, scale: 1, delay: 1 },
  { src: "/images/ixmyride.jpg", top: "13%", left: "75%", rotate: -10, scale: 1, delay: 3 },
  { src: "/images/knightmentor.jpg", top: "16%", right: "10%", rotate: 15, scale: 1, delay: 3.5 },
  { src: "/images/ecotracker.jpg", top: "22%", left: "80%", rotate: -8, scale: 1, delay: 4 },
  { src: "/images/greenleaf.jpg", top: "11%", left: "65%", rotate: 12, scale: 1, delay: 4.5 },
  { src: "/images/musemap.jpg", top: "19%", right: "12%", rotate: -18, scale: 1, delay: 5 },
  { src: "/images/queuequest.jpg", top: "24%", left: "70%", rotate: 8, scale: 1, delay: 5.5 },
  { src: "/images/knighthacks.jpeg", top: "14%", right: "25%", rotate: -15, scale: 1, delay: 6 },
  { src: "/images/onboardOS.jpg", top: "17%", left: "60%", rotate: 20, scale: 1, delay: 6.5 },
  { src: "/images/ixmyride.jpg", top: "50%", left: "12%", rotate: 18, scale: 1, delay: 10.5 },
  { src: "/images/knightmentor.jpg", top: "55%", left: "8%", rotate: -15, scale: 1, delay: 11 },
  { src: "/images/ecotracker.jpg", top: "60%", left: "14%", rotate: 10, scale: 1, delay: 11.5 },
  { src: "/images/greenleaf.jpg", top: "65%", left: "6%", rotate: -18, scale: 1, delay: 12 },
  { src: "/images/musemap.jpg", top: "70%", left: "10%", rotate: 22, scale: 1, delay: 12.5 },
  { src: "/images/queuequest.jpg", top: "75%", left: "15%", rotate: -10, scale: 1, delay: 13 },
  { src: "/images/knighthacks.jpeg", top: "80%", left: "8%", rotate: 16, scale: 1, delay: 13.5 },
  { src: "/images/ledgerless.jpg", top: "45%", right: "8%", rotate: -20, scale: 1, delay: 16 },
  { src: "/images/shadowhire.jpg", top: "50%", right: "15%", rotate: 12, scale: 1, delay: 16.5 },
  { src: "/images/pawporter.jpg", top: "55%", right: "6%", rotate: -12, scale: 1, delay: 17 },
  { src: "/images/ixmyride.jpg", top: "60%", right: "10%", rotate: 18, scale: 1, delay: 17.5 },
  { src: "/images/knightmentor.jpg", top: "65%", right: "12%", rotate: -15, scale: 1, delay: 18 },
  { src: "/images/ecotracker.jpg", top: "70%", right: "8%", rotate: 10, scale: 1, delay: 18.5 },
  { src: "/images/greenleaf.jpg", top: "75%", right: "10%", rotate: -18, scale: 1, delay: 19 },
  { src: "/images/musemap.jpg", top: "80%", right: "6%", rotate: 22, scale: 1, delay: 19.5 },
  { src: "/images/queuequest.jpg", top: "82%", left: "15%", rotate: -10, scale: 1, delay: 20 },
  { src: "/images/pawporter.jpg", top: "83%", left: "60%", rotate: -12, scale: 1, delay: 24 },
  { src: "/images/ixmyride.jpg", top: "85%", right: "25%", rotate: 18, scale: 1, delay: 24.5 },
  { src: "/images/knightmentor.jpg", top: "87%", left: "50%", rotate: -15, scale: 1, delay: 25 },
  { src: "/images/ecotracker.jpg", top: "89%", right: "30%", rotate: 10, scale: 1, delay: 25.5 },
];

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

      <div className="absolute inset-0 z-[-5] pointer-events-none">
        {backgroundImages.map((img, idx) => (
          <img
            key={idx}
            src={img.src}
            alt=""
            width={128}
            height={128}
            className="absolute w-32 h-32 object-cover rounded-xl opacity-20 grayscale blur-[1px] animate-float-slow"
            style={{
              ...(img.top && { top: img.top }),
              ...(img.bottom && { bottom: img.bottom }),
              ...(img.left && { left: img.left }),
              ...(img.right && { right: img.right }),
              transform: `rotate(${img.rotate}deg) scale(${img.scale})`,
              animationDelay: `${img.delay}s`,
              animationDuration: `${4 + (idx % 3)}s`,
              imageRendering: 'auto',
              backfaceVisibility: 'hidden',
            }}
            loading="eager"
            decoding="sync"
          />
        ))}
      </div>

      <FadeContent delay={200} duration={800}>
        <GlassCard 
        variant="liquid" 
        className="w-full max-w-2xl z-20 p-10 animate-float-slow shadow-2xl relative bg-white/10 backdrop-blur-lg border border-white/20"
        style={{
          boxShadow: '0 20px 60px rgba(147, 51, 234, 0.2), 0 0 60px rgba(236, 72, 153, 0.15), 0 0 100px rgba(59, 130, 246, 0.1)',
        }}
      >
        <div className="flex flex-col justify-center items-center h-full text-center space-y-8">
          <div className="space-y-4">
            <h1 className="text-6xl font-black tracking-tight">
              <span className="text-gray-900">GTM</span>
              <span className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">Forge</span>
            </h1>
            <div className="w-16 h-1 bg-gradient-to-r from-purple-500 to-pink-500 mx-auto rounded-full"></div>
          </div>
          <div className="space-y-4">
            <h2 className="text-2xl font-bold text-gray-800">
              Build. Launch. Scale.
            </h2>
            <p className="text-lg text-gray-600 max-w-lg mx-auto leading-relaxed">
              Your go-to-market strategy, built for founders who want to move fast and win big.
            </p>
          </div>
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
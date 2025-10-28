import { Button } from "@/components/ui/button";
import { InputForm } from "@/components/InputForm";
import { GlassCard } from "@/components/ui/glass-card";
import DualVerticalGalleries from "@/components/animations/DualVerticalGalleries";

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
  { src: "/images/orbit.jpg",        top: "0%",   left: "12%", rotate: 25,  scale: 0.5,  delay: 7 },
  { src: "/images/ledgerless.jpg",   top: "6%",   right: "14%", rotate: -12, scale: 0.7,  delay: 1.5 },
  { src: "/images/ixmyride.jpg",     top: "12%",  left: "52%", rotate: 18,  scale: 0.7,  delay: 10.5 },
  { src: "/images/relay.jpg",        top: "18%",  right: "12%", rotate: -15, scale: 0.7,  delay: 0 },
  { src: "/images/musemap.jpg",      top: "24%",  left: "58%", rotate: 22,  scale: 0.6,  delay: 12.5 },
  { src: "/images/greenleaf.jpg",    top: "30%",  right: "16%", rotate: 12,  scale: 0.75, delay: 4.5 },
  { src: "/images/composer.jpg",     top: "36%",  left: "18%", rotate: 15,  scale: 0.7,  delay: 8.5 },
  { src: "/images/queuequest.jpg",   top: "42%",  right: "20%", rotate: 8,   scale: 0.7,  delay: 5.5 },
  { src: "/images/pawporter.jpg",    top: "48%",  left: "5%", rotate: -20, scale: 0.6,  delay: 2.5 },
  { src: "/images/ecotracker.jpg",   top: "54%",  right: "15%", rotate: 10,  scale: 0.65, delay: 11.5 },
  { src: "/images/composer.jpg",     top: "60%",  left: "10%", rotate: 18,  scale: 0.75, delay: 1 },
  { src: "/images/queuequest.jpg",   top: "66%",  right: "18%", rotate: -10, scale: 0.75, delay: 13 },
  { src: "/images/onboardOS.jpg",    top: "72%",  left: "5%", rotate: 20,  scale: 0.65, delay: 6.5 },
  { src: "/images/atlaspitch.jpg",   top: "78%",  right: "12%", rotate: 10,  scale: 0.6,  delay: 0.5 },
  { src: "/images/pawporter.jpg",    top: "84%",  left: "16%", rotate: -12, scale: 0.6,  delay: 10 },
  { src: "/images/ixmyride.jpg",     top: "90%",  right: "58%", rotate: -10, scale: 0.65, delay: 3 },
  { src: "/images/greenleaf.jpg",    top: "96%",  left: "20%", rotate: -18, scale: 0.7,  delay: 12 },
  { src: "/images/relay.jpg",        top: "102%", right: "10%", rotate: -25, scale: 0.55, delay: 7.5 },
  { src: "/images/knightmentor.jpg", top: "108%", left: "40%", rotate: 15,  scale: 0.8,  delay: 3.5 },
  { src: "/images/shadowhire.jpg",   top: "114%", right: "14%", rotate: 12,  scale: 0.75, delay: 9.5 },
  { src: "/images/musemap.jpg",      top: "120%", left: "12%", rotate: -18, scale: 0.6,  delay: 5 },
  { src: "/images/shadowhire.jpg",   top: "126%", right: "56%", rotate: 8,   scale: 0.8,  delay: 2 },
  { src: "/images/knighthacks.jpeg", top: "132%", left: "15%", rotate: -15, scale: 0.8,  delay: 6 },
  { src: "/images/knightmentor.jpg", top: "138%", right: "12%", rotate: -15, scale: 0.8,  delay: 11 },
  { src: "/images/ledgerless.jpg",   top: "150%", right: "16%", rotate: -20, scale: 0.65, delay: 9 },
  { src: "/images/ecotracker.jpg",   top: "156%", left: "18%", rotate: -8,  scale: 0.7,  delay: 4 },
  { src: "/images/knighthacks.jpeg", top: "162%", right: "52%", rotate: 16,  scale: 0.65, delay: 13.5 },
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
            className="absolute w-32 h-32 object-cover rounded-xl opacity-20 grayscale blur-[1px]"
            style={{
              ...(img.top && { top: img.top }),
              ...(img.bottom && { bottom: img.bottom }),
              ...(img.left && { left: img.left }),
              ...(img.right && { right: img.right }),
              transform: `rotate(${img.rotate}deg) scale(${img.scale})`,
              imageRendering: 'auto',
              backfaceVisibility: 'hidden',
              animationDelay: `${idx * 100}ms`,
              animationDuration: '3s',
            }}
            loading="eager"
            decoding="sync"
          />
        ))}
      </div>

      <GlassCard 
      variant="liquid" 
      className="w-full max-w-2xl z-20 p-10 shadow-2xl relative bg-white/10 backdrop-blur-lg border border-white/20 animate-fadeIn"
      style={{
        boxShadow: '0 20px 60px rgba(147, 51, 234, 0.2), 0 0 60px rgba(236, 72, 153, 0.15), 0 0 100px rgba(59, 130, 246, 0.1)',
        animationDuration: '3s',
        animationIterationCount: '1',
        animationFillMode: 'forwards',
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
          <div className="space-y-6">
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
    </div>
  );
}
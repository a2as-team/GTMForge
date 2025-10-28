import { useEffect, useState } from 'react';

interface PageTransitionProps {
  children: React.ReactNode;
  isActive: boolean;
}

export default function PageTransition({ children, isActive }: PageTransitionProps) {
  const [shouldRender, setShouldRender] = useState(isActive);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (isActive) {
      setShouldRender(true);
      // Small delay to trigger animation
      setTimeout(() => setIsAnimating(true), 50);
    } else {
      setIsAnimating(false);
      // Wait for exit animation to complete
      setTimeout(() => setShouldRender(false), 300);
    }
  }, [isActive]);

  if (!shouldRender) return null;

  return (
    <div
      className="w-full h-full transition-all duration-300 ease-out"
      style={{
        opacity: isAnimating ? 1 : 0,
        transform: isAnimating ? 'translateX(0) scale(1)' : 'translateX(-20px) scale(0.98)',
      }}
    >
      {children}
    </div>
  );
}


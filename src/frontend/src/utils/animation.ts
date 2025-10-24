import { useEffect, useState } from 'react';

/**
 * Hook to detect if user prefers reduced motion
 * Respects accessibility preferences
 */
export function useReducedMotion(): boolean {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return prefersReducedMotion;
}

/**
 * Throttle animation function to maintain 60fps
 */
export function throttleAnimation<T extends (...args: never[]) => void>(
  func: T,
  limit: number = 16 // ~60fps
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  return function(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Use Intersection Observer to lazy load animations
 */
export function useLazyAnimation(
  ref: React.RefObject<HTMLElement>,
  threshold: number = 0.1
): boolean {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold }
    );

    observer.observe(element);
    return () => observer.disconnect();
  }, [ref, threshold]);

  return isVisible;
}

/**
 * Detect if device can handle heavy animations
 */
export function canHandleHeavyAnimations(): boolean {
  // Check for mobile device
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  );
  
  // Check for low-end device indicators
  const connection = (navigator as any).connection;
  const slowConnection = connection?.effectiveType === '2g' || connection?.effectiveType === 'slow-2g';
  
  // Check hardware concurrency (CPU cores)
  const lowCPU = navigator.hardwareConcurrency ? navigator.hardwareConcurrency < 4 : false;
  
  return !isMobile && !slowConnection && !lowCPU;
}

/**
 * Request animation frame with fallback
 */
export const requestAnimFrame = 
  window.requestAnimationFrame ||
  (window as any).webkitRequestAnimationFrame ||
  (window as any).mozRequestAnimationFrame ||
  ((callback: FrameRequestCallback) => window.setTimeout(callback, 1000 / 60));

/**
 * Cancel animation frame with fallback
 */
export const cancelAnimFrame =
  window.cancelAnimationFrame ||
  (window as any).webkitCancelAnimationFrame ||
  (window as any).mozCancelAnimationFrame ||
  clearTimeout;


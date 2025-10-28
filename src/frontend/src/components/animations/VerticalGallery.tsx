import { useEffect, useMemo, useRef, useState } from "react";

export interface VerticalGalleryItem {
  id: string | number;
  src: string;
  alt?: string;
}

interface VerticalGalleryProps {
  items: VerticalGalleryItem[];
  widthClass?: string; // Tailwind width class e.g. w-64
  itemSize?: number; // px (square)
  speedMs?: number; // full loop duration in ms (auto-drift)
  direction?: "up" | "down";
  className?: string;
}

// Full-height, fixed-position vertical gallery that:
// - Duplicates list for seamless loop
// - Supports wheel/touch to manually scroll up/down
// - Also auto-drifts at a controlled speed
export default function VerticalGallery({
  items,
  widthClass = "w-64",
  itemSize = 160,
  speedMs = 15000,
  direction = "down",
  className = "",
}: VerticalGalleryProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const listRef = useRef<HTMLDivElement | null>(null);
  const doubled = useMemo(() => [...items, ...items], [items]);

  const [loopLength, setLoopLength] = useState<number>(1);
  const [offset, setOffset] = useState<number>(0);

  // Measure list height to compute loop length (half of doubled list)
  useEffect(() => {
    const measure = () => {
      const listEl = listRef.current;
      if (!listEl) return;
      const total = listEl.scrollHeight; // doubled list
      setLoopLength(Math.max(1, total / 2));
    };
    measure();
    const ro = new ResizeObserver(measure);
    if (listRef.current) ro.observe(listRef.current);
    return () => ro.disconnect();
  }, [doubled.length]);

  // Manual wheel/touch control
  useEffect(() => {
    const onWheel = (e: WheelEvent) => {
      // Move in the sign of deltaY; positive deltaY moves down
      setOffset((prev) => prev + e.deltaY * 0.6);
    };

    let touchStartY = 0;
    const onTouchStart = (e: TouchEvent) => {
      if (e.touches.length === 1) touchStartY = e.touches[0].clientY;
    };
    const onTouchMove = (e: TouchEvent) => {
      if (e.touches.length === 1) {
        const dy = touchStartY - e.touches[0].clientY;
        touchStartY = e.touches[0].clientY;
        setOffset((prev) => prev + dy);
      }
    };

    window.addEventListener("wheel", onWheel, { passive: true });
    window.addEventListener("touchstart", onTouchStart, { passive: true });
    window.addEventListener("touchmove", onTouchMove, { passive: true });
    return () => {
      window.removeEventListener("wheel", onWheel as EventListener);
      window.removeEventListener("touchstart", onTouchStart as EventListener);
      window.removeEventListener("touchmove", onTouchMove as EventListener);
    };
  }, []);

  // Auto drift via RAF
  useEffect(() => {
    let raf: number | null = null;
    let lastTs: number | null = null;
    const dir = direction === "down" ? 1 : -1;

    const stepPerMs = loopLength > 0 ? loopLength / speedMs : 0; // px per ms
    const tick = (ts: number) => {
      if (lastTs == null) lastTs = ts;
      const dt = ts - lastTs;
      lastTs = ts;
      if (stepPerMs > 0) {
        setOffset((prev) => prev + dir * dt * stepPerMs);
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => {
      if (raf) cancelAnimationFrame(raf);
    };
  }, [loopLength, speedMs, direction]);

  const translateY = (() => {
    if (loopLength <= 0) return 0;
    // Keep offset within [0, loopLength)
    let v = offset % loopLength;
    if (v < 0) v += loopLength;
    return v;
  })();

  return (
    <div
      ref={containerRef}
      className={`fixed top-0 ${widthClass} h-screen overflow-hidden -z-10 ${className}`}
      style={{ pointerEvents: "none" }}
    >
      <div
        className="relative"
        style={{
          transform: `translateY(-${translateY}px)`,
          willChange: "transform",
        }}
      >
        <div ref={listRef} className="flex flex-col items-center gap-6 py-10">
          {doubled.map((item, i) => (
            <img
              key={`${item.id}-dup-${i}`}
              src={item.src}
              alt={item.alt || ""}
              style={{ width: itemSize, height: itemSize }}
              className="object-cover rounded-xl shadow-lg border border-white/20 backdrop-blur-sm"
            />
          ))}
        </div>
      </div>
    </div>
  );
}



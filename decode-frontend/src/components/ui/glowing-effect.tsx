/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";
import React, { useRef, useState, useEffect } from "react";

export const GlowingEffect = ({
  blur = 0,
  borderWidth = 3,
  spread = 80,
  glow = true,
  disabled = false,
  proximity = 64,
  inactiveZone = 0.01,
}: any) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    if (disabled) return;
    const container = containerRef.current?.parentElement;
    if (!container) return;

    const updateMousePosition = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      setMousePosition({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      });
    };

    container.addEventListener("mousemove", updateMousePosition);
    container.addEventListener("mouseenter", () => setIsHovered(true));
    container.addEventListener("mouseleave", () => setIsHovered(false));
    return () => {
      container.removeEventListener("mousemove", updateMousePosition);
      container.removeEventListener("mouseenter", () => setIsHovered(true));
      container.removeEventListener("mouseleave", () => setIsHovered(false));
    };
  }, [disabled]);

  if (!glow) return null;

  return (
    <div
      ref={containerRef}
      className="pointer-events-none absolute inset-0 rounded-[inherit] transition-opacity duration-300 z-0"
      style={{ opacity: isHovered ? 1 : 0 }}
    >
      <div
        className="absolute inset-0 z-0 h-full w-full rounded-[inherit]"
        style={{
          background: `radial-gradient(${spread * 2.5}px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(34, 211, 238, 0.8), transparent 100%)`,
          maskImage: `linear-gradient(#fff 0 0), linear-gradient(#fff 0 0)`,
          maskClip: `padding-box, border-box`,
          maskComposite: `exclude`,
          WebkitMaskComposite: `destination-out`,
          padding: `${borderWidth}px`,
        }}
      />
    </div>
  );
};

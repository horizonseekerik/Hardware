"use client";

import React, { useRef, useEffect } from "react";

interface PixelFieldCanvasProps {
  reversed?: boolean;
  className?: string;
}

export function PixelFieldCanvas({ reversed = false, className = "" }: PixelFieldCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Accessibility check: if user prefers reduced motion, draw static pixels once
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    let animationFrameId: number;
    let width = (canvas.width = canvas.parentElement?.clientWidth || window.innerWidth);
    let height = (canvas.height = canvas.parentElement?.clientHeight || 400);

    const handleResize = () => {
      if (!canvas || !canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth;
      height = canvas.height = canvas.parentElement.clientHeight;
    };

    window.addEventListener("resize", handleResize);

    const pixelSize = 4;
    const cols = Math.floor(width / 24);
    const rows = Math.floor(height / 24);
    const count = Math.min(180, cols * rows);

    // Initialize twinkling pixels
    const pixels = Array.from({ length: count }, () => {
      const x = Math.floor(Math.random() * (width / pixelSize)) * pixelSize;
      const y = Math.floor(Math.random() * (height / pixelSize)) * pixelSize;
      const alpha = Math.random() * 0.6 + 0.1;
      const speed = (Math.random() * 0.02 + 0.005) * (Math.random() > 0.5 ? 1 : -1);
      const isOrange = Math.random() < 0.25;
      return { x, y, alpha, speed, isOrange };
    });

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      for (let i = 0; i < pixels.length; i++) {
        const p = pixels[i];
        
        // Calculate vertical density gradient
        const normalizedY = p.y / height;
        const densityFactor = reversed ? normalizedY : 1 - normalizedY;

        if (!prefersReducedMotion) {
          p.alpha += p.speed;
          if (p.alpha > 0.8 || p.alpha < 0.05) {
            p.speed = -p.speed;
          }
        }

        const currentAlpha = Math.max(0, Math.min(1, p.alpha * (0.3 + densityFactor * 0.7)));

        if (p.isOrange) {
          ctx.fillStyle = `rgba(255, 87, 34, ${currentAlpha})`;
        } else {
          ctx.fillStyle = `rgba(148, 163, 184, ${currentAlpha * 0.5})`;
        }

        ctx.fillRect(p.x, p.y, pixelSize, pixelSize);
      }

      if (!prefersReducedMotion) {
        animationFrameId = requestAnimationFrame(render);
      }
    };

    render();

    return () => {
      window.removeEventListener("resize", handleResize);
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
    };
  }, [reversed]);

  return (
    <canvas
      ref={canvasRef}
      className={`absolute inset-0 pointer-events-none z-0 ${className}`}
      style={{ imageRendering: "pixelated" }}
    />
  );
}

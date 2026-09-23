"use client";

import React, { useRef, useEffect } from "react";

interface PixelIconProps {
  name: "chip" | "laser" | "shield" | "flame" | "binary" | "bolt" | "cube" | "chart";
  size?: number;
  color?: string;
}

// 8x8 Pixel Art Bitmaps
const ICON_BITMAPS: Record<string, number[][]> = {
  chip: [
    [0,1,0,1,0,1,0,0],
    [1,1,1,1,1,1,1,1],
    [0,1,0,0,0,0,1,0],
    [1,1,0,1,1,0,1,1],
    [0,1,0,1,1,0,1,0],
    [1,1,0,0,0,0,1,1],
    [0,1,1,1,1,1,1,0],
    [0,1,0,1,0,1,0,0],
  ],
  laser: [
    [0,0,0,1,1,0,0,0],
    [0,0,1,1,1,1,0,0],
    [0,0,0,1,1,0,0,0],
    [1,1,1,1,1,1,1,1],
    [0,0,1,1,1,1,0,0],
    [0,1,0,1,1,0,1,0],
    [1,0,0,1,1,0,0,1],
    [0,0,0,1,1,0,0,0],
  ],
  shield: [
    [1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1],
    [1,1,0,1,1,0,1,1],
    [1,1,1,1,1,1,1,1],
    [0,1,1,1,1,1,1,0],
    [0,1,1,1,1,1,1,0],
    [0,0,1,1,1,1,0,0],
    [0,0,0,1,1,0,0,0],
  ],
  flame: [
    [0,0,0,0,1,0,0,0],
    [0,0,0,1,1,0,0,0],
    [0,0,1,1,1,1,0,0],
    [0,1,1,0,1,1,1,0],
    [1,1,1,0,0,1,1,1],
    [1,1,1,1,0,1,1,1],
    [0,1,1,1,1,1,1,0],
    [0,0,1,1,1,1,0,0],
  ],
  binary: [
    [0,1,0,0,0,1,1,0],
    [1,1,0,0,1,0,0,1],
    [0,1,0,0,1,0,0,1],
    [0,1,0,0,1,0,0,1],
    [0,1,0,0,1,0,0,1],
    [0,1,0,0,1,0,0,1],
    [1,1,1,0,0,1,1,0],
    [0,0,0,0,0,0,0,0],
  ],
  bolt: [
    [0,0,0,1,1,0,0,0],
    [0,0,1,1,0,0,0,0],
    [0,1,1,1,1,1,0,0],
    [0,0,0,1,1,0,0,0],
    [0,0,1,1,0,0,0,0],
    [0,1,1,1,1,1,1,0],
    [0,0,0,0,1,1,0,0],
    [0,0,0,1,0,0,0,0],
  ],
  cube: [
    [0,0,1,1,1,1,0,0],
    [0,1,0,0,0,0,1,0],
    [1,0,1,1,1,1,0,1],
    [1,0,1,0,0,1,0,1],
    [1,0,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,1],
    [0,1,1,1,1,1,1,0],
    [0,0,1,1,1,1,0,0],
  ],
  chart: [
    [0,0,0,0,0,0,1,1],
    [0,0,0,0,0,0,1,1],
    [0,0,0,1,1,0,1,1],
    [0,0,0,1,1,0,1,1],
    [0,1,1,1,1,0,1,1],
    [0,1,1,1,1,0,1,1],
    [1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0],
  ]
};

export function PixelIcon({ name, size = 32, color = "#FF5722" }: PixelIconProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const bitmap = ICON_BITMAPS[name] || ICON_BITMAPS.chip;
    const pixelSize = canvas.width / 8;

    ctx.fillStyle = color;
    for (let r = 0; r < 8; r++) {
      for (let c = 0; c < 8; c++) {
        if (bitmap[r][c] === 1) {
          ctx.fillRect(c * pixelSize, r * pixelSize, pixelSize, pixelSize);
        }
      }
    }
  }, [name, color]);

  return (
    <canvas
      ref={canvasRef}
      width={64}
      height={64}
      style={{ width: size, height: size, imageRendering: "pixelated" }}
      className="inline-block flex-shrink-0"
    />
  );
}

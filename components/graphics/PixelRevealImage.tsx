"use client";

import React, { useRef, useEffect } from "react";

interface PixelRevealImageProps {
  label: string;
  sublabel: string;
  tabKey: string;
}

export function PixelRevealImage({ label, sublabel, tabKey }: PixelRevealImageProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = (canvas.width = 480);
    const height = (canvas.height = 300);

    // Render an 8-bit schematic diagram representing photonic waveguides / switches
    ctx.fillStyle = "#121217";
    ctx.fillRect(0, 0, width, height);

    // Draw retro grid
    ctx.strokeStyle = "rgba(39, 39, 51, 0.6)";
    ctx.lineWidth = 1;
    const gridSize = 16;
    for (let x = 0; x < width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Draw optical waveguide paths
    ctx.strokeStyle = "#FF5722";
    ctx.lineWidth = 3;
    const lines = [
      [20, 60, 180, 60, 260, 120, 440, 120],
      [20, 120, 140, 120, 220, 180, 440, 180],
      [20, 180, 220, 180, 300, 80, 440, 80],
      [20, 240, 160, 240, 240, 240, 440, 240],
    ];

    lines.forEach((pts) => {
      ctx.beginPath();
      ctx.moveTo(pts[0], pts[1]);
      for (let i = 2; i < pts.length; i += 2) {
        ctx.lineTo(pts[i], pts[i + 1]);
      }
      ctx.stroke();
    });

    // Draw Sb2S3 PCM Switch Nodes (squares)
    const nodes = [
      [180, 60], [260, 120], [140, 120], [220, 180], [300, 80], [240, 240]
    ];

    nodes.forEach(([nx, ny]) => {
      ctx.fillStyle = "#FFB300";
      ctx.fillRect(nx - 6, ny - 6, 12, 12);
      ctx.strokeStyle = "#000";
      ctx.lineWidth = 2;
      ctx.strokeRect(nx - 6, ny - 6, 12, 12);
    });

    // Label overlay in retro font
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 13px monospace";
    ctx.fillText(`[TOPOLOGY: ${label.toUpperCase()}]`, 24, 34);

    ctx.fillStyle = "#FF5722";
    ctx.font = "11px monospace";
    ctx.fillText(sublabel, 24, height - 20);

  }, [label, sublabel, tabKey]);

  return (
    <div className="relative w-full overflow-hidden pixel-corners border-2 border-slate-300 dark:border-retro-darkBorder bg-retro-darkBg shadow-pixel-dark">
      <canvas
        ref={canvasRef}
        className="w-full h-auto block"
        style={{ imageRendering: "pixelated" }}
      />
      <div className="absolute top-2 right-2 px-2 py-0.5 bg-black/80 border border-retro-orange/40 text-[10px] font-mono text-retro-orange pixel-corners">
        LIVE 8-BIT TOPOLOGY
      </div>
    </div>
  );
}

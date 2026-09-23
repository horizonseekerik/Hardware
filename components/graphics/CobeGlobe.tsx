"use client";

import React, { useEffect, useRef } from "react";
import createGlobe from "cobe";
import { siteConfig } from "@/site.config";

export function CobeGlobe() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    let phi = 0;
    let width = 0;
    const canvas = canvasRef.current;
    if (!canvas) return;

    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const onResize = () => {
      if (canvas) {
        width = canvas.offsetWidth;
      }
    };
    window.addEventListener("resize", onResize);
    onResize();

    const markers = siteConfig.creatorsSection.globeLocations.map((loc) => ({
      location: [loc.lat, loc.lng] as [number, number],
      size: loc.size,
    }));

    const globe = createGlobe(canvas, {
      devicePixelRatio: 2,
      width: width * 2,
      height: width * 2,
      phi: 0,
      theta: 0.25,
      dark: 1,
      diffuse: 1.2,
      mapSamples: 16000,
      mapBrightness: 6,
      baseColor: [0.1, 0.1, 0.14],
      markerColor: [1.0, 0.34, 0.13], // #FF5722 Retro Orange
      glowColor: [1.0, 0.34, 0.13],
      markers: markers,
      onRender: (state) => {
        if (!prefersReducedMotion) {
          phi += 0.005;
        }
        state.phi = phi;
        state.width = width * 2;
        state.height = width * 2;
      },
    });

    return () => {
      globe.destroy();
      window.removeEventListener("resize", onResize);
    };
  }, []);

  return (
    <div className="w-full max-w-[360px] aspect-square relative mx-auto flex items-center justify-center">
      <div className="absolute inset-0 rounded-full border-2 border-dashed border-retro-orange/30 pointer-events-none animate-spin-slow" />
      <canvas
        ref={canvasRef}
        className="w-full h-full cursor-grab active:cursor-grabbing"
        style={{ width: "100%", height: "100%", contain: "layout paint size" }}
      />
    </div>
  );
}

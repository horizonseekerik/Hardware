"use client";

import React from "react";
import dynamic from "next/dynamic";
import { siteConfig } from "@/site.config";
import { PixelBadge } from "@/components/ui/PixelBadge";
import { PixelButton } from "@/components/ui/PixelButton";

// Dynamic SSR: false import for 8-Bit WebGL Flame Shader
const FlameShaderCanvas = dynamic(
  () => import("@/components/graphics/FlameShaderCanvas").then((mod) => mod.FlameShaderCanvas),
  { ssr: false, loading: () => <div className="absolute inset-0 bg-retro-darkSurface/90 animate-pulse" /> }
);

export function FinalCTA() {
  return (
    <section className="relative py-20 md:py-32 overflow-hidden border-b-2 border-slate-200 dark:border-retro-darkBorder bg-retro-darkBg">
      {/* 8-Bit WebGL Flame Shader Background */}
      <FlameShaderCanvas />

      {/* CRT Scanline effect over shader */}
      <div className="absolute inset-0 scanlines opacity-50 pointer-events-none" />

      <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 text-center">
        <PixelBadge variant="orange" icon="🔥">
          {siteConfig.finalCta.tag}
        </PixelBadge>

        <h2 className="mt-4 font-mono text-2xl sm:text-4xl md:text-5xl font-black uppercase text-white tracking-tight leading-tight drop-shadow-[0_2px_12px_rgba(0,0,0,0.8)]">
          {siteConfig.finalCta.headline}
        </h2>

        <p className="mt-4 max-w-2xl mx-auto text-sm sm:text-base text-slate-200 font-sans leading-relaxed drop-shadow-[0_1px_4px_rgba(0,0,0,0.8)]">
          {siteConfig.finalCta.subhead}
        </p>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <PixelButton
            variant="primary"
            size="lg"
            href={siteConfig.finalCta.primaryButton.href}
          >
            {siteConfig.finalCta.primaryButton.text}
          </PixelButton>

          <PixelButton
            variant="retro"
            size="lg"
            href={siteConfig.finalCta.secondaryButton.href}
          >
            {siteConfig.finalCta.secondaryButton.text}
          </PixelButton>
        </div>

        <div className="mt-8 text-xs font-mono text-retro-orange/90 font-bold uppercase tracking-widest">
          ◆ NO ADCS REQUIRED • ZERO ANALOG DRIFT • INT64 VERIFIED ◆
        </div>
      </div>
    </section>
  );
}

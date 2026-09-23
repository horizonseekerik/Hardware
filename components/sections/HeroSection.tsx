"use client";

import React, { useEffect, useState } from "react";
import { siteConfig } from "@/site.config";
import { PixelBadge } from "@/components/ui/PixelBadge";
import { PixelButton } from "@/components/ui/PixelButton";
import { PixelFieldCanvas } from "@/components/graphics/PixelFieldCanvas";

export function HeroSection() {
  const [revealedWordCount, setRevealedWordCount] = useState(0);

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) {
      setRevealedWordCount(siteConfig.hero.titleWords.length);
      return;
    }

    const interval = setInterval(() => {
      setRevealedWordCount((prev) => {
        if (prev < siteConfig.hero.titleWords.length) {
          return prev + 1;
        }
        clearInterval(interval);
        return prev;
      });
    }, 180);

    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative min-h-[82vh] flex items-center justify-center overflow-hidden py-16 md:py-24 border-b-2 border-slate-200 dark:border-retro-darkBorder">
      {/* Background Animated Pixel Field */}
      <PixelFieldCanvas />

      {/* Retro Scanline Accent */}
      <div className="absolute inset-0 scanlines" />

      <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 text-center">
        {/* Top Retro Tag */}
        <div className="inline-flex items-center gap-2 mb-6">
          <PixelBadge variant="orange" icon="⚡">
            {siteConfig.hero.tag}
          </PixelBadge>
        </div>

        {/* Word-by-Word Reveal Headline */}
        <h1 className="font-mono text-3xl sm:text-5xl md:text-6xl font-black uppercase tracking-tight text-slate-900 dark:text-white mb-6 leading-tight min-h-[3.2em] sm:min-h-[2.4em] flex flex-wrap items-center justify-center gap-x-3 gap-y-2">
          {siteConfig.hero.titleWords.map((word, idx) => {
            const isRevealed = idx < revealedWordCount;
            const isOrange = word === "PHOTONIC" || word === "RESIDUE";

            return (
              <span
                key={idx}
                className={`transition-all duration-300 transform ${
                  isRevealed
                    ? "opacity-100 translate-y-0"
                    : "opacity-0 translate-y-4"
                } ${
                  isOrange
                    ? "text-retro-orange drop-shadow-[0_2px_12px_rgba(255,87,34,0.4)]"
                    : "text-slate-900 dark:text-white"
                }`}
              >
                {word}
              </span>
            );
          })}
        </h1>

        {/* Editorial Subhead */}
        <p className="max-w-3xl mx-auto text-sm sm:text-base md:text-lg text-slate-600 dark:text-slate-300 font-sans leading-relaxed mb-8">
          {siteConfig.hero.subhead}
        </p>

        {/* CTA Button Row */}
        <div className="flex flex-wrap items-center justify-center gap-4 mb-10">
          <PixelButton
            variant="primary"
            size="lg"
            href={siteConfig.hero.primaryCta.href}
          >
            {siteConfig.hero.primaryCta.text}
          </PixelButton>

          <PixelButton
            variant="outline"
            size="lg"
            href={siteConfig.hero.secondaryCta.href}
          >
            {siteConfig.hero.secondaryCta.text}
          </PixelButton>
        </div>

        {/* Meta badges row */}
        <div className="inline-flex flex-wrap items-center justify-center gap-3 pt-4 border-t-2 border-dotted border-slate-300 dark:border-retro-darkBorder/60">
          {siteConfig.hero.metaBadges.map((badge, idx) => (
            <span
              key={idx}
              className="text-xs font-mono font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest flex items-center gap-1.5"
            >
              <span className="text-retro-orange">■</span>
              {badge}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

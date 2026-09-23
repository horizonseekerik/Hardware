"use client";

import React, { useState } from "react";
import { siteConfig } from "@/site.config";
import { PixelBadge } from "@/components/ui/PixelBadge";
import { PixelCard } from "@/components/ui/PixelCard";

export function TestimonialCarousel() {
  const [currentIdx, setCurrentIdx] = useState(0);
  const items = siteConfig.testimonials;

  const next = () => setCurrentIdx((prev) => (prev + 1) % items.length);
  const prev = () => setCurrentIdx((prev) => (prev - 1 + items.length) % items.length);

  const current = items[currentIdx];

  return (
    <section className="py-16 md:py-24 border-b-2 border-slate-200 dark:border-retro-darkBorder bg-white dark:bg-retro-darkBg">
      <div className="max-w-4xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-10">
          <PixelBadge variant="orange" icon="💬">
            PEER REVIEWS & APPRAISALS
          </PixelBadge>
          <h2 className="mt-3 font-mono text-2xl sm:text-3xl font-black uppercase text-slate-900 dark:text-white">
            COMMUNITY & ACADEMIC VOICES
          </h2>
        </div>

        <PixelCard variant="featured" className="p-8 md:p-10 relative">
          {/* Big retro quotes */}
          <div className="text-4xl font-pixel text-retro-orange/30 absolute top-4 left-6">
            “
          </div>

          <div className="relative z-10 pt-4">
            <p className="text-base sm:text-xl font-serif italic text-slate-800 dark:text-slate-200 leading-relaxed min-h-[5em]">
              {current.quote}
            </p>

            <div className="mt-8 pt-6 border-t-2 border-dotted border-retro-orange/30 flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                {/* Pixel-notched avatar badge */}
                <div className="w-12 h-12 bg-retro-orange/20 border-2 border-retro-orange pixel-corners flex items-center justify-center font-mono font-bold text-retro-orange text-sm">
                  {current.author.split(" ").map((n) => n[0]).join("")}
                </div>
                <div>
                  <div className="font-mono font-bold text-slate-900 dark:text-white text-sm sm:text-base">
                    {current.author}
                  </div>
                  <div className="text-xs font-mono text-retro-orange font-bold">
                    {current.role} • {current.institution}
                  </div>
                </div>
              </div>

              {/* Navigation controls */}
              <div className="flex items-center gap-2">
                <button
                  onClick={prev}
                  aria-label="Previous review"
                  className="w-9 h-9 border-2 border-slate-300 dark:border-retro-darkBorder hover:border-retro-orange bg-white dark:bg-retro-darkCard pixel-corners font-mono text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center justify-center transition-colors"
                >
                  ◀
                </button>
                <span className="font-mono text-xs text-slate-500 px-1">
                  {currentIdx + 1}/{items.length}
                </span>
                <button
                  onClick={next}
                  aria-label="Next review"
                  className="w-9 h-9 border-2 border-slate-300 dark:border-retro-darkBorder hover:border-retro-orange bg-white dark:bg-retro-darkCard pixel-corners font-mono text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center justify-center transition-colors"
                >
                  ▶
                </button>
              </div>
            </div>
          </div>
        </PixelCard>
      </div>
    </section>
  );
}

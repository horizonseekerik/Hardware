"use client";

import React from "react";
import { siteConfig } from "@/site.config";
import { PixelBadge } from "@/components/ui/PixelBadge";
import { PixelCard } from "@/components/ui/PixelCard";

export function UseCaseCards() {
  return (
    <section id="usecases" className="py-16 md:py-24 border-b-2 border-slate-200 dark:border-retro-darkBorder bg-slate-50 dark:bg-retro-darkSurface/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <PixelBadge variant="orange" icon="🎯">
            ACCELERATION WORKLOADS
          </PixelBadge>
          <h2 className="mt-3 font-mono text-2xl sm:text-3xl md:text-4xl font-black uppercase text-slate-900 dark:text-white">
            MISSION-CRITICAL APPLICATIONS
          </h2>
          <p className="mt-3 text-sm sm:text-base text-slate-600 dark:text-slate-400">
            From trillion-parameter generative transformers to real-time synthetic aperture radar and cryptographic lattices.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {siteConfig.useCases.map((uc, idx) => (
            <PixelCard
              key={idx}
              variant="default"
              className="group hover:border-retro-orange transition-all duration-200"
            >
              <div className="flex items-start justify-between gap-4 mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{uc.icon}</span>
                  <div>
                    <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-retro-orange">
                      {uc.category}
                    </span>
                    <h3 className="font-mono text-base sm:text-lg font-bold text-slate-900 dark:text-white group-hover:text-retro-orange transition-colors">
                      {uc.title}
                    </h3>
                  </div>
                </div>

                <span className="text-xs font-mono font-extrabold px-2 py-1 bg-retro-green/15 text-retro-green border border-retro-green/40 pixel-corners">
                  {uc.throughputGain}
                </span>
              </div>

              <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 font-sans leading-relaxed mb-4">
                {uc.description}
              </p>

              <div className="pt-3 border-t border-dashed border-slate-200 dark:border-retro-darkBorder flex items-center justify-between text-xs font-mono">
                <span className="text-slate-500 dark:text-slate-400">Key Advantage:</span>
                <span className="font-bold text-slate-800 dark:text-slate-200">{uc.advantage}</span>
              </div>
            </PixelCard>
          ))}
        </div>
      </div>
    </section>
  );
}

"use client";

import React from "react";
import { siteConfig } from "@/site.config";
import { PixelBadge } from "@/components/ui/PixelBadge";
import { PixelIcon } from "@/components/ui/PixelIcon";
import { PixelCard } from "@/components/ui/PixelCard";

export function BenefitsGrid() {
  return (
    <section id="benefits" className="py-16 md:py-24 border-b-2 border-slate-200 dark:border-retro-darkBorder bg-white dark:bg-retro-darkBg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <PixelBadge variant="orange" icon="⚡">
            COMPETITIVE ADVANTAGES
          </PixelBadge>
          <h2 className="mt-3 font-mono text-2xl sm:text-3xl md:text-4xl font-black uppercase text-slate-900 dark:text-white">
            WHY DETERMINISTIC OPTICS WINS
          </h2>
          <p className="mt-3 text-sm sm:text-base text-slate-600 dark:text-slate-400">
            Overcoming the physical bottlenecks of analog MZI meshes, thermal runaway, and electronic wire delays.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {siteConfig.benefits.map((benefit, idx) => (
            <PixelCard
              key={idx}
              variant="default"
              className="group hover:border-retro-orange transition-all duration-200"
            >
              <div className="flex items-start justify-between gap-4 mb-4">
                <div className="p-2 border-2 border-slate-200 dark:border-retro-darkBorder bg-slate-50 dark:bg-retro-darkCard pixel-corners group-hover:border-retro-orange transition-colors">
                  <PixelIcon name={benefit.iconType} size={36} color="#FF5722" />
                </div>
                <span className="text-[11px] font-mono px-2 py-0.5 bg-retro-orange/10 text-retro-orange border border-retro-orange/30 pixel-corners font-bold">
                  {benefit.metric}
                </span>
              </div>

              <h3 className="font-mono text-base sm:text-lg font-bold text-slate-900 dark:text-white uppercase mb-2 group-hover:text-retro-orange transition-colors">
                {benefit.title}
              </h3>

              <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 font-sans leading-relaxed">
                {benefit.description}
              </p>
            </PixelCard>
          ))}
        </div>
      </div>
    </section>
  );
}

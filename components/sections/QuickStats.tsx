"use client";

import React, { useEffect, useState } from "react";
import { siteConfig } from "@/site.config";

export function QuickStats() {
  const [hasAnimated, setHasAnimated] = useState(false);

  useEffect(() => {
    setHasAnimated(true);
  }, []);

  return (
    <section className="py-12 bg-slate-50 dark:bg-retro-darkSurface/60 border-b-2 border-slate-200 dark:border-retro-darkBorder">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <div className="text-xs font-mono font-bold uppercase tracking-widest text-retro-orange mb-1">
            VERIFIED PHYSICAL METRICS
          </div>
          <h2 className="font-mono text-xl sm:text-2xl font-black uppercase text-slate-900 dark:text-white">
            ARCHITECTURAL BENCHMARK ATTRIBUTION
          </h2>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
          {siteConfig.stats.map((stat, idx) => (
            <div
              key={idx}
              className={`p-4 bg-white dark:bg-retro-darkCard border-2 pixel-corners flex flex-col justify-between transition-all duration-300 ${
                stat.highlight
                  ? "border-retro-orange shadow-pixel-orange dark:shadow-pixel-orange"
                  : "border-slate-200 dark:border-retro-darkBorder shadow-pixel-dark"
              }`}
            >
              <div className="text-[11px] font-mono text-slate-500 dark:text-slate-400 uppercase font-bold tracking-wider mb-2">
                {stat.label}
              </div>

              {/* Counter with clipped slide-up entrance */}
              <div className="overflow-hidden py-1">
                <div
                  className={`transform transition-transform duration-700 font-mono font-black ${
                    hasAnimated ? "translate-y-0" : "translate-y-full"
                  }`}
                >
                  <span className="text-2xl sm:text-3xl text-slate-900 dark:text-white">
                    {stat.value}
                  </span>
                  {stat.unit && (
                    <span className="text-xs ml-1 text-retro-orange font-bold">
                      {stat.unit}
                    </span>
                  )}
                </div>
              </div>

              <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-2 font-mono leading-tight">
                {stat.subtext}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

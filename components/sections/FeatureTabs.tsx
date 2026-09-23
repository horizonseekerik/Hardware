"use client";

import React, { useState, useEffect } from "react";
import { siteConfig } from "@/site.config";
import { PixelBadge } from "@/components/ui/PixelBadge";
import { PixelRevealImage } from "@/components/graphics/PixelRevealImage";

export function FeatureTabs() {
  const [activeTabIdx, setActiveTabIdx] = useState(0);
  const [isAutoCycling, setIsAutoCycling] = useState(true);

  const tabs = siteConfig.featureTabs;
  const currentTab = tabs[activeTabIdx];

  // Auto-cycling feature tabs
  useEffect(() => {
    if (!isAutoCycling) return;
    const interval = setInterval(() => {
      setActiveTabIdx((prev) => (prev + 1) % tabs.length);
    }, 6000);
    return () => clearInterval(interval);
  }, [isAutoCycling, tabs.length]);

  return (
    <section id="features" className="py-16 md:py-24 border-b-2 border-slate-200 dark:border-retro-darkBorder bg-slate-50 dark:bg-retro-darkSurface/40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <PixelBadge variant="orange" icon="🧮">
            ARCHITECTURAL PILLARS
          </PixelBadge>
          <h2 className="mt-3 font-mono text-2xl sm:text-3xl md:text-4xl font-black uppercase text-slate-900 dark:text-white">
            FOUR CORE FOUNDATIONS OF JANUS
          </h2>
          <p className="mt-3 text-sm sm:text-base text-slate-600 dark:text-slate-400">
            Click any pillar to inspect mathematical formulations and 8-bit waveguide routing topologies.
          </p>
        </div>

        {/* Tab Buttons Row */}
        <div className="flex flex-wrap items-center justify-center gap-2 mb-8">
          {tabs.map((tab, idx) => {
            const isActive = idx === activeTabIdx;
            return (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTabIdx(idx);
                  setIsAutoCycling(false);
                }}
                className={`px-4 py-2.5 font-mono text-xs sm:text-sm font-bold uppercase tracking-wider pixel-corners border-2 transition-all ${
                  isActive
                    ? "bg-retro-orange text-white border-black dark:border-retro-orange shadow-pixel-dark"
                    : "bg-white dark:bg-retro-darkSurface text-slate-700 dark:text-slate-300 border-slate-200 dark:border-retro-darkBorder hover:border-retro-orange"
                }`}
              >
                [{String(idx + 1).padStart(2, "0")}] {tab.title}
              </button>
            );
          })}
        </div>

        {/* Tab Content Display Area */}
        <div className="p-6 md:p-8 bg-white dark:bg-retro-darkSurface border-2 border-slate-300 dark:border-retro-darkBorder pixel-corners shadow-pixel-dark">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Left: Explanations & Metrics */}
            <div className="lg:col-span-6 space-y-6">
              <div>
                <PixelBadge variant="cyan" icon="◆">
                  {currentTab.badge}
                </PixelBadge>
                <h3 className="mt-2 font-mono text-xl sm:text-2xl font-black text-slate-900 dark:text-white uppercase">
                  {currentTab.title}
                </h3>
                <div className="text-xs font-mono font-bold text-retro-orange mt-1">
                  {currentTab.subtitle}
                </div>
              </div>

              <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300 leading-relaxed font-sans">
                {currentTab.description}
              </p>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 gap-3 pt-2">
                {currentTab.metrics.map((m, mIdx) => (
                  <div
                    key={mIdx}
                    className="p-3 bg-slate-50 dark:bg-retro-darkCard border border-slate-200 dark:border-retro-darkBorder pixel-corners"
                  >
                    <div className="text-[10px] font-mono text-slate-500 dark:text-slate-400 uppercase font-bold">
                      {m.label}
                    </div>
                    <div className="text-base sm:text-lg font-mono font-extrabold text-retro-orange mt-0.5">
                      {m.value}
                    </div>
                  </div>
                ))}
              </div>

              {/* Code snippet */}
              <div className="p-3.5 bg-slate-900 text-slate-200 pixel-corners border border-slate-700 font-mono text-xs overflow-x-auto">
                <div className="text-[10px] text-retro-amber font-bold mb-1">// CO-DESIGN SPECIFICATION</div>
                <pre>{currentTab.codeSnippet}</pre>
              </div>
            </div>

            {/* Right: Pixel-Reveal Interactive Topology Canvas */}
            <div className="lg:col-span-6 flex flex-col justify-center">
              <PixelRevealImage
                label={currentTab.title}
                sublabel={currentTab.subtitle}
                tabKey={currentTab.id}
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

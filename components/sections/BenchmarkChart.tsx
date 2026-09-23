"use client";

import React, { useState } from "react";
import { siteConfig } from "@/site.config";
import { PixelBadge } from "@/components/ui/PixelBadge";

export function BenchmarkChart() {
  const [selectedMetricIdx, setSelectedMetricIdx] = useState(0);

  const categories = siteConfig.benchmarks.categories;
  const currentCategory = categories[selectedMetricIdx];

  // Data series for the selected metric
  const items = [
    { label: "JANUS Model 6B (Hyperscale 3D)", value: currentCategory.janus6b, color: "#FF5722", isPrimary: true },
    { label: "JANUS Model 1A (Planar 10.24mm²)", value: currentCategory.janus1a, color: "#FFB300" },
    { label: "NVIDIA H100 SXM (Electronic GPU)", value: currentCategory.h100, color: "#64748B" },
    { label: "Analog MZI Mesh (Conventional)", value: currentCategory.mziMesh, color: "#475569" },
  ];

  // Maximum value for proportional bar scaling
  const maxValue = Math.max(...items.map((i) => i.value));

  return (
    <section id="benchmarks" className="py-16 md:py-24 border-b-2 border-slate-200 dark:border-retro-darkBorder bg-slate-50 dark:bg-retro-darkSurface/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <PixelBadge variant="orange" icon="📊">
            CROSS-PARADIGM BENCHMARKS
          </PixelBadge>
          <h2 className="mt-3 font-mono text-2xl sm:text-3xl md:text-4xl font-black uppercase text-slate-900 dark:text-white">
            PHYSICAL EFFICIENCY & THROUGHPUT
          </h2>
          <p className="mt-3 text-sm sm:text-base text-slate-600 dark:text-slate-400">
            Compare Project JANUS against leading electronic compute engines and analog photonic architectures.
          </p>
        </div>

        {/* Metric Selector Tabs */}
        <div className="flex flex-wrap items-center justify-center gap-2 mb-8">
          {categories.map((cat, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedMetricIdx(idx)}
              className={`px-4 py-2 font-mono text-xs sm:text-sm font-bold uppercase tracking-wider pixel-corners border-2 transition-all ${
                idx === selectedMetricIdx
                  ? "bg-retro-orange text-white border-black dark:border-retro-orange shadow-pixel-dark"
                  : "bg-white dark:bg-retro-darkSurface text-slate-700 dark:text-slate-300 border-slate-200 dark:border-retro-darkBorder hover:border-retro-orange"
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>

        {/* Interactive Bar Chart Box */}
        <div className="p-6 md:p-8 bg-white dark:bg-retro-darkSurface border-2 border-slate-300 dark:border-retro-darkBorder pixel-corners shadow-pixel-dark max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-dashed border-slate-200 dark:border-retro-darkBorder">
            <div>
              <div className="text-xs font-mono text-retro-orange font-bold uppercase">
                ACTIVE METRIC
              </div>
              <h3 className="font-mono text-lg sm:text-xl font-black text-slate-900 dark:text-white">
                {currentCategory.name}
              </h3>
            </div>
            <div className="text-right text-xs font-mono text-slate-500 dark:text-slate-400">
              [LOG-NORMALIZED SCALE]
            </div>
          </div>

          {/* Bar rows */}
          <div className="space-y-6">
            {items.map((item, idx) => {
              const percentage = maxValue > 0 ? Math.max(6, (item.value / maxValue) * 100) : 0;
              return (
                <div key={idx} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs sm:text-sm font-mono font-bold">
                    <span className={item.isPrimary ? "text-retro-orange" : "text-slate-800 dark:text-slate-200"}>
                      {item.label}
                    </span>
                    <span className="font-mono font-black text-slate-900 dark:text-white">
                      {item.value.toLocaleString()}
                    </span>
                  </div>

                  {/* 8-bit notched bar */}
                  <div className="h-6 w-full bg-slate-100 dark:bg-retro-darkBg border border-slate-300 dark:border-retro-darkBorder pixel-corners overflow-hidden p-0.5">
                    <div
                      className="h-full transition-all duration-500 pixel-corners flex items-center justify-end px-2"
                      style={{
                        width: `${percentage}%`,
                        backgroundColor: item.color,
                      }}
                    >
                      {percentage > 20 && (
                        <span className="text-[10px] font-mono text-white font-extrabold uppercase">
                          {item.value}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Legend and Citation */}
          <div className="mt-8 pt-4 border-t-2 border-dotted border-slate-200 dark:border-retro-darkBorder flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono text-slate-500 dark:text-slate-400">
            <span>AUDIT: 5-Tier Multi-Physics Co-Simulation Suite (MEEP + Elmer + Xyce)</span>
            <a href="/JANUS_Mini16_Simulation_Report.pdf" target="_blank" className="text-retro-orange hover:underline font-bold">
              View Simulation Report (PDF) →
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

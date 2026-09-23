"use client";

import React from "react";
import dynamic from "next/dynamic";
import Image from "next/image";
import { siteConfig } from "@/site.config";
import { PixelBadge } from "@/components/ui/PixelBadge";
import { PixelCard } from "@/components/ui/PixelCard";

// Dynamic SSR: false import for Cobe 3D Globe to avoid hydration errors on Vercel
const CobeGlobe = dynamic(
  () => import("@/components/graphics/CobeGlobe").then((mod) => mod.CobeGlobe),
  { ssr: false, loading: () => <div className="w-[300px] h-[300px] mx-auto bg-retro-darkBorder/20 pixel-corners animate-pulse" /> }
);

export function CreatorsBand() {
  return (
    <section id="creators" className="py-16 md:py-24 border-b-2 border-slate-200 dark:border-retro-darkBorder bg-white dark:bg-retro-darkBg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <PixelBadge variant="orange" icon="🌐">
            {siteConfig.creatorsSection.badge}
          </PixelBadge>
          <h2 className="mt-3 font-mono text-2xl sm:text-3xl md:text-4xl font-black uppercase text-slate-900 dark:text-white">
            {siteConfig.creatorsSection.title}
          </h2>
          <p className="mt-3 text-sm sm:text-base text-slate-600 dark:text-slate-400 font-sans">
            {siteConfig.creatorsSection.description}
          </p>
        </div>

        {/* 2-Column: Interactive 3D Globe + Creator Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          {/* Left: 3D Interactive WebGL Globe */}
          <div className="lg:col-span-5 flex flex-col items-center justify-center p-6 bg-slate-50 dark:bg-retro-darkSurface border-2 border-slate-200 dark:border-retro-darkBorder pixel-corners shadow-pixel-dark">
            <div className="text-xs font-mono font-bold uppercase tracking-widest text-retro-orange mb-4 flex items-center gap-2">
              <span className="w-2 h-2 bg-retro-orange rounded-full animate-ping" />
              GLOBAL RESEARCH COLLABORATIVE
            </div>
            
            <CobeGlobe />

            <div className="mt-4 text-center">
              <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400">
                DRAG GLOBE TO ROTATE • RESEARCH HUBS MAPPED
              </span>
            </div>
          </div>

          {/* Right: Creator Profile Cards */}
          <div className="lg:col-span-7 space-y-5">
            {siteConfig.creatorsSection.creators.map((creator, idx) => (
              <PixelCard key={idx} variant="default" className="border-2 border-slate-200 dark:border-retro-darkBorder">
                <div className="flex flex-col sm:flex-row items-start gap-4">
                  {/* Pixel Notched Avatar */}
                  <div className="relative w-16 h-16 flex-shrink-0 border-2 border-retro-orange bg-retro-orange/10 pixel-corners overflow-hidden p-1 shadow-pixel-dark">
                    <Image
                      src={creator.avatar}
                      alt={creator.name}
                      width={64}
                      height={64}
                      className="object-contain"
                    />
                  </div>

                  <div className="flex-1">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div>
                        <h3 className="font-mono text-base sm:text-lg font-bold text-slate-900 dark:text-white">
                          {creator.name}
                        </h3>
                        <div className="text-xs font-mono font-bold text-retro-orange">
                          {creator.role}
                        </div>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 bg-slate-100 dark:bg-retro-darkCard border border-slate-300 dark:border-retro-darkBorder text-slate-600 dark:text-slate-300 pixel-corners">
                        {creator.location}
                      </span>
                    </div>

                    <p className="mt-2 text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed font-sans">
                      {creator.bio}
                    </p>

                    <div className="mt-4 flex flex-wrap items-center gap-2 pt-3 border-t border-dashed border-slate-200 dark:border-retro-darkBorder">
                      {creator.links.doi && (
                        <a
                          href={creator.links.doi}
                          target="_blank"
                          rel="noreferrer"
                          className="text-[11px] font-mono text-retro-orange hover:underline font-bold flex items-center gap-1"
                        >
                          <span>[DOI: 10.5281/zenodo.22733656]</span>
                        </a>
                      )}
                      {creator.links.github && (
                        <a
                          href={creator.links.github}
                          target="_blank"
                          rel="noreferrer"
                          className="text-[11px] font-mono text-slate-600 dark:text-slate-400 hover:text-retro-orange font-bold flex items-center gap-1 ml-auto"
                        >
                          <span>GitHub Repository →</span>
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </PixelCard>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

"use client";

import React from "react";
import { siteConfig } from "@/site.config";
import { PixelBadge } from "@/components/ui/PixelBadge";
import { PixelButton } from "@/components/ui/PixelButton";
import { PixelCard } from "@/components/ui/PixelCard";

export function PricingGrid() {
  return (
    <section id="pricing" className="py-16 md:py-24 border-b-2 border-slate-200 dark:border-retro-darkBorder bg-white dark:bg-retro-darkBg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <PixelBadge variant="orange" icon="💰">
            ENGAGEMENT TIERS
          </PixelBadge>
          <h2 className="mt-3 font-mono text-2xl sm:text-3xl md:text-4xl font-black uppercase text-slate-900 dark:text-white">
            RESEARCH & COMMERCIAL LICENSING
          </h2>
          <p className="mt-3 text-sm sm:text-base text-slate-600 dark:text-slate-400">
            Open-access academic manuscripts alongside foundry tape-out packages and hyperscale 3D rack architecture licensing.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch">
          {siteConfig.pricing.map((plan, idx) => (
            <PixelCard
              key={idx}
              variant={plan.featured ? "featured" : "default"}
              className={`flex flex-col justify-between relative ${
                plan.featured ? "scale-105 z-10" : ""
              }`}
            >
              {plan.badge && (
                <div className="absolute -top-3 left-6">
                  <PixelBadge variant={plan.featured ? "orange" : "muted"} icon="★">
                    {plan.badge}
                  </PixelBadge>
                </div>
              )}

              <div>
                <h3 className="font-mono text-lg font-black text-slate-900 dark:text-white uppercase mb-2">
                  {plan.name}
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-400 font-sans mb-6 min-h-[2.8em]">
                  {plan.description}
                </p>

                <div className="flex items-baseline gap-1 mb-6 pb-6 border-b-2 border-dotted border-slate-200 dark:border-retro-darkBorder">
                  <span className="font-mono text-3xl sm:text-4xl font-black text-slate-900 dark:text-white">
                    {plan.price}
                  </span>
                  <span className="text-xs font-mono text-slate-500">/{plan.period}</span>
                </div>

                <div className="space-y-3 mb-8">
                  {plan.features.map((feat, fIdx) => (
                    <div key={fIdx} className="flex items-start gap-2.5 text-xs font-mono text-slate-700 dark:text-slate-300">
                      <span className="text-retro-orange flex-shrink-0 font-bold">✓</span>
                      <span>{feat}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <PixelButton
                  variant={plan.featured ? "primary" : "outline"}
                  size="md"
                  href={plan.ctaHref}
                  className="w-full"
                >
                  {plan.ctaLabel}
                </PixelButton>
              </div>
            </PixelCard>
          ))}
        </div>
      </div>
    </section>
  );
}

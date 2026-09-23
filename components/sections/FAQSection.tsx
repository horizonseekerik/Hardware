"use client";

import React from "react";
import { siteConfig } from "@/site.config";
import { PixelBadge } from "@/components/ui/PixelBadge";
import { RetroAccordion } from "@/components/ui/RetroAccordion";

export function FAQSection() {
  return (
    <section id="faq" className="py-16 md:py-24 border-b-2 border-slate-200 dark:border-retro-darkBorder bg-slate-50 dark:bg-retro-darkSurface/50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-12">
          <PixelBadge variant="orange" icon="❓">
            TECHNICAL INQUIRIES
          </PixelBadge>
          <h2 className="mt-3 font-mono text-2xl sm:text-3xl md:text-4xl font-black uppercase text-slate-900 dark:text-white">
            FREQUENTLY ASKED QUESTIONS
          </h2>
          <p className="mt-3 text-sm sm:text-base text-slate-600 dark:text-slate-400">
            Addressing physical optics, material physics, mathematical precision guarantees, and foundry tape-out.
          </p>
        </div>

        <RetroAccordion items={siteConfig.faqs} />
      </div>
    </section>
  );
}

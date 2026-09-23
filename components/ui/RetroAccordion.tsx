"use client";

import React, { useState } from "react";
import { FAQItem } from "@/site.config";

interface RetroAccordionProps {
  items: FAQItem[];
}

export function RetroAccordion({ items }: RetroAccordionProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const toggle = (idx: number) => {
    setOpenIndex(openIndex === idx ? null : idx);
  };

  return (
    <div className="space-y-4">
      {items.map((item, idx) => {
        const isOpen = openIndex === idx;
        return (
          <div
            key={idx}
            className={`transition-all duration-200 pixel-corners ${
              isOpen
                ? "bg-white dark:bg-retro-darkSurface border-2 border-retro-orange shadow-pixel-dark"
                : "bg-slate-50 dark:bg-retro-darkSurface/50 border-2 border-slate-200 dark:border-retro-darkBorder"
            }`}
          >
            <button
              onClick={() => toggle(idx)}
              className="w-full text-left p-5 flex items-center justify-between gap-4 font-mono font-bold text-sm md:text-base tracking-wide"
            >
              <div className="flex items-center gap-3">
                <span className="text-retro-orange text-xs">[{String(idx + 1).padStart(2, "0")}]</span>
                <span className={isOpen ? "text-retro-orange" : "text-slate-900 dark:text-slate-100"}>
                  {item.question}
                </span>
              </div>
              <span className="font-pixel text-xs text-retro-orange flex-shrink-0">
                {isOpen ? "[-]" : "[+]"}
              </span>
            </button>

            {isOpen && (
              <div className="px-5 pb-5 pt-1 text-sm text-slate-600 dark:text-slate-400 font-sans leading-relaxed border-t-2 border-dotted border-retro-orange/30">
                <p className="mt-3">{item.answer}</p>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

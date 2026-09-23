"use client";

import React, { useState } from "react";
import Link from "next/link";
import { siteConfig } from "@/site.config";
import { PixelFieldCanvas } from "@/components/graphics/PixelFieldCanvas";
import { PixelButton } from "@/components/ui/PixelButton";

export function Footer() {
  const [email, setEmail] = useState("");
  const [subscribed, setSubscribed] = useState(false);

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) {
      setSubscribed(true);
      setEmail("");
    }
  };

  return (
    <footer className="relative pt-16 pb-12 overflow-hidden bg-slate-900 dark:bg-black text-slate-300 border-t-2 border-retro-orange/30">
      {/* Reversed density Pixel Field background */}
      <PixelFieldCanvas reversed={true} className="opacity-40" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Newsletter & Editorial Announcement Bar */}
        <div className="p-6 md:p-8 bg-slate-800/80 dark:bg-retro-darkSurface/80 border-2 border-slate-700 dark:border-retro-darkBorder pixel-corners mb-12 shadow-pixel-dark">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
            <div className="lg:col-span-7">
              <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-retro-orange">
                ACADEMIC DISPATCH & FOUNDRY UPDATES
              </span>
              <h3 className="font-mono text-lg sm:text-xl font-black text-white uppercase mt-1">
                STAY INFORMED ON SILICON TAPE-OUTS
              </h3>
              <p className="text-xs sm:text-sm text-slate-400 mt-1 font-sans">
                Receive peer-reviewed preprint releases, MEEP simulation additions, and multi-project wafer schedule announcements.
              </p>
            </div>

            <div className="lg:col-span-5">
              {subscribed ? (
                <div className="p-3 bg-retro-green/10 border border-retro-green/40 text-retro-green font-mono text-xs font-bold pixel-corners">
                  ✓ DISPATCH SUBSCRIPTION CONFIRMED. ZERO SPAM PROMISE.
                </div>
              ) : (
                <form onSubmit={handleSubscribe} className="flex gap-2">
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="researcher@institute.edu"
                    className="flex-1 px-3 py-2 bg-slate-950 border border-slate-700 text-xs font-mono text-white pixel-corners focus:outline-none focus:border-retro-orange"
                  />
                  <PixelButton variant="primary" size="sm" type="submit">
                    SUBSCRIBE
                  </PixelButton>
                </form>
              )}
            </div>
          </div>
        </div>

        {/* Multi-Column Links */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
          {/* Col 1: Brand Info */}
          <div>
            <div className="font-mono font-black text-xl text-white tracking-wider flex items-center gap-2 mb-3">
              <span>JANUS</span>
              <span className="text-[10px] px-1.5 py-0.5 bg-retro-orange text-white pixel-corners font-mono">
                RNS
              </span>
            </div>
            <p className="text-xs text-slate-400 font-sans leading-relaxed mb-4">
              Deterministic Spatial Residue Optical Computing Architecture delivering 104.8 PetaMAC/s at zero static hold power.
            </p>
            <div className="text-[11px] font-mono text-retro-orange font-bold">
              PERMANENT DOI: 10.5281/zenodo.22733656
            </div>
          </div>

          {/* Col 2, 3, 4: Configured Footer Link Groups */}
          {siteConfig.footer.links.map((group, idx) => (
            <div key={idx}>
              <h4 className="font-mono text-xs font-extrabold uppercase text-white tracking-wider mb-4 pb-1 border-b border-dashed border-slate-700">
                {group.title}
              </h4>
              <ul className="space-y-2">
                {group.items.map((item, itemIdx) => (
                  <li key={itemIdx}>
                    <Link
                      href={item.href}
                      className="text-xs font-mono text-slate-400 hover:text-retro-orange transition-colors flex items-center gap-1.5"
                    >
                      <span className="text-retro-orange text-[10px]">›</span>
                      <span>{item.label}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Bar with Verification Assurance */}
        <div className="pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-slate-500">
          <div>{siteConfig.footer.copyright}</div>
          <div className="flex items-center gap-4">
            <span className="text-slate-400">VERIFIED VERCEL DEPLOYMENT</span>
            <a href="/robots.txt" className="hover:text-retro-orange">robots.txt</a>
            <a href="/sitemap.xml" className="hover:text-retro-orange">sitemap.xml</a>
          </div>
        </div>
      </div>
    </footer>
  );
}

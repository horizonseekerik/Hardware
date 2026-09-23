"use client";

import React, { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { siteConfig } from "@/site.config";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { PixelButton } from "@/components/ui/PixelButton";

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<number | null>(null);

  return (
    <header className="sticky top-0 z-50 w-full backdrop-blur-md bg-white/90 dark:bg-retro-darkBg/90 border-b-2 border-slate-200 dark:border-retro-darkBorder">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="relative w-9 h-9 border-2 border-retro-orange bg-retro-orange/10 pixel-corners flex items-center justify-center p-0.5 group-hover:scale-105 transition-transform">
            <Image
              src="/janus-logo.png"
              alt="Janus Logo"
              width={32}
              height={32}
              className="object-contain"
            />
          </div>
          <div>
            <div className="font-mono font-extrabold text-lg tracking-wider text-slate-950 dark:text-white flex items-center gap-1.5">
              <span>JANUS</span>
              <span className="text-[10px] px-1.5 py-0.2 bg-retro-orange text-white pixel-corners font-mono">
                INT64
              </span>
            </div>
            <div className="text-[10px] font-mono tracking-widest text-retro-orange uppercase">
              Photonic Hardware
            </div>
          </div>
        </Link>

        {/* Desktop Navigation & Mega-Menu Dropdown */}
        <nav className="hidden lg:flex items-center gap-1 xl:gap-2">
          {siteConfig.nav.megaMenu.map((category, idx) => (
            <div
              key={idx}
              className="relative"
              onMouseEnter={() => setActiveDropdown(idx)}
              onMouseLeave={() => setActiveDropdown(null)}
            >
              <button className="px-3 py-2 text-xs font-mono font-bold tracking-wider uppercase text-slate-700 dark:text-slate-300 hover:text-retro-orange flex items-center gap-1.5 transition-colors">
                <span>{category.title}</span>
                <span className="text-[9px] font-pixel text-retro-orange">▼</span>
              </button>

              {/* Dropdown panel */}
              {activeDropdown === idx && (
                <div className="absolute top-full left-0 w-80 p-3 bg-white dark:bg-retro-darkSurface border-2 border-slate-300 dark:border-retro-darkBorder pixel-corners shadow-pixel-dark animate-in fade-in duration-150">
                  <div className="space-y-2">
                    {category.items.map((item, itemIdx) => (
                      <Link
                        key={itemIdx}
                        href={item.href}
                        className="block p-2.5 hover:bg-slate-100 dark:hover:bg-retro-darkCard pixel-corners border border-transparent hover:border-retro-orange/40 transition-all group"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-xs font-bold text-slate-900 dark:text-slate-100 group-hover:text-retro-orange">
                            {item.label}
                          </span>
                          {item.badge && (
                            <span className="text-[9px] font-mono px-1.5 py-0.5 bg-retro-orange/20 text-retro-orange pixel-corners border border-retro-orange/40">
                              {item.badge}
                            </span>
                          )}
                        </div>
                        {item.description && (
                          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                            {item.description}
                          </p>
                        )}
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* Direct quick links */}
          {siteConfig.nav.directLinks.map((link, idx) => (
            <Link
              key={idx}
              href={link.href}
              className="px-3 py-2 text-xs font-mono font-bold tracking-wider uppercase text-slate-700 dark:text-slate-300 hover:text-retro-orange transition-colors"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Right Action Stack: Theme Toggle & PDF CTA */}
        <div className="hidden sm:flex items-center gap-3">
          <ThemeToggle />
          <PixelButton
            variant="primary"
            size="sm"
            href="/JANUS_IEEE_Manuscript.pdf"
          >
            Treatise (PDF)
          </PixelButton>
        </div>

        {/* Mobile Animated Pixel-Art Hamburger Icon */}
        <div className="flex items-center gap-2 lg:hidden">
          <ThemeToggle />
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle mobile menu"
            className="w-10 h-10 border-2 border-slate-300 dark:border-retro-darkBorder bg-slate-100 dark:bg-retro-darkSurface pixel-corners flex flex-col items-center justify-center gap-1 p-2 focus:outline-none"
          >
            <span
              className={`w-5 h-0.5 bg-retro-orange transition-transform duration-200 ${
                mobileMenuOpen ? "rotate-45 translate-y-1.5" : ""
              }`}
            />
            <span
              className={`w-5 h-0.5 bg-retro-orange transition-opacity duration-200 ${
                mobileMenuOpen ? "opacity-0" : ""
              }`}
            />
            <span
              className={`w-5 h-0.5 bg-retro-orange transition-transform duration-200 ${
                mobileMenuOpen ? "-rotate-45 -translate-y-1.5" : ""
              }`}
            />
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t-2 border-slate-200 dark:border-retro-darkBorder bg-white dark:bg-retro-darkSurface p-4 space-y-4 max-h-[85vh] overflow-y-auto">
          {siteConfig.nav.megaMenu.map((category, idx) => (
            <div key={idx} className="border-b border-dashed border-slate-300 dark:border-retro-darkBorder pb-3">
              <div className="text-xs font-mono font-extrabold text-retro-orange uppercase mb-2">
                {category.title}
              </div>
              <div className="space-y-1.5">
                {category.items.map((item, itemIdx) => (
                  <Link
                    key={itemIdx}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className="block py-1.5 px-2 text-xs font-mono text-slate-800 dark:text-slate-200 hover:text-retro-orange"
                  >
                    • {item.label} {item.badge && `[${item.badge}]`}
                  </Link>
                ))}
              </div>
            </div>
          ))}
          <div className="pt-2">
            <PixelButton
              variant="primary"
              size="md"
              href="/JANUS_IEEE_Manuscript.pdf"
              className="w-full"
            >
              DOWNLOAD TREATISE (PDF)
            </PixelButton>
          </div>
        </div>
      )}
    </header>
  );
}

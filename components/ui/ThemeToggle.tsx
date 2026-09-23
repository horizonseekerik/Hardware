"use client";

import React, { useEffect, useState } from "react";
import { useTheme } from "next-themes";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="h-8 w-20 bg-retro-darkBorder/40 pixel-corners animate-pulse" />
    );
  }

  const isDark = theme === "dark";

  return (
    <button
      onClick={() => setTheme(isDark ? "light" : "dark")}
      aria-label="Toggle retro color mode"
      className="relative inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-mono font-bold uppercase tracking-wider border-2 border-slate-300 dark:border-retro-darkBorder bg-white dark:bg-retro-darkSurface text-slate-800 dark:text-slate-200 pixel-corners hover:border-retro-orange transition-colors"
    >
      <span className="text-retro-orange">{isDark ? "🌙" : "☀️"}</span>
      <span>{isDark ? "DARK" : "LIGHT"}</span>
    </button>
  );
}

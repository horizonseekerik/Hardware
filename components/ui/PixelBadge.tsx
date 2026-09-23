import React from "react";

interface PixelBadgeProps {
  children: React.ReactNode;
  variant?: "orange" | "amber" | "green" | "cyan" | "muted";
  className?: string;
  icon?: string;
}

export function PixelBadge({
  children,
  variant = "orange",
  className = "",
  icon = "◆",
}: PixelBadgeProps) {
  const variantStyles = {
    orange: "bg-retro-orange/15 text-retro-orange border-retro-orange/50",
    amber: "bg-retro-amber/15 text-retro-amber border-retro-amber/50",
    green: "bg-retro-green/15 text-retro-green border-retro-green/50",
    cyan: "bg-retro-cyan/15 text-retro-cyan border-retro-cyan/50",
    muted: "bg-slate-800/40 text-slate-300 border-slate-700/60",
  }[variant];

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-mono font-bold uppercase tracking-wider border pixel-corners ${variantStyles} ${className}`}
    >
      <span className="text-[10px] leading-none opacity-80">{icon}</span>
      {children}
    </span>
  );
}

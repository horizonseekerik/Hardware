import React from "react";

interface PixelCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: "default" | "featured" | "dotted";
}

export function PixelCard({
  children,
  className = "",
  variant = "default",
}: PixelCardProps) {
  const variantStyles = {
    default: "bg-white dark:bg-retro-darkSurface border-2 border-slate-200 dark:border-retro-darkBorder shadow-pixel-dark",
    featured: "bg-white dark:bg-retro-darkCard border-2 border-retro-orange shadow-pixel-orange dark:shadow-pixel-orange",
    dotted: "bg-slate-50 dark:bg-retro-darkSurface/60 retro-border-dotted",
  }[variant];

  return (
    <div className={`p-6 pixel-corners transition-all duration-200 ${variantStyles} ${className}`}>
      {children}
    </div>
  );
}

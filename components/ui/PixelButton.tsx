import React from "react";

interface PixelButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "retro";
  size?: "sm" | "md" | "lg";
  asChild?: boolean;
  href?: string;
  icon?: React.ReactNode;
}

export function PixelButton({
  children,
  variant = "primary",
  size = "md",
  className = "",
  href,
  icon,
  ...props
}: PixelButtonProps) {
  const baseStyles = "relative inline-flex items-center justify-center font-mono font-bold uppercase tracking-wider transition-all duration-150 active:translate-y-0.5 active:translate-x-0.5";
  
  const sizeStyles = {
    sm: "px-3 py-1.5 text-xs gap-1.5",
    md: "px-5 py-2.5 text-sm gap-2",
    lg: "px-7 py-3.5 text-base gap-2.5",
  }[size];

  const variantStyles = {
    primary: "bg-retro-orange text-white hover:bg-retro-orangeHover shadow-pixel-dark dark:shadow-pixel-orange border-2 border-black dark:border-retro-orange",
    secondary: "bg-retro-darkSurface text-white hover:bg-retro-darkCard border-2 border-retro-darkBorder shadow-pixel-dark",
    outline: "bg-transparent text-retro-orange border-2 border-retro-orange hover:bg-retro-orange hover:text-white",
    retro: "bg-retro-amber text-black hover:bg-retro-yellow border-2 border-black shadow-pixel-dark",
  }[variant];

  const content = (
    <>
      {icon && <span className="flex-shrink-0">{icon}</span>}
      <span>{children}</span>
    </>
  );

  if (href) {
    return (
      <a
        href={href}
        className={`${baseStyles} ${sizeStyles} ${variantStyles} pixel-corners ${className}`}
      >
        {content}
      </a>
    );
  }

  return (
    <button
      className={`${baseStyles} ${sizeStyles} ${variantStyles} pixel-corners ${className}`}
      {...props}
    >
      {content}
    </button>
  );
}

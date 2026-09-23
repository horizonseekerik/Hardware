import React from "react";
import { Header } from "@/components/sections/Header";
import { HeroSection } from "@/components/sections/HeroSection";
import { QuickStats } from "@/components/sections/QuickStats";
import { CreatorsBand } from "@/components/sections/CreatorsBand";
import { FeatureTabs } from "@/components/sections/FeatureTabs";
import { BenefitsGrid } from "@/components/sections/BenefitsGrid";
import { BenchmarkChart } from "@/components/sections/BenchmarkChart";
import { TestimonialCarousel } from "@/components/sections/TestimonialCarousel";
import { UseCaseCards } from "@/components/sections/UseCaseCards";
import { PricingGrid } from "@/components/sections/PricingGrid";
import { FAQSection } from "@/components/sections/FAQSection";
import { FinalCTA } from "@/components/sections/FinalCTA";
import { Footer } from "@/components/sections/Footer";

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* 1. Sticky Header with Mega-Menu & Animated Pixel Hamburger */}
      <Header />

      <main className="flex-1">
        {/* 2. Hero Section with Word-by-Word Reveal & Pixel Field */}
        <HeroSection />

        {/* 3. Quick Stats with Clipped Slide-Up Counters */}
        <QuickStats />

        {/* 4. Creators Band with Interactive WebGL 3D Globe */}
        <CreatorsBand />

        {/* 5. Feature Tabs with Auto-Cycling & Pixel Reveal Transitions */}
        <FeatureTabs />

        {/* 6. Benefits Grid with Canvas-Rendered Pixel Icons */}
        <BenefitsGrid />

        {/* 7. Benchmark Chart with Tabbed Metric Switching */}
        <BenchmarkChart />

        {/* 8. Testimonial Carousel with Pixel-Notched Avatars */}
        <TestimonialCarousel />

        {/* 9. Use-Case Cards with Retro Badges */}
        <UseCaseCards />

        {/* 10. Pricing Grid with Featured Plan Highlight */}
        <PricingGrid />

        {/* 11. FAQ Section with Retro Dotted Borders */}
        <FAQSection />

        {/* 12. Final CTA Banner over 8-Bit WebGL Flame Shader */}
        <FinalCTA />
      </main>

      {/* 13. Footer with Reversed Pixel Field Backdrop & Newsletter Form */}
      <Footer />
    </div>
  );
}

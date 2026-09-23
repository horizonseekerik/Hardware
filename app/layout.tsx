import type { Metadata, Viewport } from "next";
import { siteConfig } from "@/site.config";
import { ThemeProvider } from "@/components/providers/ThemeProvider";
import { SmoothScrollProvider } from "@/components/providers/SmoothScroll";
import "./globals.css";

export const viewport: Viewport = {
  themeColor: "#FF5722",
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  title: `${siteConfig.name} | Spatial Optical Computing Architecture`,
  description: siteConfig.description,
  keywords: [
    "Janus",
    "Photonic Hardware",
    "Optical Computing",
    "Silicon Photonics",
    "RNS",
    "Sb2S3",
    "3D Heterogeneous CMOS",
    "Deep Learning Accelerator",
    "Spatial Residue",
    "INT64 Precision",
  ],
  authors: [{ name: "Horizon Seeker IK", url: siteConfig.url }],
  creator: "Horizon Seeker IK",
  publisher: "Project JANUS Research Group",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  openGraph: {
    type: "website",
    url: siteConfig.url,
    title: siteConfig.name,
    description: siteConfig.description,
    siteName: siteConfig.name,
    images: [
      {
        url: siteConfig.ogImage,
        width: 1200,
        height: 630,
        alt: "Project JANUS Photonic Hardware Architecture",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: siteConfig.name,
    description: siteConfig.description,
    images: [siteConfig.ogImage],
  },
  icons: {
    icon: [
      { url: "/favicon.ico" },
      { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
    ],
    apple: [{ url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" }],
  },
  manifest: "/manifest.json",
  // CRITICAL: Preserve all domain verification meta tags
  verification: {
    google: siteConfig.googleVerification,
  },
  other: {
    "google-site-verification": siteConfig.googleVerification,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning data-theme="dark">
      <head>
        {/* Explicit fallback meta tag for Google Search Console verification */}
        <meta
          name="google-site-verification"
          content={siteConfig.googleVerification}
        />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Inter:wght@400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />

        {/* VideoObject Schema.org JSON-LD for Google Video Search (Preserved from legacy site) */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "VideoObject",
              name: "Project JANUS: 3D Heterogeneous Photonic Accelerator Stack",
              description:
                "Exploded 3D physical architecture demonstration of Project JANUS Mini-16 Monolithic Photonic Accelerator showing the 250um microchannel lid, copper thermal matrix, silicon photonic stratum, and 65nm CMOS logic die.",
              thumbnailUrl: [
                "https://janus-photonic-hardware.vercel.app/janus_mini16_poster.jpg",
                "https://janus-photonic-hardware.vercel.app/og-image.png",
              ],
              uploadDate: "2026-09-04T00:00:00Z",
              duration: "PT10S",
              contentUrl:
                "https://janus-photonic-hardware.vercel.app/JANUS_Mini16_Demonstration.mp4",
              embedUrl: "https://janus-photonic-hardware.vercel.app/#features",
            }),
          }}
        />
      </head>
      <body className="min-h-screen font-sans bg-[#0a0a0c] text-white selection:bg-[#FF5722] selection:text-white">
        <ThemeProvider
          attribute="data-theme"
          defaultTheme="dark"
          enableSystem={false}
          disableTransitionOnChange
        >
          <SmoothScrollProvider>
            {children}
          </SmoothScrollProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}

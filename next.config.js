/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // Ensure PDFs and static documents from public/ have standard caching
  async headers() {
    return [
      {
        source: '/(.*)\\.pdf',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
          {
            key: 'Accept-Ranges',
            value: 'bytes',
          },
        ],
      },
    ];
  },
  webpack: (config) => {
    config.externals = [...(config.externals || [])];
    return config;
  },
};

module.exports = nextConfig;

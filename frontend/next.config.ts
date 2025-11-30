import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/trending/:path*',
        destination: 'http://localhost:8000/:path*',
      },
      {
        source: '/api/keywords/:path*',
        destination: 'http://localhost:7002/:path*',
      },
      {
        source: '/api/related/:path*',
        destination: 'http://localhost:7001/:path*',
      },
    ];
  },
};

export default nextConfig;

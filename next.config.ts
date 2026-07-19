import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  cacheComponents: true,
  allowedDevOrigins: ["192.168.1.77", "localhost:3000"],
};

export default nextConfig;

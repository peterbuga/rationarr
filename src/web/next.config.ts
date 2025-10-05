import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["localhost:3000", "localhost:8009"],
  outputFileTracingRoot: __dirname,
  // distDir: ".next",
  // eslint: {
  //   dirs: ["./src/web"],
  // },
  output: "export",
  turbopack: {
    root: path.join(__dirname, "../.."),
  },
  webpack(config) {
    config.resolve.alias["@"] = path.resolve(__dirname, ".");
    return config;
  },
  images: { unoptimized: true },
};

export default nextConfig;

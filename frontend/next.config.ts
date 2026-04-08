import type { NextConfig } from "next";
import path from "node:path";

const nextConfig: NextConfig = {
  // Prefer this app as Turbopack root when another package-lock exists higher in the tree (e.g. user home).
  turbopack: {
    root: path.resolve(process.cwd()),
  },
};

export default nextConfig;

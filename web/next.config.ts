import type { NextConfig } from "next";

// Local dev (and the two-project fallback): proxy /api/* to the FastAPI app so
// the browser only ever talks to one origin and the session cookie is first-party.
// On Vercel with Services, /api/* is routed to the Python service instead.
const apiOrigin = process.env.API_ORIGIN;

const nextConfig: NextConfig = {
  async rewrites() {
    return apiOrigin ? [{ source: "/api/:path*", destination: `${apiOrigin}/api/:path*` }] : [];
  },
};

export default nextConfig;

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone", // serveur Node autonome → image Docker légère
  async rewrites() {
    return [
      {
        source: "/api/django/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@homeguard/types', '@homeguard/utils'],
  images: {
    domains: ['localhost'],
  },
};

module.exports = nextConfig;
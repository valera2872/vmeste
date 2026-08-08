/** @type {import('next').NextConfig} */
const isGithubPages = process.env.GITHUB_ACTIONS === 'true';

const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  trailingSlash: true,
  basePath: isGithubPages ? '/vmeste' : '',
  assetPrefix: isGithubPages ? '/vmeste/' : '',
  images: {
    unoptimized: true,
  },
};

export default nextConfig;

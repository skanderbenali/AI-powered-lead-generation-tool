/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: [
      'localhost',
      'lh3.googleusercontent.com',   // Google profile pictures
      'avatars.githubusercontent.com', // GitHub profile pictures
      'github.com',
      'avatar-management--avatars.us-west-2.prod.public.atl-paas.net', // Atlassian
      'ui-avatars.com',  // UI Avatars service
      'gravatar.com',    // Gravatar
      'secure.gravatar.com',
      'images.unsplash.com',  // Unsplash
      's.gravatar.com',
      'source.unsplash.com',
      'cloudflare-ipfs.com', // IPFS Gateway
      'i.imgur.com',    // Imgur
    ],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  async redirects() {
    return [
      {
        source: '/',
        destination: '/dashboard',
        permanent: true,
      },
    ];
  },
};

module.exports = nextConfig;

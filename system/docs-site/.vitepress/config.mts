import { defineConfig } from 'vitepress';

export default defineConfig({
  title: 'Antigravity Brain',
  description: 'The PM Knowledge Management System — Documentation',
  base: '/',
  cleanUrls: true,
  appearance: 'dark',

  head: [
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    ['link', { href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap', rel: 'stylesheet' }],
  ],

  themeConfig: {
    logo: '⚛',
    siteTitle: 'Antigravity Brain',

    nav: [
      { text: 'Guide', link: '/guide/' },
      { text: 'Skills', link: '/skills/' },
      { text: 'Workflows', link: '/workflows/' },
      { text: 'Architecture', link: '/architecture/' },
    ],

    sidebar: {
      '/guide/': [
        {
          text: 'Getting Started',
          items: [
            { text: 'Introduction', link: '/guide/' },
            { text: 'Commands Reference', link: '/guide/commands' },
          ],
        },
      ],
      '/skills/': [
        {
          text: 'Skills',
          items: [
            { text: 'Index', link: '/skills/' },
          ],
        },
      ],
      '/workflows/': [
        {
          text: 'Workflows',
          items: [
            { text: 'Index', link: '/workflows/' },
          ],
        },
      ],
      '/architecture/': [
        {
          text: 'Architecture',
          items: [
            { text: 'Overview', link: '/architecture/' },
          ],
        },
      ],
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/nshofficial/beats-pm-antigravity-brain' },
    ],

    search: {
      provider: 'local',
    },

    footer: {
      message: 'Beats PM Antigravity Kit',
      copyright: '100% Local · Free Forever',
    },
  },
});

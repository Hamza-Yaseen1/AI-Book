import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/about',
    component: ComponentCreator('/about', 'ca4'),
    exact: true
  },
  {
    path: '/blog',
    component: ComponentCreator('/blog', 'b2f'),
    exact: true
  },
  {
    path: '/blog/archive',
    component: ComponentCreator('/blog/archive', '182'),
    exact: true
  },
  {
    path: '/blog/authors',
    component: ComponentCreator('/blog/authors', '0b7'),
    exact: true
  },
  {
    path: '/blog/authors/all-sebastien-lorber-articles',
    component: ComponentCreator('/blog/authors/all-sebastien-lorber-articles', '4a1'),
    exact: true
  },
  {
    path: '/blog/authors/yangshun',
    component: ComponentCreator('/blog/authors/yangshun', 'a68'),
    exact: true
  },
  {
    path: '/blog/first-blog-post',
    component: ComponentCreator('/blog/first-blog-post', '89a'),
    exact: true
  },
  {
    path: '/blog/long-blog-post',
    component: ComponentCreator('/blog/long-blog-post', '9ad'),
    exact: true
  },
  {
    path: '/blog/mdx-blog-post',
    component: ComponentCreator('/blog/mdx-blog-post', 'e9f'),
    exact: true
  },
  {
    path: '/blog/tags',
    component: ComponentCreator('/blog/tags', '287'),
    exact: true
  },
  {
    path: '/blog/tags/docusaurus',
    component: ComponentCreator('/blog/tags/docusaurus', '704'),
    exact: true
  },
  {
    path: '/blog/tags/facebook',
    component: ComponentCreator('/blog/tags/facebook', '858'),
    exact: true
  },
  {
    path: '/blog/tags/hello',
    component: ComponentCreator('/blog/tags/hello', '299'),
    exact: true
  },
  {
    path: '/blog/tags/hola',
    component: ComponentCreator('/blog/tags/hola', '00d'),
    exact: true
  },
  {
    path: '/blog/welcome',
    component: ComponentCreator('/blog/welcome', 'd2b'),
    exact: true
  },
  {
    path: '/markdown-page',
    component: ComponentCreator('/markdown-page', '3d7'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', 'a9c'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', 'c7e'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', 'aa0'),
            routes: [
              {
                path: '/docs/ch03-ml-physical-ai/ch03-lesson01/',
                component: ComponentCreator('/docs/ch03-ml-physical-ai/ch03-lesson01/', '7ca'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/ch03-ml-physical-ai/ch03-lesson02/',
                component: ComponentCreator('/docs/ch03-ml-physical-ai/ch03-lesson02/', 'd20'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/ch03-ml-physical-ai/ch03-lesson03/',
                component: ComponentCreator('/docs/ch03-ml-physical-ai/ch03-lesson03/', '417'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/ch04-physical-ai-applications/ch04-lesson01/',
                component: ComponentCreator('/docs/ch04-physical-ai-applications/ch04-lesson01/', '5f6'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/ch04-physical-ai-applications/ch04-lesson02/',
                component: ComponentCreator('/docs/ch04-physical-ai-applications/ch04-lesson02/', '0b6'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/ch04-physical-ai-applications/ch04-lesson03/',
                component: ComponentCreator('/docs/ch04-physical-ai-applications/ch04-lesson03/', '7c0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-1/lesson-1',
                component: ComponentCreator('/docs/chapter-1/lesson-1', '57c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-1/lesson-2',
                component: ComponentCreator('/docs/chapter-1/lesson-2', '83c'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-1/lesson-3',
                component: ComponentCreator('/docs/chapter-1/lesson-3', '852'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-2/lesson-1',
                component: ComponentCreator('/docs/chapter-2/lesson-1', '694'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-2/lesson-2',
                component: ComponentCreator('/docs/chapter-2/lesson-2', '663'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-2/lesson-3',
                component: ComponentCreator('/docs/chapter-2/lesson-3', '887'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/chapter-3/lesson-1',
                component: ComponentCreator('/docs/chapter-3/lesson-1', '8d3'),
                exact: true
              },
              {
                path: '/docs/chapter-3/lesson-2',
                component: ComponentCreator('/docs/chapter-3/lesson-2', '31c'),
                exact: true
              },
              {
                path: '/docs/chapter-3/lesson-3',
                component: ComponentCreator('/docs/chapter-3/lesson-3', '2ea'),
                exact: true
              },
              {
                path: '/docs/chapter-4/lesson-1',
                component: ComponentCreator('/docs/chapter-4/lesson-1', 'eaa'),
                exact: true
              },
              {
                path: '/docs/chapter-4/lesson-2',
                component: ComponentCreator('/docs/chapter-4/lesson-2', 'aca'),
                exact: true
              },
              {
                path: '/docs/chapter-4/lesson-3',
                component: ComponentCreator('/docs/chapter-4/lesson-3', '15d'),
                exact: true
              },
              {
                path: '/docs/hardware-compatibility',
                component: ComponentCreator('/docs/hardware-compatibility', '168'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/intro',
                component: ComponentCreator('/docs/intro', '61d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/troubleshooting',
                component: ComponentCreator('/docs/troubleshooting', 'e02'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tutorial-basics/congratulations',
                component: ComponentCreator('/docs/tutorial-basics/congratulations', '458'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tutorial-basics/create-a-blog-post',
                component: ComponentCreator('/docs/tutorial-basics/create-a-blog-post', '108'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tutorial-basics/create-a-document',
                component: ComponentCreator('/docs/tutorial-basics/create-a-document', '8fc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tutorial-basics/create-a-page',
                component: ComponentCreator('/docs/tutorial-basics/create-a-page', '951'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tutorial-basics/deploy-your-site',
                component: ComponentCreator('/docs/tutorial-basics/deploy-your-site', 'b91'),
                exact: true
              },
              {
                path: '/docs/tutorial-basics/markdown-features',
                component: ComponentCreator('/docs/tutorial-basics/markdown-features', 'b05'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tutorial-extras/manage-docs-versions',
                component: ComponentCreator('/docs/tutorial-extras/manage-docs-versions', '978'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tutorial-extras/translate-your-site',
                component: ComponentCreator('/docs/tutorial-extras/translate-your-site', 'f9a'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', 'e5f'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];

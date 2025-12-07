import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Chapter 1: Physical AI Fundamentals',
      items: [
        'chapter-1/lesson-1',
        'chapter-1/lesson-2',
        'chapter-1/lesson-3'
      ],
    },
    {
      type: 'category',
      label: 'Chapter 2: Advanced Physical AI Systems',
      items: [
        'chapter-2/lesson-1',
        'chapter-2/lesson-2',
        'chapter-2/lesson-3'
      ],
    },
    {
      type: 'category',
      label: 'Chapter 3: Machine Learning for Physical AI',
      items: [
        'ch03-ml-physical-ai/ch03-lesson01/index',
        'ch03-ml-physical-ai/ch03-lesson02/index',
        'ch03-ml-physical-ai/ch03-lesson03/index'
      ],
    },
    {
      type: 'category',
      label: 'Chapter 4: Real-World Physical AI Applications',
      items: [
        'ch04-physical-ai-applications/ch04-lesson01/index',
        'ch04-physical-ai-applications/ch04-lesson02/index',
        'ch04-physical-ai-applications/ch04-lesson03/index'
      ],
    },
    {
      type: 'category',
      label: 'Resources',
      items: [
        'troubleshooting',
        'hardware-compatibility'
      ],
    },
    {
      type: 'category',
      label: 'Tutorial',
      items: [
        'tutorial-basics/create-a-page',
        'tutorial-basics/create-a-document',
        'tutorial-basics/create-a-blog-post',
        'tutorial-basics/markdown-features',
        'tutorial-basics/congratulations',
      ],
    },
    {
      type: 'category',
      label: 'Additional Resources',
      items: [
        'tutorial-extras/manage-docs-versions',
        'tutorial-extras/translate-your-site',
      ],
    },
  ],

  // But you can create a sidebar manually
  /*
  tutorialSidebar: [
    'intro',
    'hello',
    {
      type: 'category',
      label: 'Tutorial',
      items: ['tutorial-basics/create-a-document'],
    },
  ],
   */
};

export default sidebars;

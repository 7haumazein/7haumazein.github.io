'use strict';

// Hexo does not create /index.html when a blog has no posts. Keep the
// homepage available so the banner and navigation still work before the
// first real article is published.
hexo.extend.generator.register('empty_home', function (locals) {
  if (locals.posts.length > 0) return;

  return [
    {
      path: 'index.html',
      layout: 'index',
      data: { posts: locals.posts }
    },
    {
      path: 'archives/index.html',
      layout: 'archive',
      data: { posts: locals.posts }
    }
  ];
});

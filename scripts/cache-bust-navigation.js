'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// A menu change must also refresh pages previously cached by the browser.
hexo.extend.filter.register('after_render:html', function (html) {
  const config = fs.readFileSync(path.join(hexo.base_dir, '_config.fluid.yml'));
  const version = crypto.createHash('sha256').update(config).digest('hex').slice(0, 12);

  return html.replace(/<header\b[\s\S]*?<\/header>/gi, function (header) {
    return header.replace(/(<a\b[^>]*\bhref=")(\/(?!\/)[^"?#]*\/|\/)(")/gi,
      function (_, prefix, url, suffix) {
        return prefix + url + '?nav=' + version + suffix;
      });
  });
});

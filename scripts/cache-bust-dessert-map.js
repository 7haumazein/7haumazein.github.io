'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const mapScript = path.join(hexo.source_dir, 'js', 'dessert-map-v2.js');

hexo.extend.filter.register('after_render:html', function (html) {
  if (!fs.existsSync(mapScript)) return html;

  const version = crypto
    .createHash('sha256')
    .update(fs.readFileSync(mapScript))
    .digest('hex')
    .slice(0, 12);

  return html.replace(
    /\/js\/dessert-map-v2\.js(?=["'])/g,
    `/js/dessert-map-v2.js?v=${version}`
  );
});

(function () {
  'use strict';

  var stores = [
    { name: 'PJ patisserie', coordinates: [39.8981, 116.4847], review: '我最常吃的一家，小蛋糕、大蛋糕和各种其他小点心都很能打，个人最喜欢焦糖金杏那一款了（嚼嚼嚼）（想吃拿破仑记得周末去）' },
    { name: 'Way°chib', coordinates: [39.9747, 116.5620], review: '芭菲和上新的神，店长是一款热爱尝试的，经常有事儿没事儿试试新品，产品更新巨快，我经常来不及去吃......而且现在疑似成为小半个网红店，有些热门甜品记得提前找她们预约（悲）' },
    { name: '老梦面包', coordinates: [39.9628, 116.4709], review: '神秘社区面包店，一定要吃咸派和苹果派（苹果派！一定！要蘸！香草酱！）' },
    { name: '文华饼店', coordinates: [39.9147, 116.4118], review: '高端这一块（但确实好吃）' },
    { name: '峪谷倉烘焙', coordinates: [40.0540, 116.5760], review: '强大的开酥实力......如果不是太远我真的会天天爽吃' },
    { name: 'LES MORILLES', coordinates: [39.9598, 116.4714], review: '饭店，但是法甜做的很nb，念念不忘他们的车厘子挞和草莓挞' },
    { name: 'leguan蛋糕', coordinates: [39.9657, 116.4215], review: '暂时相对冷门的一家，很喜欢小店装修，和柠檬挞' },
    { name: 'T-FOUR', coordinates: [39.9112, 116.4635], review: '不太喜欢歌剧院，但百香果慕斯很喜欢，热爱酸甜口' },
    { name: 'didilato', coordinates: [39.9400, 116.3913], review: '经典偏冷门小店，这家是冰淇淋专精，有时候会推出一些很神奇的口味，怪好玩的' },
    { name: 'pichoco', coordinates: [39.9270, 116.4126], review: '芭菲，好吃，其他没试过' },
    { name: 'Darling U', coordinates: [39.9254, 116.4113], review: '精品率很高的一家，吃过两次他家大蛋糕都很值' },
    { name: 'Lechouchoü', coordinates: [39.9213, 116.4621], review: '夏洛特......夏洛特......（嚼嚼嚼）（空气拿破仑也好吃）' },
    { name: 'L3mon ONE', coordinates: [39.9987, 116.4798], review: '柠檬专精，酸甜口爱好者不可错过的一家' },
    { name: 'CAPARESH', coordinates: [39.9092, 116.4611], review: '并非甜品店，但是他们的提拉米苏做的真的很好吃' }
  ];

  function escapeHtml(value) {
    return value.replace(/[&<>'"]/g, function (character) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character];
    });
  }

  function reviewCard(store) {
    return '<div class="dessert-review-card">' +
      '<div class="dessert-review-title">' + escapeHtml(store.name) + '</div>' +
      '<div class="dessert-review-body">' + escapeHtml(store.review) + '</div>' +
      '</div>';
  }

  function initializeMap() {
    var container = document.getElementById('dessert-map');
    var overlay = document.getElementById('dessert-review-overlay');
    var shell = container && container.parentElement;
    if (!container || !overlay || !shell || !window.L || container.dataset.initialized) return;

    container.dataset.initialized = 'true';

    var map = window.L.map(container, {
      scrollWheelZoom: true,
      zoomControl: true
    });

    window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var pin = window.L.divIcon({
      className: 'dessert-map-marker',
      html: '<div class="dessert-map-pin" aria-hidden="true"></div>',
      iconSize: [20, 20],
      iconAnchor: [10, 20],
      tooltipAnchor: [0, -19]
    });

    function hideReview() {
      overlay.classList.remove('is-visible', 'is-below');
    }

    function showReview(store) {
      var point = map.latLngToContainerPoint(store.coordinates);
      overlay.innerHTML = reviewCard(store);
      overlay.classList.remove('is-below');
      overlay.classList.add('is-visible');

      var halfWidth = overlay.offsetWidth / 2;
      var left = Math.max(halfWidth + 8, Math.min(point.x, shell.clientWidth - halfWidth - 8));
      overlay.style.left = left + 'px';
      overlay.style.top = (point.y - 20) + 'px';

      if (point.y - 20 - overlay.offsetHeight < 0) {
        overlay.classList.add('is-below');
        overlay.style.top = (point.y + 20) + 'px';
      }
    }

    var bounds = [];
    stores.forEach(function (store) {
      bounds.push(store.coordinates);
      var marker = window.L.marker(store.coordinates, { icon: pin, title: store.name })
        .addTo(map);

      marker.on('mouseover', function () {
        showReview(store);
      });
      marker.on('mouseout', hideReview);
      marker.on('click', function () {
        showReview(store);
      });
    });

    map.on('movestart', hideReview);
    map.fitBounds(bounds, { padding: [36, 36], maxZoom: 13 });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeMap);
  } else {
    initializeMap();
  }
})();

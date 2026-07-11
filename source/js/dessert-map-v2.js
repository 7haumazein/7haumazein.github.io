(function () {
  'use strict';

  var stores = [
    { name: 'PJ patisserie', coordinates: [39.8981, 116.4847] },
    { name: 'Way°chib', coordinates: [39.9747, 116.5620] },
    { name: '老梦面包', coordinates: [39.9628, 116.4709] },
    { name: '文华饼店', coordinates: [39.9147, 116.4118] },
    { name: '峪谷倉烘焙', coordinates: [40.0540, 116.5760] },
    { name: 'LES MORILLES', coordinates: [39.9598, 116.4714] },
    { name: 'leguan蛋糕', coordinates: [39.9657, 116.4215] },
    { name: 'T-FOUR', coordinates: [39.9112, 116.4635] },
    { name: 'didilato', coordinates: [39.9400, 116.3913] },
    { name: 'pichoco', coordinates: [39.9270, 116.4126] },
    { name: 'Darling U', coordinates: [39.9254, 116.4113] },
    { name: 'Lechouchoü', coordinates: [39.9213, 116.4621] },
    { name: 'L3mon ONE', coordinates: [39.9987, 116.4798] }
  ];

  function initializeMap() {
    var container = document.getElementById('dessert-map');
    if (!container || !window.L || container.dataset.initialized) return;

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

    var bounds = [];
    stores.forEach(function (store) {
      bounds.push(store.coordinates);
      window.L.marker(store.coordinates, { icon: pin, title: store.name })
        .addTo(map)
        .bindTooltip(store.name, {
          direction: 'top',
          opacity: 1,
          className: 'dessert-map-tooltip'
        });
    });

    map.fitBounds(bounds, { padding: [36, 36], maxZoom: 13 });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeMap);
  } else {
    initializeMap();
  }
})();

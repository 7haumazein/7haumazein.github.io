(function () {
  'use strict';

  function addMagicCircle(x, y) {
    var element = document.createElement('span');
    element.className = 'click-magic-circle';
    element.style.left = x + 'px';
    element.style.top = y + 'px';
    element.innerHTML = '<span aria-hidden="true"></span><span aria-hidden="true"></span><span aria-hidden="true"></span>';
    document.body.appendChild(element);
    window.setTimeout(function () {
      element.remove();
    }, 850);
  }

  document.addEventListener('click', function (event) {
    if (event.button !== 0 || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (event.target.closest('a, button, input, textarea, select, label, .leaflet-container')) return;

    addMagicCircle(event.clientX, event.clientY);
  });
})();

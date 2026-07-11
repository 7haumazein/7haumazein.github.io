(function () {
  'use strict';

  function addElement(className, x, y) {
    var element = document.createElement('span');
    element.className = className;
    element.style.left = x + 'px';
    element.style.top = y + 'px';
    document.body.appendChild(element);
    window.setTimeout(function () {
      element.remove();
    }, 700);
    return element;
  }

  document.addEventListener('click', function (event) {
    if (event.button !== 0 || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (event.target.closest('a, button, input, textarea, select, label, .leaflet-container')) return;

    addElement('click-effect-ring', event.clientX, event.clientY);

    [[-14, -10], [13, -9], [-9, 13], [12, 12]].forEach(function (offset) {
      var spark = addElement('click-effect-spark', event.clientX, event.clientY);
      spark.style.setProperty('--spark-x', offset[0] + 'px');
      spark.style.setProperty('--spark-y', offset[1] + 'px');
    });
  });
})();

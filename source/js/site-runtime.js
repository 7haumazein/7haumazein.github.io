(function () {
  'use strict';

  var birthTime = new Date('2026-07-10T16:30:36+08:00').getTime();

  function updateRuntime() {
    var element = document.getElementById('site-runtime');
    if (!element) return;

    var elapsed = Math.max(0, Math.floor((Date.now() - birthTime) / 1000));
    var days = Math.floor(elapsed / 86400);
    elapsed %= 86400;
    var hours = Math.floor(elapsed / 3600);
    elapsed %= 3600;
    var minutes = Math.floor(elapsed / 60);
    var seconds = elapsed % 60;

    element.textContent = '本站已运行 ' + days + ' 天 ' +
      String(hours).padStart(2, '0') + ' 时 ' +
      String(minutes).padStart(2, '0') + ' 分 ' +
      String(seconds).padStart(2, '0') + ' 秒';
  }

  updateRuntime();
  window.setInterval(updateRuntime, 1000);
})();

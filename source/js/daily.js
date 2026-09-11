(function () {
  'use strict';
  var root = document.querySelector('.daily-page');
  if (!root) return;
  var state = { report: 'close', window: 'all', live: 'gainers', index: null, reports: {}, latest: null };
  var $ = function (selector) { return root.querySelector(selector); };
  var escapeHtml = function (value) { return String(value == null ? '' : value).replace(/[&<>'"]/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[c]; }); };
  var pct = function (value) { return value == null ? '--' : (value > 0 ? '+' : '') + Number(value).toFixed(2) + '%'; };
  var place = function (row) { var city = row.city || row.province || ''; var key = ['江苏', '浙江', '上海', '武汉', '北京'].some(function (x) { return city.indexOf(x) >= 0; }); return '<span class="daily-place ' + (key ? 'is-focus' : '') + '">' + escapeHtml(city || '地域待补充') + '</span>'; };
  function table(rows, frequency) {
    if (!rows || !rows.length) return '<p class="daily-empty">暂无可用榜单。窗口积累中或数据源尚未连接。</p>';
    return '<div class="daily-scroll"><table><thead><tr><th>#</th><th>股票</th><th>行业</th><th>地域</th><th>' + (frequency ? '上榜率' : '涨跌幅') + '</th><th>' + (frequency ? '次数' : '成交额') + '</th></tr></thead><tbody>' + rows.map(function (row) { return '<tr><td>' + (row.rank || '--') + '</td><td><strong>' + escapeHtml(row.name || row.key) + '</strong><small>' + escapeHtml(row.code || row.key) + (row.st ? ' · ST' : '') + '</small></td><td>' + escapeHtml(row.industry || '待补充') + '</td><td>' + place(row) + '</td><td class="' + ((row.change_pct || 0) >= 0 ? 'is-up' : 'is-down') + '">' + (frequency ? (row.frequency_pct == null ? '--' : row.frequency_pct.toFixed(2) + '%') : pct(row.change_pct)) + '</td><td>' + (frequency ? (row.count || 0) + ' 次' : (row.amount ? Number(row.amount).toLocaleString() : '--')) + '</td></tr>'; }).join('') + '</tbody></table></div>';
  }
  function sectors(rows) { if (!rows || !rows.length) return '<span>行业统计待补充</span>'; return '<strong>行业前三：</strong> ' + rows.map(function (x) { return escapeHtml(x.industry) + ' ' + x.count + '只'; }).join(' · '); }
  function render() {
    var report = state.reports[state.report] || {};
    $('#report-heading').textContent = state.report === 'noon' ? '午间版' : '收盘版';
    $('#report-time').textContent = report.published_at ? '发布于 ' + report.published_at : '--';
    $('#daily-board').innerHTML = table(report.daily_gainers, false);
    $('#frequency-board').innerHTML = table(state.window === 'afternoon' ? report.frequency_afternoon : report.frequency_all, true);
    $('#daily-sectors').innerHTML = sectors(report.daily_sectors);
    $('#frequency-sectors').innerHTML = sectors(state.window === 'afternoon' ? report.frequency_sectors_afternoon : report.frequency_sectors_all);
    $('#sector-explanations').innerHTML = (report.sector_explanations || []).map(function (x) { return '<article><strong>' + escapeHtml(x.industry) + '</strong><span>' + escapeHtml(x.status || '待补充资料') + '</span></article>'; }).join('') || '<p class="daily-empty">未配置解释任务；基础统计仍可独立使用。</p>';
    var liveRows = state.live === 'daily' ? state.latest.daily_gainers : state.live === 'decliners' ? state.latest.five_minute_decliners : state.latest.five_minute_gainers;
    $('#live-board').innerHTML = table(liveRows, false);
    $('#live-time').textContent = state.latest.quote_time ? '行情 ' + state.latest.quote_time : '--';
  }
  function loadJson(url) { return fetch(url, { headers: { Accept: 'application/json' } }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }); }
  function load() {
    var api = root.getAttribute('data-daily-api');
    return Promise.all([loadJson(api + '/reports/index.json'), loadJson(api + '/latest.json')]).then(function (items) { state.index = items[0]; state.latest = items[1]; return (state.index.reports || []).reduce(function (chain, item) { return chain.then(function () { return loadJson(api + '/reports/' + item.date + '/' + item.type + '.json').then(function (report) { if (!state.reports[item.type]) state.reports[item.type] = report; }); }); }, Promise.resolve()); }).then(function () { $('#daily-state').textContent = state.latest.status || '数据已更新'; $('#daily-state').dataset.state = state.latest.quality === 'stale' ? 'stale' : 'online'; $('#daily-meta').textContent = '北京时间 · 数据源：' + (state.latest.provider || '未配置') + ' · 覆盖率：' + (state.latest.coverage_pct == null ? '--' : state.latest.coverage_pct + '%'); render(); }).catch(function () { $('#daily-state').textContent = '尚未连接实时数据源'; $('#daily-state').dataset.state = 'offline'; $('#daily-meta').textContent = '本地页面已就绪；请先配置外部只读数据发布，再显示实时行情。'; $('#daily-message').hidden = false; $('#daily-message').textContent = '数据源验证尚未完成，当前不展示模拟行情。'; });
  }
  root.addEventListener('click', function (event) { var button = event.target.closest('button'); if (!button) return; if (button.dataset.report) { state.report = button.dataset.report; root.querySelectorAll('[data-report]').forEach(function (x) { x.classList.toggle('is-active', x === button); }); render(); } if (button.dataset.window) { state.window = button.dataset.window; root.querySelectorAll('[data-window]').forEach(function (x) { x.classList.toggle('is-active', x === button); }); render(); } if (button.dataset.liveBoard) { state.live = button.dataset.liveBoard; root.querySelectorAll('[data-live-board]').forEach(function (x) { x.classList.toggle('is-active', x === button); }); render(); } });
  load();
}());

---
title: A股日报
layout: page
subtitle: 行情观察与资料整理
banner_img: /img/archive-banner.png
banner_img_height: 60
---

<div class="daily-page" data-daily-api="/daily-data">
  <section class="daily-status" aria-labelledby="daily-heading">
    <div>
      <p class="daily-eyebrow">A-SHARE DAILY</p>
      <h2 id="daily-heading">A股日报</h2>
      <p class="daily-muted">用于行情观察与资料整理，不构成投资建议。</p>
    </div>
    <div id="daily-state" class="daily-state" data-state="offline">尚未连接实时数据源</div>
  </section>

  <section class="daily-toolbar" aria-label="日报筛选">
    <label>报告日期 <select id="daily-date"><option value="">最新可用</option></select></label>
    <div class="daily-segmented" role="group" aria-label="报告版本">
      <button type="button" class="is-active" data-report="close">收盘版</button>
      <button type="button" data-report="noon">午间版</button>
    </div>
    <div class="daily-segmented" role="group" aria-label="五分钟统计范围">
      <button type="button" class="is-active" data-window="all">全天</button>
      <button type="button" data-window="afternoon">仅下午</button>
    </div>
  </section>

  <div id="daily-meta" class="daily-meta" aria-live="polite">正在读取报告索引...</div>
  <div id="daily-message" class="daily-message" hidden></div>

  <section class="daily-live-panel">
    <div class="daily-section-heading"><h3>实时榜单</h3><span id="live-time">--</span></div>
    <div class="daily-segmented daily-live-tabs" role="group" aria-label="实时榜单类型">
      <button type="button" class="is-active" data-live-board="gainers">五分钟涨幅</button>
      <button type="button" data-live-board="decliners">五分钟跌幅</button>
      <button type="button" data-live-board="daily">当日涨幅</button>
    </div>
    <div id="live-board" class="daily-table-wrap"></div>
  </section>

  <section class="daily-reports">
    <div class="daily-section-heading"><h3 id="report-heading">收盘版</h3><span id="report-time">--</span></div>
    <div class="daily-report-grid">
      <article class="daily-report-card"><h4>A榜 · 当日涨幅前30</h4><div id="daily-board"></div><div id="daily-sectors" class="daily-sectors"></div></article>
      <article class="daily-report-card"><h4>B榜 · 五分钟高频前30</h4><div id="frequency-board"></div><div id="frequency-sectors" class="daily-sectors"></div></article>
    </div>
  </section>

  <section class="daily-explanations"><div class="daily-section-heading"><h3>综合前五板块</h3><span>解释任务可选</span></div><div id="sector-explanations" class="daily-explanation-list"></div></section>
</div>

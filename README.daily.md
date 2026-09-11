# A 股日报首版

日报页面位于 `/daily/`，导航入口在“关于”下。页面和采集器默认不包含模拟行情。

## 本地验证

1. 安装 Python 3.11+（采集器仅使用标准库）。
2. 准备一份不含凭据的行情导出 JSON/CSV，字段至少为 `exchange,code,name,price,prev_close`，可选 `amount,quote_time,industry,province,city,status,st`。
3. 运行 `python -m collector.cli probe path/to/export.csv`，检查解析和确定性榜单。
4. 将真实采样组装为 `collector.report.build_report(...)`，使用 `collector.publish.publish_report(...)` 原子发布到只读数据目录。
5. 将该数据目录映射为博客页面的 `/daily-data/`；页面会读取 `latest.json` 和 `reports/index.json`。

## 当前边界

通达信正式接口、实时行情服务、公司资料/公告源尚未在本机验证，因此没有启动常驻采集循环，也没有声称分钟级公网实时已完成。`FileQuoteProvider` 只用于验证用户导出格式。模型解释默认关闭，后续可在不改统计代码的前提下增加适配器。

已实际发现一个可在通达信关闭后读取报价的公开端点，并保留为候选备用源；它还没有通过全市场覆盖、连续采样和展示许可验收，不能直接作为生产源。

本机通达信验证和低负载运行步骤见 [`docs/local-tdx-runbook.md`](docs/local-tdx-runbook.md)。

自动更新方案：GitHub Actions 每 5 分钟调用独立公开行情源，在构建时生成
`public/daily-data` 并发布到 Pages；不需要本机启动通达信。公开接口属于尽力而为，
若失败页面会显示数据源不可用。GitHub Actions 可能延迟调度，不能承诺严格每分钟更新。

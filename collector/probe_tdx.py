"""Read-only probe of the TQ interface bundled with the installed terminal.

Uses the terminal's existing login; never accepts account credentials.
Run: py -m collector.probe_tdx
"""
import argparse
import importlib
import json
from pathlib import Path
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--terminal', default=r'C:\new_tdx64')
    parser.add_argument('--code', default='000001.SZ')
    parser.add_argument('--benchmark', type=int, default=0,
                        help='Read up to N A-share snapshots after one cache refresh')
    args = parser.parse_args()
    sdk = Path(args.terminal).resolve() / 'PYPlugins' / 'sys'
    if not (sdk / 'tqcenter.py').is_file():
        raise SystemExit('Terminal TQ SDK not found')
    sys.path.insert(0, str(sdk))
    tq = importlib.import_module('tqcenter').tq
    started = time.monotonic()
    try:
        try:
            tq.initialize(str(Path(__file__).resolve()))
        except Exception as exc:
            raise SystemExit(
                "无法连接通达信 TQ 行情接口。请先启动 C:\\new_tdx64\\TdxW.exe，"
                "完成登录并打开行情后重试；本程序只读取行情，不会代下单。"
                f" 原始错误: {exc}"
            ) from exc
        if args.benchmark:
            stocks = tq.get_stock_list('5', list_type=0)
            print(json.dumps({'universe_count': len(stocks), 'sample': stocks[:3]}, ensure_ascii=False), flush=True)
            codes = [s for s in stocks if isinstance(s, str) and s.endswith(('.SH', '.SZ', '.BJ'))]
            if not codes:
                raise SystemExit('Unexpected stock-list shape; inspect before proceeding')
            refresh_start = time.monotonic()
            refresh = tq.refresh_cache(market='AG', force=True)
            print(json.dumps({'refresh': refresh, 'refresh_seconds': round(time.monotonic()-refresh_start, 3)}), flush=True)
            errors, sample, elapsed = 0, [], []
            for code in codes[:min(args.benchmark, 6000)]:
                tick_start = time.monotonic()
                result = tq.get_market_snapshot(stock_code=code, field_list=[])
                elapsed.append(time.monotonic()-tick_start)
                errors += int(not result or result.get('ErrorId') != '0')
                if len(sample) < 3:
                    sample.append({'code': code, 'result': result})
                if time.monotonic()-refresh_start > 45:
                    break
            print(json.dumps({'read_count': len(elapsed), 'errors': errors,
                              'read_seconds': round(sum(elapsed), 3),
                              'elapsed_seconds': round(time.monotonic()-started, 3),
                              'sample': sample}, ensure_ascii=False), flush=True)
            return
        result = tq.get_market_snapshot(stock_code=args.code, field_list=[])
        print(json.dumps({'probe': 'read-only snapshot', 'code': args.code,
                          'elapsed_seconds': round(time.monotonic() - started, 3),
                          'result': result}, ensure_ascii=False, default=str))
    finally:
        tq.close()


if __name__ == '__main__':
    main()

"""Small public quote adapter for Tencent's quote endpoint.

This adapter is a candidate fallback, not a claim of guaranteed availability or
redistribution rights. It is intentionally separate from the TDX provider.
"""
import re
import urllib.request
from datetime import datetime
from .models import Quote


class TencentQuoteProvider:
    name = "tencent-public-candidate"

    def __init__(self, timeout=10):
        self.timeout = timeout

    def snapshot(self, codes):
        symbols = []
        for code in codes:
            exchange, number = code.upper().replace('.', '').split(':')[-1].split()[-1], None
            match = re.match(r'^(SH|SZ|BJ)(\d{6})$', code.upper().replace('.', ''))
            if not match:
                continue
            symbols.append(match.group(1).lower() + match.group(2))
        if not symbols:
            return []
        url = 'https://qt.gtimg.cn/q=' + ','.join(symbols)
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        text = urllib.request.urlopen(request, timeout=self.timeout).read().decode('gb18030', errors='replace')
        result = []
        for line in text.splitlines():
            match = re.search(r'v_(?:sh|sz|bj)(\d{6})="(.*)";', line)
            if not match:
                continue
            fields = match.group(2).split('~')
            if len(fields) < 32:
                continue
            prefix = line.split('v_')[1][:2].upper()
            quote_time = None
            if fields[30].isdigit() and len(fields[30]) == 14:
                quote_time = datetime.strptime(fields[30], '%Y%m%d%H%M%S')
            result.append(Quote(prefix, match.group(1), fields[1], float(fields[3]) if fields[3] else None,
                                float(fields[4]) if fields[4] else None,
                                amount=float(fields[37]) if len(fields) > 37 and fields[37] else None,
                                quote_time=quote_time, status='normal'))
        return result

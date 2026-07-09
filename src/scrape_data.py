"""
快速数据爬取脚本 - 获取热门股票数据
使用Tushare免费接口，无需token
"""
import tushare as ts
import pandas as pd
import os
import time

# 热门股票列表（精选100只）
STOCK_LIST = [
    # 沪市主板
    '600000.SH', '600016.SH', '600019.SH', '600028.SH', '600030.SH',
    '600036.SH', '600048.SH', '600050.SH', '600104.SH', '600109.SH',
    '600111.SH', '600309.SH', '600519.SH', '600547.SH', '600570.SH',
    '600585.SH', '600690.SH', '600745.SH', '600837.SH', '600887.SH',
    '601012.SH', '601088.SH', '601166.SH', '601288.SH', '601318.SH',
    '601398.SH', '601628.SH', '601668.SH', '601688.SH', '601818.SH',
    '601857.SH', '601888.SH', '601899.SH', '601988.SH', '603259.SH',
    '603288.SH', '603501.SH', '603986.SH',

    # 深市主板
    '000001.SZ', '000002.SZ', '000063.SZ', '000066.SZ', '000069.SZ',
    '000100.SZ', '000157.SZ', '000166.SZ', '000333.SZ', '000338.SZ',
    '000402.SZ', '000425.SZ', '000538.SZ', '000568.SZ', '000625.SZ',
    '000651.SZ', '000661.SZ', '000725.SZ', '000768.SZ', '000776.SZ',
    '000858.SZ', '000876.SZ', '000895.SZ', '000938.SZ', '001979.SZ',

    # 创业板
    '300003.SZ', '300015.SZ', '300033.SZ', '300059.SZ', '300122.SZ',
    '300124.SZ', '300142.SZ', '300144.SZ', '300347.SZ', '300408.SZ',
    '300433.SZ', '300498.SZ', '300595.SZ', '300750.SZ', '300760.SZ',

    # 科创板
    '688009.SH', '688012.SH', '688036.SH', '688111.SH', '688126.SH',
    '688169.SH', '688187.SH', '688223.SH', '688303.SH', '688396.SH',
    '688561.SH', '688599.SH', '688981.SH',

    # 北交所
    '430047.BJ', '430090.BJ', '430139.BJ', '430198.BJ', '430510.BJ',
]

def scrape_stock_data(ts_code, start_date='20240101', end_date='20251231'):
    """
    爬取单只股票数据
    """
    try:
        print(f"正在获取 {ts_code} 的数据...", end=' ')

        # 使用免费接口
        code = ts_code.split('.')[0]

        # 获取历史数据
        df = ts.get_hist_data(code, start=start_date, end=end_date)

        if df is None or len(df) == 0:
            print("❌ 无数据")
            return False

        # 转换格式
        df = df.reset_index()
        df = df.rename(columns={
            'date': 'trade_date',
            'open': 'open',
            'high': 'high',
            'close': 'close',
            'low': 'low',
            'volume': 'vol',
            'price_change': 'change',
            'p_change': 'pct_chg',
            'ma5': 'ma5',
            'ma10': 'ma10',
            'ma20': 'ma20',
            'turnover': 'amount'
        })

        # 添加股票代码
        df['ts_code'] = ts_code

        # 转换日期格式
        df['trade_date'] = pd.to_datetime(df['trade_date']).dt.strftime('%Y%m%d')

        # 选择需要的列
        columns = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close',
                   'vol', 'amount', 'change', 'pct_chg']
        df = df[columns]

        # 保存到CSV
        data_dir = '../data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        filename = os.path.join(data_dir, f"{ts_code.replace('.', '_')}.csv")
        df.to_csv(filename, index=False, encoding='utf-8')

        print(f"✅ 成功 ({len(df)}条)")
        return True

    except Exception as e:
        print(f"❌ 失败: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("  📊 股票数据爬取工具")
    print("=" * 60)
    print()

    # 选择要爬取的股票数量
    print(f"可用股票总数: {len(STOCK_LIST)}")
    print()

    choice = input("选择爬取数量 (1=10只, 2=50只, 3=全部): ").strip()

    if choice == '1':
        stocks = STOCK_LIST[:10]
    elif choice == '2':
        stocks = STOCK_LIST[:50]
    else:
        stocks = STOCK_LIST

    print()
    print(f"开始爬取 {len(stocks)} 只股票...")
    print("-" * 60)

    success_count = 0
    fail_count = 0

    for i, ts_code in enumerate(stocks, 1):
        print(f"[{i}/{len(stocks)}] ", end='')

        if scrape_stock_data(ts_code):
            success_count += 1
        else:
            fail_count += 1

        # 避免请求过快
        time.sleep(0.5)

    print("-" * 60)
    print()
    print("=" * 60)
    print("  📋 爬取结果统计")
    print("=" * 60)
    print(f"成功: {success_count} 只")
    print(f"失败: {fail_count} 只")
    print(f"总计: {len(stocks)} 只")
    print()
    print(f"数据保存在: ../data/ 目录")
    print("=" * 60)

if __name__ == '__main__':
    main()

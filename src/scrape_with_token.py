"""
使用Tushare Pro API爬取股票数据
Token已配置
"""
import tushare as ts
import pandas as pd
import os
import time

# 设置Token
TOKEN = '841095bf49816d41b05db1dadf2b0840462fb9df1d76bdfe295a239f'
ts.set_token(TOKEN)
pro = ts.pro_api()

# 热门股票列表
STOCK_LIST = [
    '600000.SH',  # 浦发银行
    '600016.SH',  # 民生银行
    '600036.SH',  # 招商银行
    '600519.SH',  # 贵州茅台
    '601318.SH',  # 中国平安
    '000001.SZ',  # 平安银行
    '000002.SZ',  # 万科A
    '000066.SZ',  # 中国长城
    '000333.SZ',  # 美的集团
    '300750.SZ',  # 宁德时代
]

def scrape_stock_data(ts_code, start_date='20240101', end_date='20251231'):
    """
    使用Tushare Pro API爬取股票数据
    """
    try:
        print(f"正在获取 {ts_code} 的数据...", end=' ')

        # 获取日线数据
        df = pro.daily(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date
        )

        if df is None or len(df) == 0:
            print("❌ 无数据")
            return False

        # 按日期排序
        df = df.sort_values('trade_date')

        # 保存到CSV
        data_dir = '../data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        filename = os.path.join(data_dir, f"{ts_code.replace('.', '_')}.csv")
        df.to_csv(filename, index=False, encoding='utf-8')

        # 获取日期范围
        min_date = df['trade_date'].min()
        max_date = df['trade_date'].max()

        print(f"✅ 成功 ({len(df)}条, {min_date}-{max_date})")
        return True

    except Exception as e:
        print(f"❌ 失败: {str(e)}")
        return False

def main():
    print("=" * 70)
    print("  📊 Tushare Pro 数据爬取工具")
    print("=" * 70)
    print()
    print(f"Token: {TOKEN[:20]}...")
    print(f"时间范围: 2024-01-01 至 2025-12-31")
    print(f"股票数量: {len(STOCK_LIST)} 只")
    print()
    print("-" * 70)

    success_count = 0
    fail_count = 0

    for i, ts_code in enumerate(STOCK_LIST, 1):
        print(f"[{i}/{len(STOCK_LIST)}] ", end='')

        if scrape_stock_data(ts_code):
            success_count += 1
        else:
            fail_count += 1

        # API限速：每分钟200次，延时0.5秒
        time.sleep(0.5)

    print("-" * 70)
    print()
    print("=" * 70)
    print("  📋 爬取结果统计")
    print("=" * 70)
    print(f"✅ 成功: {success_count} 只")
    print(f"❌ 失败: {fail_count} 只")
    print(f"📊 总计: {len(STOCK_LIST)} 只")
    print()
    print(f"💾 数据保存在: ../data/ 目录")
    print("=" * 70)

if __name__ == '__main__':
    main()

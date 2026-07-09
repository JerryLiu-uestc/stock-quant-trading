"""
Tushare数据爬取模块
使用Tushare API获取股票交易数据
"""
import tushare as ts
import pandas as pd
import os
from datetime import datetime
import time


class TushareDataScraper:
    def __init__(self, token=None):
        """
        初始化Tushare数据爬取器

        Args:
            token: Tushare API token (可从 https://tushare.pro 注册获取)
        """
        self.token = token
        if token:
            ts.set_token(token)
            self.pro = ts.pro_api()
        else:
            # 使用免费接口（功能有限）
            self.pro = None

        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def get_stock_list(self, market='主板'):
        """
        获取股票列表

        Args:
            market: 市场类型 ('主板', '中小板', '创业板')

        Returns:
            DataFrame: 股票列表
        """
        try:
            if self.pro:
                # 使用Pro接口
                stock_list = self.pro.stock_basic(
                    exchange='',
                    list_status='L',
                    fields='ts_code,symbol,name,area,industry,market,list_date'
                )
                return stock_list
            else:
                # 使用免费接口
                stock_list = ts.get_stock_basics()
                return stock_list
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return None

    def get_stock_data(self, ts_code, start_date='20240101', end_date='20251231'):
        """
        获取单只股票的交易数据

        Args:
            ts_code: 股票代码 (如 '000001.SZ')
            start_date: 开始日期 (格式: '20240101')
            end_date: 结束日期 (格式: '20251231')

        Returns:
            DataFrame: 股票交易数据
        """
        try:
            if self.pro:
                # 使用Pro接口获取日线数据
                df = self.pro.daily(
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=end_date
                )
            else:
                # 使用免费接口
                code = ts_code.split('.')[0]
                df = ts.get_k_data(
                    code,
                    start=f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}",
                    end=f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
                )

            if df is not None and len(df) > 0:
                return df
            else:
                print(f"股票 {ts_code} 无数据")
                return None

        except Exception as e:
            print(f"获取股票 {ts_code} 数据失败: {e}")
            return None

    def save_stock_data(self, ts_code, df, stock_name=None):
        """
        保存股票数据到CSV文件

        Args:
            ts_code: 股票代码
            df: 股票数据DataFrame
            stock_name: 股票名称（可选）
        """
        try:
            if stock_name:
                filename = f"{ts_code}_{stock_name}.csv"
            else:
                filename = f"{ts_code}.csv"

            filepath = os.path.join(self.data_dir, filename)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"✓ 保存成功: {filename} ({len(df)} 条数据)")
            return True
        except Exception as e:
            print(f"✗ 保存失败 {ts_code}: {e}")
            return False

    def scrape_multiple_stocks(self, stock_codes, start_date='20240101', end_date='20251231', delay=0.5):
        """
        批量爬取多只股票数据

        Args:
            stock_codes: 股票代码列表 (如 ['000001.SZ', '000002.SZ'])
            start_date: 开始日期
            end_date: 结束日期
            delay: 每次请求间隔（秒），避免触发API限制

        Returns:
            dict: 成功和失败的统计信息
        """
        total = len(stock_codes)
        success = 0
        failed = 0

        print(f"\n开始爬取 {total} 只股票的数据...")
        print(f"时间范围: {start_date} 至 {end_date}")
        print("=" * 60)

        for i, ts_code in enumerate(stock_codes, 1):
            print(f"\n[{i}/{total}] 正在爬取: {ts_code}")

            # 获取数据
            df = self.get_stock_data(ts_code, start_date, end_date)

            if df is not None and len(df) > 0:
                # 保存数据
                if self.save_stock_data(ts_code, df):
                    success += 1
                else:
                    failed += 1
            else:
                print(f"✗ 无数据或获取失败: {ts_code}")
                failed += 1

            # 延迟，避免请求过快
            if i < total:
                time.sleep(delay)

        print("\n" + "=" * 60)
        print(f"爬取完成！成功: {success}, 失败: {failed}")
        print(f"数据保存目录: {self.data_dir}")

        return {"success": success, "failed": failed, "total": total}

    def get_popular_stocks(self, count=100):
        """
        获取热门股票代码列表

        Args:
            count: 需要获取的股票数量

        Returns:
            list: 股票代码列表
        """
        # 一些常见的股票代码（示例）
        # 实际使用时应该从股票列表中筛选
        popular_stocks = [
            # 沪市主板
            '600000.SH', '600019.SH', '600028.SH', '600029.SH', '600030.SH',
            '600036.SH', '600048.SH', '600050.SH', '600104.SH', '600109.SH',
            '600196.SH', '600276.SH', '600309.SH', '600519.SH', '600570.SH',
            '600584.SH', '600585.SH', '600588.SH', '600690.SH', '600703.SH',
            '600837.SH', '600887.SH', '600900.SH', '600919.SH', '601012.SH',
            '601088.SH', '601166.SH', '601169.SH', '601288.SH', '601318.SH',
            '601328.SH', '601398.SH', '601601.SH', '601628.SH', '601668.SH',
            '601688.SH', '601818.SH', '601857.SH', '601888.SH', '601899.SH',

            # 深市主板
            '000001.SZ', '000002.SZ', '000063.SZ', '000066.SZ', '000100.SZ',
            '000333.SZ', '000338.SZ', '000402.SZ', '000425.SZ', '000538.SZ',
            '000568.SZ', '000625.SZ', '000651.SZ', '000858.SZ', '000876.SZ',
            '000895.SZ', '000938.SZ', '001979.SZ', '002001.SZ', '002027.SZ',
            '002050.SZ', '002142.SZ', '002230.SZ', '002236.SZ', '002241.SZ',
            '002271.SZ', '002304.SZ', '002352.SZ', '002371.SZ', '002415.SZ',
            '002460.SZ', '002475.SZ', '002493.SZ', '002594.SZ', '002601.SZ',
            '002602.SZ', '002648.SZ', '002714.SZ', '002736.SZ', '002938.SZ',

            # 创业板
            '300003.SZ', '300014.SZ', '300015.SZ', '300033.SZ', '300059.SZ',
            '300122.SZ', '300124.SZ', '300142.SZ', '300144.SZ', '300207.SZ',
            '300274.SZ', '300347.SZ', '300408.SZ', '300413.SZ', '300433.SZ',
            '300498.SZ', '300502.SZ', '300568.SZ', '300595.SZ', '300750.SZ',
        ]

        return popular_stocks[:count]


def main():
    """主函数 - 演示如何使用"""
    print("=" * 60)
    print("Tushare 股票数据爬取工具")
    print("=" * 60)

    # 提示用户输入token
    print("\n请先在 https://tushare.pro 注册并获取token")
    print("如果没有token，可以使用免费接口（功能有限）\n")

    token = input("请输入您的Tushare token (直接回车跳过): ").strip()

    if not token:
        token = None
        print("\n使用免费接口模式")

    # 创建爬取器
    scraper = TushareDataScraper(token)

    # 选择爬取模式
    print("\n请选择爬取模式:")
    print("1. 爬取单只股票")
    print("2. 批量爬取100只热门股票")
    print("3. 自定义股票列表")

    choice = input("\n请输入选项 (1/2/3): ").strip()

    if choice == '1':
        # 单只股票
        ts_code = input("请输入股票代码 (如 000066.SZ): ").strip()
        df = scraper.get_stock_data(ts_code)
        if df is not None:
            scraper.save_stock_data(ts_code, df)

    elif choice == '2':
        # 批量爬取
        stocks = scraper.get_popular_stocks(100)
        scraper.scrape_multiple_stocks(stocks)

    elif choice == '3':
        # 自定义列表
        print("\n请输入股票代码，用逗号分隔 (如: 000066.SZ,600000.SH)")
        codes_input = input("股票代码: ").strip()
        stocks = [code.strip() for code in codes_input.split(',')]
        scraper.scrape_multiple_stocks(stocks)

    else:
        print("无效选项")

    print("\n爬取任务完成！")


if __name__ == "__main__":
    main()

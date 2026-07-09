"""
数据清理工具 - 修复CSV文件格式
"""
import pandas as pd
import os

def clean_csv_file(input_file, output_file):
    """清理CSV文件，确保格式正确"""
    print(f"处理文件: {input_file}")

    try:
        # 读取CSV，跳过中文表头行
        df = pd.read_csv(input_file, encoding='gbk', skiprows=1)

        # 重命名列为英文（与Tushare标准一致）
        df.columns = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close',
                      'pre_close', 'change', 'pct_chg', 'vol', 'amount']

        # 保存为标准格式
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"✓ 清理完成: {output_file}")
        print(f"  数据行数: {len(df)}")
        print(f"  日期范围: {df['trade_date'].min()} 至 {df['trade_date'].max()}")

        return True

    except Exception as e:
        print(f"✗ 处理失败: {e}")
        return False


def main():
    print("=" * 60)
    print("CSV数据清理工具")
    print("=" * 60)

    # 处理raw目录中的文件
    input_file = 'raw/中国长城.中文标识.csv'
    output_file = 'data/000066.SZ_中国长城.csv'

    if os.path.exists(input_file):
        clean_csv_file(input_file, output_file)
        print(f"\n清理后的文件保存在: {output_file}")
    else:
        print(f"找不到文件: {input_file}")

    print("=" * 60)


if __name__ == "__main__":
    main()

"""
股票量化交易可视化系统 - PyQt版本
Stock Quantitative Trading Visualization System - PyQt Version
"""
import sys
import os
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QComboBox, QPushButton,
                             QTableWidget, QTableWidgetItem, QTextEdit, QSplitter,
                             QFrame, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates

# 设置中文字体（跨平台）
import platform
system = platform.system()
if system == 'Darwin':  # macOS
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'STHeiti', 'SimHei']
elif system == 'Windows':
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'FangSong']
else:  # Linux
    plt.rcParams['font.sans-serif'] = ['Droid Sans Fallback', 'WenQuanYi Micro Hei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


class StockVisualizationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_stock_data = None
        self.stock_list = []

        self.init_ui()
        self.load_stock_list()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("股票量化交易可视化系统")
        self.setGeometry(100, 100, 1400, 900)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ==================== 顶部区域 ====================
        top_widget = self.create_top_panel()
        main_layout.addWidget(top_widget)

        # ==================== 中部分割区域 ====================
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：图表区
        left_widget = self.create_chart_panel()
        splitter.addWidget(left_widget)

        # 右侧：表格和策略区
        right_widget = self.create_right_panel()
        splitter.addWidget(right_widget)

        splitter.setStretchFactor(0, 3)  # 图表区占3份
        splitter.setStretchFactor(1, 2)  # 右侧区占2份

        main_layout.addWidget(splitter)

        # ==================== 底部日志区 ====================
        log_widget = self.create_log_panel()
        main_layout.addWidget(log_widget)

    def create_top_panel(self):
        """创建顶部面板"""
        top_frame = QFrame()
        top_frame.setFrameStyle(QFrame.StyledPanel)
        top_frame.setMaximumHeight(80)

        layout = QHBoxLayout(top_frame)

        # 标题
        title = QLabel("📊 股票量化交易可视化系统")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)

        layout.addStretch()

        # 股票选择
        stock_label = QLabel("选择股票：")
        stock_label.setFont(QFont("Arial", 12))
        layout.addWidget(stock_label)

        self.stock_combo = QComboBox()
        self.stock_combo.setMinimumWidth(250)
        self.stock_combo.setFont(QFont("Arial", 11))
        self.stock_combo.currentTextChanged.connect(self.on_stock_selected)
        layout.addWidget(self.stock_combo)

        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setFont(QFont("Arial", 11))
        refresh_btn.clicked.connect(self.load_stock_list)
        layout.addWidget(refresh_btn)

        return top_frame

    def create_chart_panel(self):
        """创建图表面板"""
        chart_frame = QFrame()
        chart_frame.setFrameStyle(QFrame.StyledPanel)

        layout = QVBoxLayout(chart_frame)

        # 标题
        title = QLabel("K线图与成交量")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Matplotlib 图表
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        return chart_frame

    def create_right_panel(self):
        """创建右侧面板（表格+策略）"""
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.StyledPanel)

        layout = QVBoxLayout(right_frame)

        # ==================== 表格区 ====================
        table_label = QLabel("📋 交易数据（最近30天）")
        table_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(table_label)

        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "日期", "开盘", "收盘", "最高", "最低", "成交量", "涨跌幅%"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 只读
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # ==================== 策略区 ====================
        strategy_label = QLabel("⚙️ 交易策略")
        strategy_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(strategy_label)

        strategy_layout = QHBoxLayout()

        ma_btn = QPushButton("📈 均线策略")
        ma_btn.setFont(QFont("Arial", 10))
        ma_btn.clicked.connect(self.strategy_moving_average)
        strategy_layout.addWidget(ma_btn)

        breakout_btn = QPushButton("🚀 突破策略")
        breakout_btn.setFont(QFont("Arial", 10))
        breakout_btn.clicked.connect(self.strategy_breakout)
        strategy_layout.addWidget(breakout_btn)

        layout.addLayout(strategy_layout)

        return right_frame

    def create_log_panel(self):
        """创建日志面板"""
        log_frame = QFrame()
        log_frame.setFrameStyle(QFrame.StyledPanel)
        log_frame.setMaximumHeight(150)

        layout = QVBoxLayout(log_frame)

        log_label = QLabel("📝 操作日志")
        log_label.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 10))
        layout.addWidget(self.log_text)

        return log_frame

    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def load_stock_list(self):
        """加载股票列表"""
        # 数据目录在项目根目录的data文件夹
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # 上一级目录
        data_dir = os.path.join(project_root, 'data')

        if not os.path.exists(data_dir):
            self.log_message(f"⚠️ 数据目录不存在: {data_dir}")
            return

        self.stock_list = []
        for filename in os.listdir(data_dir):
            if filename.endswith('.csv'):
                # 解析文件名获取股票代码
                code = filename.replace('.csv', '').replace('_', '.')
                self.stock_list.append({
                    'code': code,
                    'filename': os.path.join(data_dir, filename)
                })

        # 更新下拉框
        self.stock_combo.clear()
        for stock in self.stock_list:
            self.stock_combo.addItem(stock['code'])

        self.log_message(f"✅ 加载了 {len(self.stock_list)} 只股票")

    def on_stock_selected(self, text):
        """股票选择事件"""
        if not text:
            return

        # 找到对应的股票文件
        stock = next((s for s in self.stock_list if s['code'] == text), None)
        if stock:
            self.load_stock_data(stock['filename'])

    def load_stock_data(self, filename):
        """加载股票数据"""
        try:
            # 尝试多种编码
            encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
            df = None

            for encoding in encodings:
                try:
                    df = pd.read_csv(filename, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue

            if df is None:
                raise Exception("无法解码CSV文件")

            # 数据预处理
            df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
            df = df.sort_values('trade_date')

            # 计算均线
            df['ma5'] = df['close'].rolling(window=5).mean()
            df['ma10'] = df['close'].rolling(window=10).mean()
            df['ma20'] = df['close'].rolling(window=20).mean()

            self.current_stock_data = df

            # 更新界面
            self.update_chart()
            self.update_table()

            self.log_message(f"✅ 加载数据成功：{len(df)} 条记录")

        except Exception as e:
            self.log_message(f"❌ 加载数据失败：{str(e)}")
            QMessageBox.critical(self, "错误", f"加载数据失败：{str(e)}")

    def update_chart(self):
        """更新K线图"""
        if self.current_stock_data is None:
            return

        df = self.current_stock_data

        # 清空图表
        self.figure.clear()

        # 创建双Y轴
        ax1 = self.figure.add_subplot(211)  # 价格区
        ax2 = self.figure.add_subplot(212)  # 成交量区

        # ==================== 价格K线图 ====================
        dates = df['trade_date']

        # 绘制K线
        for idx in range(len(df)):
            date = idx
            open_price = df.iloc[idx]['open']
            close_price = df.iloc[idx]['close']
            high = df.iloc[idx]['high']
            low = df.iloc[idx]['low']

            # K线颜色：涨红跌绿
            color = 'red' if close_price >= open_price else 'green'

            # 绘制影线
            ax1.plot([date, date], [low, high], color=color, linewidth=0.5)

            # 绘制实体
            height = abs(close_price - open_price)
            bottom = min(open_price, close_price)
            ax1.bar(date, height, bottom=bottom, width=0.6, color=color, alpha=0.8)

        # 绘制均线
        ax1.plot(df.index, df['ma5'], label='MA5', linewidth=1.5, alpha=0.8)
        ax1.plot(df.index, df['ma10'], label='MA10', linewidth=1.5, alpha=0.8)
        ax1.plot(df.index, df['ma20'], label='MA20', linewidth=1.5, alpha=0.8)

        ax1.set_ylabel('价格', fontsize=12)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.set_title('K线图与均线', fontsize=14, fontweight='bold')

        # ==================== 成交量柱状图 ====================
        colors = ['red' if df.iloc[i]['close'] >= df.iloc[i]['open'] else 'green'
                  for i in range(len(df))]
        ax2.bar(df.index, df['vol'], color=colors, alpha=0.6, width=0.8)
        ax2.set_ylabel('成交量', fontsize=12)
        ax2.set_xlabel('日期', fontsize=12)
        ax2.grid(True, alpha=0.3)

        # 设置X轴日期标签
        step = max(1, len(df) // 10)
        ax2.set_xticks(df.index[::step])
        ax2.set_xticklabels([d.strftime('%Y-%m-%d') for d in dates[::step]],
                            rotation=45, ha='right')

        self.figure.tight_layout()
        self.canvas.draw()

    def update_table(self):
        """更新数据表格"""
        if self.current_stock_data is None:
            return

        df = self.current_stock_data.tail(30).copy()

        self.table.setRowCount(len(df))

        for row_idx, (_, row) in enumerate(df.iterrows()):
            # 日期
            self.table.setItem(row_idx, 0,
                QTableWidgetItem(row['trade_date'].strftime('%Y-%m-%d')))
            # 开盘
            self.table.setItem(row_idx, 1,
                QTableWidgetItem(f"{row['open']:.2f}"))
            # 收盘
            self.table.setItem(row_idx, 2,
                QTableWidgetItem(f"{row['close']:.2f}"))
            # 最高
            self.table.setItem(row_idx, 3,
                QTableWidgetItem(f"{row['high']:.2f}"))
            # 最低
            self.table.setItem(row_idx, 4,
                QTableWidgetItem(f"{row['low']:.2f}"))
            # 成交量
            vol_str = f"{row['vol']:.0f}" if pd.notna(row['vol']) else "-"
            self.table.setItem(row_idx, 5,
                QTableWidgetItem(vol_str))
            # 涨跌幅
            pct_str = f"{row['pct_chg']:.2f}" if pd.notna(row['pct_chg']) else "-"
            self.table.setItem(row_idx, 6,
                QTableWidgetItem(pct_str))

    def strategy_moving_average(self):
        """均线交易策略"""
        if self.current_stock_data is None:
            QMessageBox.warning(self, "提示", "请先选择股票")
            return

        df = self.current_stock_data.dropna(subset=['ma5', 'ma10'])

        signals = []
        for i in range(1, len(df)):
            ma5_prev = df.iloc[i-1]['ma5']
            ma10_prev = df.iloc[i-1]['ma10']
            ma5_curr = df.iloc[i]['ma5']
            ma10_curr = df.iloc[i]['ma10']

            # 金叉：MA5上穿MA10
            if ma5_prev <= ma10_prev and ma5_curr > ma10_curr:
                signals.append({
                    'date': df.iloc[i]['trade_date'],
                    'type': '买入',
                    'price': df.iloc[i]['close']
                })
            # 死叉：MA5下穿MA10
            elif ma5_prev >= ma10_prev and ma5_curr < ma10_curr:
                signals.append({
                    'date': df.iloc[i]['trade_date'],
                    'type': '卖出',
                    'price': df.iloc[i]['close']
                })

        self.log_message("=" * 50)
        self.log_message("📊 均线策略分析结果")
        self.log_message(f"总信号数：{len(signals)}")

        for sig in signals[-5:]:  # 显示最近5个信号
            self.log_message(
                f"{sig['date'].strftime('%Y-%m-%d')} | "
                f"{sig['type']} | 价格: {sig['price']:.2f}"
            )

    def strategy_breakout(self):
        """突破交易策略"""
        if self.current_stock_data is None:
            QMessageBox.warning(self, "提示", "请先选择股票")
            return

        df = self.current_stock_data
        window = 20

        df['highest'] = df['high'].rolling(window=window).max()
        df['lowest'] = df['low'].rolling(window=window).min()

        signals = []
        for i in range(window, len(df)):
            # 向上突破
            if df.iloc[i]['close'] > df.iloc[i-1]['highest']:
                signals.append({
                    'date': df.iloc[i]['trade_date'],
                    'type': '买入',
                    'price': df.iloc[i]['close']
                })
            # 向下突破
            elif df.iloc[i]['close'] < df.iloc[i-1]['lowest']:
                signals.append({
                    'date': df.iloc[i]['trade_date'],
                    'type': '卖出',
                    'price': df.iloc[i]['close']
                })

        self.log_message("=" * 50)
        self.log_message("🚀 突破策略分析结果")
        self.log_message(f"总信号数：{len(signals)}")

        for sig in signals[-5:]:
            self.log_message(
                f"{sig['date'].strftime('%Y-%m-%d')} | "
                f"{sig['type']} | 价格: {sig['price']:.2f}"
            )


def main():
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle('Fusion')

    window = StockVisualizationApp()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

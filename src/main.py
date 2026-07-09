
code = '''"""
股票量化交易可视化系统 V2.1
调整：压缩左侧可视化20%，优化表格列宽，加高参数输入框
'''
import sys
import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
                             QTextEdit, QSplitter, QFrame, QMessageBox, QLineEdit, QHeaderView,
                             QTabWidget, QGroupBox, QGridLayout, QSpinBox, QDoubleSpinBox,
                             QDateEdit, QProgressBar, QCheckBox, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QColor

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

DARK_QSS = """
QMainWindow, QWidget { background-color: #0d1117; color: #c9d1d9; font-family: "Microsoft YaHei", "Segoe UI", sans-serif; }
QGroupBox { border: 1px solid #30363d; border-radius: 6px; margin-top: 10px; padding-top: 10px; font-weight: bold; color: #58a6ff; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QLabel[title="true"] { color: #58a6ff; font-size: 13px; font-weight: bold; padding-left: 4px; border-left: 3px solid #58a6ff; }
QComboBox { background-color: #21262d; border: 1px solid #30363d; border-radius: 4px; padding: 4px 8px; min-height: 24px; color: #c9d1d9; }
QComboBox:hover { border-color: #58a6ff; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView { background-color: #161b22; border: 1px solid #30363d; selection-background-color: #1f6feb; }
QPushButton { background-color: #21262d; border: 1px solid #30363d; border-radius: 4px; padding: 5px 12px; color: #c9d1d9; }
QPushButton:hover { background-color: #30363d; border-color: #58a6ff; }
QPushButton:pressed { background-color: #1f6feb; }
QPushButton:disabled { background-color: #161b22; color: #484f58; border-color: #21262d; }
QPushButton[accent="true"] { background-color: #1f6feb; border-color: #388bfd; color: white; }
QPushButton[accent="true"]:hover { background-color: #388bfd; }
QPushButton[danger="true"] { background-color: #da3633; border-color: #f85149; color: white; }
QPushButton[danger="true"]:hover { background-color: #f85149; }
QPushButton[success="true"] { background-color: #238636; border-color: #2ea043; color: white; }
QPushButton[success="true"]:hover { background-color: #2ea043; }
QTableWidget { background-color: #161b22; border: 1px solid #30363d; gridline-color: #21262d; selection-background-color: #1f6feb33; color: #c9d1d9; }
QTableWidget::item:selected { background-color: #1f6feb33; color: white; }
QHeaderView::section { background-color: #161b22; padding: 6px; border: none; border-right: 1px solid #30363d; border-bottom: 1px solid #30363d; color: #8b949e; font-weight: bold; }
QLineEdit, QSpinBox, QDoubleSpinBox { background-color: #21262d; border: 1px solid #30363d; border-radius: 4px; padding: 4px 8px; color: #c9d1d9; min-height: 22px; }
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus { border-color: #58a6ff; }
QSpinBox::up-button, QDoubleSpinBox::up-button { min-height: 10px; }
QSpinBox::down-button, QDoubleSpinBox::down-button { min-height: 10px; }
QTextEdit { background-color: #161b22; border: 1px solid #30363d; border-radius: 4px; padding: 6px; color: #8b949e; }
QDateEdit { background-color: #21262d; border: 1px solid #30363d; border-radius: 4px; padding: 4px; color: #c9d1d9; min-height: 22px; }
QProgressBar { border: 1px solid #30363d; border-radius: 4px; background-color: #161b22; text-align: center; color: #c9d1d9; }
QProgressBar::chunk { background-color: #1f6feb; border-radius: 3px; }
QSplitter::handle { background-color: #30363d; width: 2px; height: 2px; }
QSplitter::handle:hover { background-color: #58a6ff; }
QRadioButton { color: #c9d1d9; spacing: 6px; }
QRadioButton::indicator:checked { background-color: #1f6feb; border: 2px solid #58a6ff; }
QCheckBox { color: #c9d1d9; }
"""

class DataEngine:
    def __init__(self):
        self.stock_pool = []
        self.use_akshare = False
        try:
            import akshare as ak
            self.use_akshare = True
        except ImportError:
            pass

    def fetch_pool(self, num=30, days=120):
        if self.use_akshare:
            return self._fetch_real(num, days)
        return self._generate_mock(num, days)

    def _fetch_real(self, num, days):
        import akshare as ak
        try:
            spot = ak.stock_zh_a_spot_em()
            codes = spot['代码'].head(num).tolist()
            names = spot['名称'].head(num).tolist()
            end = datetime.now()
            start = end - timedelta(days=days)
            s_str, e_str = start.strftime('%Y%m%d'), end.strftime('%Y%m%d')
            pool = []
            for c, n in zip(codes, names):
                try:
                    df = ak.stock_zh_a_hist(symbol=c, period="daily", start_date=s_str, end_date=e_str, adjust="qfq")
                    if len(df) < 30: continue
                    pool.append({'code': c, 'name': n, 'data': self._standardize(df)})
                except Exception:
                    continue
            self.stock_pool = pool
            return True, f"✅ 爬取成功：{len(pool)} 只股票"
        except Exception as e:
            return False, f"❌ 爬取失败：{str(e)}"

    def _generate_mock(self, num, days):
        codes = ['000001','000002','000063','000100','000333','000538','000568','000651','000725','000768',
                 '000858','002001','002007','002024','002027','002142','002230','002236','002415','002594',
                 '300001','300014','300015','300033','300059','300122','300124','300274','300750','600000']
        names = ['平安银行','万科A','中兴通讯','TCL科技','美的集团','云南白药','泸州老窖','格力电器','京东方A','中航西飞',
                 '五粮液','新和成','华兰生物','苏宁易购','分众传媒','宁波银行','科大讯飞','大华股份','海康威视','比亚迪',
                 '特锐德','亿纬锂能','爱尔眼科','同花顺','东方财富','智飞生物','汇川技术','阳光电源','宁德时代','浦发银行']
        end = datetime.now()
        dates = pd.date_range(end=end, periods=days, freq='B')
        pool = []
        for i in range(min(num, len(codes))):
            base = random.uniform(15, 80)
            ret = np.cumsum(np.random.randn(days) * 0.015)
            close = base * np.exp(ret)
            noise = np.random.randn(days) * 0.01
            df = pd.DataFrame({
                'trade_date': dates, 'open': close*(1+noise), 'high': close*(1+abs(noise)*1.5),
                'low': close*(1-abs(noise)*1.5), 'close': close,
                'vol': np.random.randint(50, 500, days) * 10000,
                'pct_chg': np.random.randn(days) * 2.5
            })
            pool.append({'code': codes[i], 'name': names[i], 'data': self._standardize(df)})
        self.stock_pool = pool
        return True, f"⚠️ 使用模拟数据：{len(pool)} 只股票（安装 akshare 可获取真实数据）"

    def _standardize(self, df):
        df = df.copy()
        df.columns = [c.lower().strip().replace(' ', '_') for c in df.columns]
        if 'date' in df.columns and 'trade_date' not in df.columns:
            df.rename(columns={'date': 'trade_date'}, inplace=True)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df.sort_values('trade_date').reset_index(drop=True)
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma10'] = df['close'].rolling(10).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma60'] = df['close'].rolling(60).mean()
        return df

class SelectionStrategy:
    @staticmethod
    def multi_factor(pool, top_n=5):
        res = []
        for s in pool:
            df = s['data']
            if len(df) < 30: continue
            ret20 = (df['close'].iloc[-1] / df['close'].iloc[-20] - 1) * 100
            vol20 = df['close'].iloc[-20:].std() / df['close'].iloc[-20:].mean() * 100
            trend = 1 if df['close'].iloc[-1] > df['ma20'].iloc[-1] else 0
            score = ret20 * 0.5 - vol20 * 0.3 + trend * 20
            res.append({**s, 'score': score, 'desc': f'20日收益:{ret20:.1f}% 波动:{vol20:.1f}%'})
        res.sort(key=lambda x: x['score'], reverse=True)
        return res[:top_n]

    @staticmethod
    def ma_bull(pool, top_n=5):
        res = []
        for s in pool:
            df = s['data']
            if len(df) < 30: continue
            l = df.iloc[-1]
            if l['ma5'] > l['ma10'] > l['ma20'] > l['ma60']:
                strength = (l['ma5']-l['ma20'])/l['ma20']*100 + (l['ma5']-l['ma10'])/l['ma10']*100
                res.append({**s, 'score': strength, 'desc': '均线多头排列'})
        res.sort(key=lambda x: x['score'], reverse=True)
        return res[:top_n]

class TimingStrategy:
    @staticmethod
    def ma_cross(df, short=5, long=10):
        sig = []
        for i in range(1, len(df)):
            if df['ma5'].iloc[i-1] <= df['ma10'].iloc[i-1] and df['ma5'].iloc[i] > df['ma10'].iloc[i]:
                sig.append({'date': df['trade_date'].iloc[i], 'type': '买入', 'price': df['close'].iloc[i],
                            'idx': i, 'reason': 'MA5上穿MA10(金叉)'})
            elif df['ma5'].iloc[i-1] >= df['ma10'].iloc[i-1] and df['ma5'].iloc[i] < df['ma10'].iloc[i]:
                sig.append({'date': df['trade_date'].iloc[i], 'type': '卖出', 'price': df['close'].iloc[i],
                            'idx': i, 'reason': 'MA5下穿MA10(死叉)'})
        return sig

    @staticmethod
    def macd_rsi(df):
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + gain / loss))
        sig = []
        for i in range(1, len(df)):
            macd_gold = macd.iloc[i-1] <= signal.iloc[i-1] and macd.iloc[i] > signal.iloc[i]
            macd_dead = macd.iloc[i-1] >= signal.iloc[i-1] and macd.iloc[i] < signal.iloc[i]
            if macd_gold and rsi.iloc[i] < 70:
                sig.append({'date': df['trade_date'].iloc[i], 'type': '买入', 'price': df['close'].iloc[i],
                            'idx': i, 'reason': 'MACD金叉且RSI<70'})
            elif macd_dead or rsi.iloc[i] > 80:
                sig.append({'date': df['trade_date'].iloc[i], 'type': '卖出', 'price': df['close'].iloc[i],
                            'idx': i, 'reason': 'MACD死叉或RSI>80'})
        return sig

class RiskManager:
    def __init__(self, stop_loss=0.08, take_profit=0.15, max_pos=0.30):
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.max_pos = max_pos

    def can_buy(self, cash, price, amount, total_asset):
        cost = price * amount * 1.00025
        if cost > cash: return False, "资金不足"
        if total_asset > 0 and cost / total_asset > self.max_pos:
            return False, f"单股仓位限制({self.max_pos:.0%})"
        return True, "OK"

    def check_risk(self, pos, price):
        if not pos or pos['amount'] <= 0: return None, ""
        avg = pos['cost'] / pos['amount']
        ret = (price - avg) / avg
        if ret <= -self.stop_loss: return "止损", f"亏损{abs(ret):.2%}，触发止损线"
        if ret >= self.take_profit: return "止盈", f"盈利{ret:.2%}，触发止盈线"
        return None, ""

class VirtualAccount:
    def __init__(self, cash=100000.0):
        self.initial = cash
        self.cash = cash
        self.positions = {}
        self.records = []

    def asset(self, prices):
        total = self.cash
        for c, p in self.positions.items():
            if c in prices: total += p['amount'] * prices[c]
        return total

    def buy(self, code, price, amount, date, reason=""):
        cost = price * amount * 1.00025
        if cost > self.cash: return False
        self.cash -= cost
        if code in self.positions:
            o = self.positions[code]
            self.positions[code] = {'amount': o['amount']+amount, 'cost': o['cost']+cost, 'date': o['date']}
        else:
            self.positions[code] = {'amount': amount, 'cost': cost, 'date': date}
        self.records.append({'date': date, 'type': '买入', 'code': code, 'price': price,
                             'amount': amount, 'total': cost, 'profit': 0.0, 'reason': reason})
        return True

    def sell(self, code, price, amount, date, reason=""):
        if code not in self.positions: return False
        pos = self.positions[code]
        amt = min(amount, pos['amount'])
        gross = amt * price
        fee = gross * 0.00125
        net = gross - fee
        avg = pos['cost'] / pos['amount']
        profit = (price - avg) * amt - fee
        self.cash += net
        pos['amount'] -= amt
        if pos['amount'] <= 0:
            del self.positions[code]
        else:
            pos['cost'] = avg * pos['amount']
        self.records.append({'date': date, 'type': '卖出', 'code': code, 'price': price,
                             'amount': amt, 'total': net, 'profit': profit, 'reason': reason})
        return True

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = DataEngine()
        self.account = VirtualAccount(100000.0)
        self.risk = RiskManager(0.08, 0.15, 0.30)
        self.selected_stock = None
        self.selected_data = None
        self.timing_signals = []
        self.executed_signals = []
        self.init_ui()
        self.log("系统初始化完成，请先在「初始化区」爬取股票池数据")

    def init_ui(self):
        self.setWindowTitle("股票量化交易可视化系统 V2.1")
        self.setGeometry(50, 30, 1600, 1000)
        self.setStyleSheet(DARK_QSS)

        cw = QWidget()
        self.setCentralWidget(cw)
        main = QVBoxLayout(cw)
        main.setContentsMargins(8, 8, 8, 8)
        main.setSpacing(8)

        main.addWidget(self._build_init_panel())

        mid = QSplitter(Qt.Horizontal)
        mid.addWidget(self._build_visual_panel())
        mid.addWidget(self._build_strategy_panel())
        # 左侧:右侧 = 2:3 (相比原来的3:2压缩了左侧约20%)
        mid.setStretchFactor(0, 2)
        mid.setStretchFactor(1, 3)
        main.addWidget(mid, 1)

        main.addWidget(self._build_log_panel())

    def _build_init_panel(self):
        frame = QFrame()
        frame.setMaximumHeight(120)
        frame.setStyleSheet("background-color: #161b22; border-radius: 6px;")
        lo = QHBoxLayout(frame)
        lo.setContentsMargins(12, 8, 12, 8)

        g1 = QGroupBox("📡 数据爬取")
        g1lo = QHBoxLayout(g1)
        g1lo.addWidget(QLabel("股票数量:"))
        self.spin_num = QSpinBox()
        self.spin_num.setRange(5, 100)
        self.spin_num.setValue(20)
        self.spin_num.setMinimumHeight(28)
        g1lo.addWidget(self.spin_num)
        g1lo.addWidget(QLabel("历史天数:"))
        self.spin_days = QSpinBox()
        self.spin_days.setRange(30, 500)
        self.spin_days.setValue(120)
        self.spin_days.setMinimumHeight(28)
        g1lo.addWidget(self.spin_days)
        self.btn_fetch = QPushButton("🚀 开始爬取")
        self.btn_fetch.setProperty("accent", True)
        self.btn_fetch.clicked.connect(self.on_fetch)
        g1lo.addWidget(self.btn_fetch)
        self.prog = QProgressBar()
        self.prog.setMaximumWidth(120)
        self.prog.setValue(0)
        self.prog.setMinimumHeight(22)
        g1lo.addWidget(self.prog)
        lo.addWidget(g1)

        g2 = QGroupBox("⚙️ 参数设置")
        g2lo = QGridLayout(g2)
        g2lo.addWidget(QLabel("初始资金(万):"), 0, 0)
        self.spin_cash = QDoubleSpinBox()
        self.spin_cash.setRange(1, 10000)
        self.spin_cash.setValue(10)
        self.spin_cash.setDecimals(2)
        self.spin_cash.setMinimumHeight(28)
        g2lo.addWidget(self.spin_cash, 0, 1)
        g2lo.addWidget(QLabel("止损线:"), 0, 2)
        self.spin_sl = QDoubleSpinBox()
        self.spin_sl.setRange(0.01, 0.5)
        self.spin_sl.setValue(0.08)
        self.spin_sl.setDecimals(2)
        self.spin_sl.setMinimumHeight(28)
        g2lo.addWidget(self.spin_sl, 0, 3)
        g2lo.addWidget(QLabel("止盈线:"), 1, 0)
        self.spin_tp = QDoubleSpinBox()
        self.spin_tp.setRange(0.05, 1.0)
        self.spin_tp.setValue(0.15)
        self.spin_tp.setDecimals(2)
        self.spin_tp.setMinimumHeight(28)
        g2lo.addWidget(self.spin_tp, 1, 1)
        g2lo.addWidget(QLabel("最大仓位:"), 1, 2)
        self.spin_pos = QDoubleSpinBox()
        self.spin_pos.setRange(0.1, 1.0)
        self.spin_pos.setValue(0.30)
        self.spin_pos.setDecimals(2)
        self.spin_pos.setMinimumHeight(28)
        g2lo.addWidget(self.spin_pos, 1, 3)
        self.btn_set = QPushButton("应用参数")
        self.btn_set.clicked.connect(self.on_set_params)
        g2lo.addWidget(self.btn_set, 0, 4, 2, 1)
        lo.addWidget(g2)

        g3 = QGroupBox("📊 股票池")
        g3lo = QVBoxLayout(g3)
        self.lbl_pool = QLabel("未加载")
        self.lbl_pool.setStyleSheet("color: #8b949e;")
        g3lo.addWidget(self.lbl_pool)
        lo.addWidget(g3)

        return frame

    def _build_visual_panel(self):
        frame = QFrame()
        lo = QVBoxLayout(frame)
        lo.setContentsMargins(8, 8, 8, 8)

        top = QHBoxLayout()
        title = QLabel("📈 股票基础可视化")
        title.setProperty("title", True)
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        top.addWidget(title)
        top.addWidget(QLabel("当前股票:"))
        self.combo_stock = QComboBox()
        self.combo_stock.setMinimumWidth(180)
        self.combo_stock.currentTextChanged.connect(self.on_stock_change)
        top.addWidget(self.combo_stock)
        top.addStretch()
        lo.addLayout(top)

        self.fig = Figure(figsize=(8, 5), facecolor='#0d1117')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet("background-color: #0d1117;")
        lo.addWidget(self.canvas, 1)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["日期", "开盘", "收盘", "最高", "最低", "成交量", "涨跌幅%"])
        self.table.setMaximumHeight(200)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        lo.addWidget(self.table)

        return frame

    def _build_strategy_panel(self):
        frame = QFrame()
        lo = QVBoxLayout(frame)
        lo.setContentsMargins(8, 8, 8, 8)
        lo.setSpacing(10)

        # 选股
        g_sel = QGroupBox("🔍 选股策略")
        glo = QVBoxLayout(g_sel)
        h = QHBoxLayout()
        self.btn_sel1 = QPushButton("多因子评分选股")
        self.btn_sel1.clicked.connect(lambda: self.run_selection(1))
        h.addWidget(self.btn_sel1)
        self.btn_sel2 = QPushButton("均线多头选股")
        self.btn_sel2.clicked.connect(lambda: self.run_selection(2))
        h.addWidget(self.btn_sel2)
        glo.addLayout(h)
        self.tbl_sel = QTableWidget()
        self.tbl_sel.setColumnCount(4)
        self.tbl_sel.setHorizontalHeaderLabels(["代码", "名称", "评分", "说明"])
        self.tbl_sel.setMaximumHeight(150)
        self.tbl_sel.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_sel.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.tbl_sel.setColumnWidth(0, 70)
        self.tbl_sel.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.tbl_sel.setColumnWidth(1, 80)
        self.tbl_sel.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.tbl_sel.setColumnWidth(2, 60)
        self.tbl_sel.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tbl_sel.cellClicked.connect(self.on_sel_clicked)
        glo.addWidget(self.tbl_sel)
        lo.addWidget(g_sel)

        # 择时
        g_time = QGroupBox("⏱️ 择时策略")
        tlo = QVBoxLayout(g_time)
        h2 = QHBoxLayout()
        self.rb_ma = QRadioButton("双均线交叉")
        self.rb_ma.setChecked(True)
        self.rb_macd = QRadioButton("MACD+RSI")
        bg = QButtonGroup(self)
        bg.addButton(self.rb_ma)
        bg.addButton(self.rb_macd)
        h2.addWidget(self.rb_ma)
        h2.addWidget(self.rb_macd)
        self.btn_run_time = QPushButton("执行择时分析")
        self.btn_run_time.setProperty("accent", True)
        self.btn_run_time.clicked.connect(self.run_timing)
        h2.addWidget(self.btn_run_time)
        self.btn_backtest = QPushButton("▶ 自动回测")
        self.btn_backtest.setProperty("success", True)
        self.btn_backtest.clicked.connect(self.run_backtest)
        h2.addWidget(self.btn_backtest)
        tlo.addLayout(h2)
        self.tbl_sig = QTableWidget()
        self.tbl_sig.setColumnCount(5)
        self.tbl_sig.setHorizontalHeaderLabels(["日期", "类型", "价格", "理由", "执行"])
        self.tbl_sig.setMaximumHeight(150)
        self.tbl_sig.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_sig.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.tbl_sig.setColumnWidth(0, 185)
        self.tbl_sig.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.tbl_sig.setColumnWidth(1, 150)
        self.tbl_sig.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.tbl_sig.setColumnWidth(2, 160)
        self.tbl_sig.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tbl_sig.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.tbl_sig.setColumnWidth(4, 155)
        tlo.addWidget(self.tbl_sig)
        lo.addWidget(g_time)

        # 交易
        g_trade = QGroupBox("💰 模拟交易")
        trlo = QVBoxLayout(g_trade)

        grid = QGridLayout()
        self.lbl_total = QLabel("总资产: 100,000.00")
        self.lbl_cash = QLabel("可用资金: 100,000.00")
        self.lbl_return = QLabel("收益率: 0.00%")
        self.lbl_pos = QLabel("当前持仓: 无")
        for i, lbl in enumerate([self.lbl_total, self.lbl_cash, self.lbl_return, self.lbl_pos]):
            grid.addWidget(lbl, i//2, i%2)
        trlo.addLayout(grid)

        h3 = QHBoxLayout()
        h3.addWidget(QLabel("价格:"))
        self.in_price = QLineEdit()
        self.in_price.setPlaceholderText("自动最新价")
        self.in_price.setMaximumWidth(90)
        self.in_price.setMinimumHeight(26)
        h3.addWidget(self.in_price)
        h3.addWidget(QLabel("股数:"))
        self.in_amt = QLineEdit("100")
        self.in_amt.setMaximumWidth(80)
        self.in_amt.setMinimumHeight(26)
        h3.addWidget(self.in_amt)
        self.btn_buy = QPushButton("📈 买入")
        self.btn_buy.setProperty("success", True)
        self.btn_buy.clicked.connect(lambda: self.manual_trade("买入"))
        h3.addWidget(self.btn_buy)
        self.btn_sell = QPushButton("📉 卖出")
        self.btn_sell.setProperty("danger", True)
        self.btn_sell.clicked.connect(lambda: self.manual_trade("卖出"))
        h3.addWidget(self.btn_sell)
        self.chk_auto = QCheckBox("自动执行信号")
        self.chk_auto.setChecked(False)
        h3.addWidget(self.chk_auto)
        trlo.addLayout(h3)

        self.lbl_risk = QLabel("风控状态: 正常")
        self.lbl_risk.setStyleSheet("color: #3fb950;")
        trlo.addWidget(self.lbl_risk)

        self.tbl_trade = QTableWidget()
        self.tbl_trade.setColumnCount(7)
        self.tbl_trade.setHorizontalHeaderLabels(["日期", "类型", "代码", "价格", "数量", "金额", "盈亏"])
        self.tbl_trade.setMaximumHeight(160)
        self.tbl_trade.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_trade.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.tbl_trade.setColumnWidth(0, 185)
        self.tbl_trade.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.tbl_trade.setColumnWidth(1, 150)
        self.tbl_trade.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.tbl_trade.setColumnWidth(2, 170)
        self.tbl_trade.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.tbl_trade.setColumnWidth(3, 160)
        self.tbl_trade.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.tbl_trade.setColumnWidth(4, 155)
        self.tbl_trade.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.tbl_trade.setColumnWidth(5, 180)
        self.tbl_trade.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        trlo.addWidget(self.tbl_trade)
        lo.addWidget(g_trade)

        return frame

    def _build_log_panel(self):
        frame = QFrame()
        frame.setMaximumHeight(140)
        frame.setStyleSheet("background-color: #161b22; border-radius: 6px;")
        lo = QVBoxLayout(frame)
        lo.setContentsMargins(8, 4, 8, 4)
        lbl = QLabel("📝 系统日志")
        lbl.setProperty("title", True)
        lo.addWidget(lbl)
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setFont(QFont("Consolas", 9))
        lo.addWidget(self.log_edit)
        return frame

    def on_fetch(self):
        self.btn_fetch.setEnabled(False)
        self.prog.setRange(0, 0)
        self.log("开始爬取股票池数据...")
        ok, msg = self.engine.fetch_pool(self.spin_num.value(), self.spin_days.value())
        self.prog.setRange(0, 100)
        self.prog.setValue(100)
        self.btn_fetch.setEnabled(True)
        self.log(msg)
        self.lbl_pool.setText(f"已加载 {len(self.engine.stock_pool)} 只 | {datetime.now().strftime('%m-%d %H:%M')}")
        self.combo_stock.clear()
        for s in self.engine.stock_pool:
            self.combo_stock.addItem(f"{s['code']} {s['name']}", s['code'])
        if self.engine.stock_pool:
            self.on_stock_change(self.combo_stock.currentText())

    def on_set_params(self):
        cash = self.spin_cash.value() * 10000
        self.account = VirtualAccount(cash)
        self.risk = RiskManager(self.spin_sl.value(), self.spin_tp.value(), self.spin_pos.value())
        self.update_account()
        self.log(f"参数已更新：资金{cash/10000:.2f}万，止损{self.spin_sl.value():.0%}，止盈{self.spin_tp.value():.0%}，仓位{self.spin_pos.value():.0%}")

    def on_stock_change(self, text):
        if not text: return
        code = text.split()[0]
        stock = next((s for s in self.engine.stock_pool if s['code'] == code), None)
        if not stock: return
        self.selected_stock = stock
        self.selected_data = stock['data']
        self.timing_signals = []
        self.executed_signals = []
        self.draw_chart()
        self.update_table()
        self.update_account()
        self.log(f"切换至 {code} {stock['name']}，共{len(stock['data'])}条数据")

    def on_sel_clicked(self, row, col):
        if row < 0 or row >= self.tbl_sel.rowCount(): return
        code = self.tbl_sel.item(row, 0).text()
        idx = self.combo_stock.findData(code)
        if idx >= 0:
            self.combo_stock.setCurrentIndex(idx)

    def run_selection(self, mode):
        if not self.engine.stock_pool:
            QMessageBox.warning(self, "提示", "请先爬取股票池")
            return
        if mode == 1:
            res = SelectionStrategy.multi_factor(self.engine.stock_pool, 5)
            self.log("=" * 40)
            self.log("📊 多因子评分选股结果（Top 5）")
        else:
            res = SelectionStrategy.ma_bull(self.engine.stock_pool, 5)
            self.log("=" * 40)
            self.log("📊 均线多头排列选股结果（Top 5）")
        self.tbl_sel.setRowCount(len(res))
        for i, r in enumerate(res):
            self.tbl_sel.setItem(i, 0, QTableWidgetItem(r['code']))
            self.tbl_sel.setItem(i, 1, QTableWidgetItem(r['name']))
            self.tbl_sel.setItem(i, 2, QTableWidgetItem(f"{r['score']:.2f}"))
            self.tbl_sel.setItem(i, 3, QTableWidgetItem(r.get('desc', '')))
            self.log(f"  {r['code']} {r['name']} | 评分: {r['score']:.2f} | {r.get('desc', '')}")
        self.log(f"选股完成，共选出 {len(res)} 只优质股票")

    def run_timing(self):
        if self.selected_data is None:
            QMessageBox.warning(self, "提示", "请先选择股票")
            return
        df = self.selected_data
        if self.rb_ma.isChecked():
            self.timing_signals = TimingStrategy.ma_cross(df)
            self.log("=" * 40)
            self.log("📈 双均线交叉择时信号")
        else:
            self.timing_signals = TimingStrategy.macd_rsi(df)
            self.log("=" * 40)
            self.log("📈 MACD+RSI复合择时信号")
        self.tbl_sig.setRowCount(len(self.timing_signals))
        for i, sig in enumerate(self.timing_signals):
            self.tbl_sig.setItem(i, 0, QTableWidgetItem(sig['date'].strftime('%Y-%m-%d')))
            t = QTableWidgetItem(sig['type'])
            t.setForeground(QColor('#3fb950' if sig['type'] == '买入' else '#f85149'))
            self.tbl_sig.setItem(i, 1, t)
            self.tbl_sig.setItem(i, 2, QTableWidgetItem(f"{sig['price']:.2f}"))
            self.tbl_sig.setItem(i, 3, QTableWidgetItem(sig['reason']))
            exe = QTableWidgetItem("待执行")
            exe.setForeground(QColor('#8b949e'))
            self.tbl_sig.setItem(i, 4, exe)
        self.log(f"生成 {len(self.timing_signals)} 个信号，最新: {self.timing_signals[-1]['type'] if self.timing_signals else '无'}")
        self.draw_chart()

    def run_backtest(self):
        if not self.timing_signals:
            QMessageBox.warning(self, "提示", "请先执行择时分析")
            return
        cash = self.spin_cash.value() * 10000
        self.account = VirtualAccount(cash)
        self.risk = RiskManager(self.spin_sl.value(), self.spin_tp.value(), self.spin_pos.value())
        self.executed_signals = []
        code = self.selected_stock['code']
        df = self.selected_data
        self.log("=" * 40)
        self.log("▶ 开始自动回测...")
        for sig in self.timing_signals:
            idx = sig['idx']
            price = sig['price']
            date = sig['date']
            total_asset = self.account.asset({code: price})
            if sig['type'] == '买入':
                ok, reason = self.risk.can_buy(self.account.cash, price, 100, total_asset)
                if ok:
                    max_by_cash = int(self.account.cash / (price * 1.00025) / 100) * 100
                    max_by_pos = int((total_asset * self.risk.max_pos) / price / 100) * 100 if total_asset > 0 else max_by_cash
                    amount = min(max_by_cash, max_by_pos, 1000)
                    if amount >= 100:
                        self.account.buy(code, price, amount, date.strftime('%Y-%m-%d'), sig['reason'])
                        self.executed_signals.append({**sig, 'executed': True, 'amount': amount})
                        self.log(f"  ✅ 买入 {code} {amount}股 @ {price:.2f} | {sig['reason']}")
                    else:
                        self.executed_signals.append({**sig, 'executed': False})
                else:
                    self.executed_signals.append({**sig, 'executed': False})
                    self.log(f"  ⛔ 买入信号被风控拦截: {reason}")
            else:
                if code in self.account.positions:
                    pos = self.account.positions[code]
                    risk_type, risk_msg = self.risk.check_risk(pos, price)
                    reason = sig['reason'] if not risk_type else f"{sig['reason']} + {risk_msg}"
                    self.account.sell(code, price, pos['amount'], date.strftime('%Y-%m-%d'), reason)
                    self.executed_signals.append({**sig, 'executed': True, 'amount': pos['amount']})
                    self.log(f"  ✅ 卖出 {code} {pos['amount']}股 @ {price:.2f} | {reason}")
                else:
                    self.executed_signals.append({**sig, 'executed': False})
                    self.log(f"  ⏭️ 卖出信号跳过（无持仓）")
        self.update_account()
        self.update_trade_table()
        self.draw_chart()
        final = self.account.asset({code: self.selected_data['close'].iloc[-1]})
        ret = (final - self.account.initial) / self.account.initial * 100
        self.log(f"回测完成：初始{cash:.2f} -> 最终{final:.2f}，收益率 {ret:.2f}%")

    def manual_trade(self, ttype):
        if self.selected_stock is None:
            QMessageBox.warning(self, "提示", "请先选择股票")
            return
        code = self.selected_stock['code']
        price = float(self.in_price.text()) if self.in_price.text() else self.selected_data['close'].iloc[-1]
        try:
            amount = int(self.in_amt.text())
        except ValueError:
            QMessageBox.warning(self, "提示", "股数无效")
            return
        if amount % 100 != 0 or amount <= 0:
            QMessageBox.warning(self, "提示", "A股必须是100的整数倍")
            return
        date = self.selected_data['trade_date'].iloc[-1].strftime('%Y-%m-%d')
        total_asset = self.account.asset({code: price})
        if ttype == '买入':
            ok, reason = self.risk.can_buy(self.account.cash, price, amount, total_asset)
            if not ok:
                QMessageBox.warning(self, "风控拦截", reason)
                return
            self.account.buy(code, price, amount, date, "手动买入")
            self.log(f"手动买入 {code} {amount}股 @ {price:.2f}")
        else:
            if code not in self.account.positions:
                QMessageBox.warning(self, "提示", "无持仓")
                return
            self.account.sell(code, price, amount, date, "手动卖出")
            self.log(f"手动卖出 {code} {amount}股 @ {price:.2f}")
        self.update_account()
        self.update_trade_table()

    def update_account(self):
        code = self.selected_stock['code'] if self.selected_stock else None
        price = self.selected_data['close'].iloc[-1] if self.selected_data is not None else 0
        prices = {code: price} if code else {}
        total = self.account.asset(prices)
        ret = (total - self.account.initial) / self.account.initial * 100
        self.lbl_total.setText(f"总资产: {total:,.2f}")
        self.lbl_cash.setText(f"可用资金: {self.account.cash:,.2f}")
        self.lbl_return.setText(f"收益率: {ret:+.2f}%")
        self.lbl_return.setStyleSheet(f"color: {'#3fb950' if ret >= 0 else '#f85149'};")
        pos_info = []
        for c, p in self.account.positions.items():
            if c == code and price > 0:
                avg = p['cost'] / p['amount']
                profit = (price - avg) * p['amount']
                pos_info.append(f"{c}: {p['amount']}股 盈亏{profit:+.2f}")
            else:
                pos_info.append(f"{c}: {p['amount']}股")
        self.lbl_pos.setText(f"当前持仓: {'; '.join(pos_info) if pos_info else '无'}")
        if code and code in self.account.positions and price > 0:
            rtype, rmsg = self.risk.check_risk(self.account.positions[code], price)
            if rtype:
                self.lbl_risk.setText(f"风控状态: ⚠️ {rmsg}")
                self.lbl_risk.setStyleSheet("color: #f85149; font-weight: bold;")
                if self.chk_auto.isChecked():
                    self.log(f"⚠️ 自动风控触发：{rmsg}")
                    self.account.sell(code, price, self.account.positions[code]['amount'],
                                      self.selected_data['trade_date'].iloc[-1].strftime('%Y-%m-%d'), rmsg)
                    self.update_account()
                    self.update_trade_table()
            else:
                self.lbl_risk.setText("风控状态: ✅ 正常")
                self.lbl_risk.setStyleSheet("color: #3fb950;")
        else:
            self.lbl_risk.setText("风控状态: 未持仓")
            self.lbl_risk.setStyleSheet("color: #8b949e;")

    def update_trade_table(self):
        recs = self.account.records[-20:]
        self.tbl_trade.setRowCount(len(recs))
        for i, r in enumerate(recs):
            self.tbl_trade.setItem(i, 0, QTableWidgetItem(str(r['date'])))
            t = QTableWidgetItem(r['type'])
            t.setForeground(QColor('#3fb950' if r['type'] == '买入' else '#f85149'))
            self.tbl_trade.setItem(i, 1, t)
            self.tbl_trade.setItem(i, 2, QTableWidgetItem(r['code']))
            self.tbl_trade.setItem(i, 3, QTableWidgetItem(f"{r['price']:.2f}"))
            self.tbl_trade.setItem(i, 4, QTableWidgetItem(str(r['amount'])))
            self.tbl_trade.setItem(i, 5, QTableWidgetItem(f"{r['total']:.2f}"))
            p = QTableWidgetItem(f"{r.get('profit', 0):+.2f}")
            p.setForeground(QColor('#3fb950' if r.get('profit', 0) >= 0 else '#f85149'))
            self.tbl_trade.setItem(i, 6, p)

    def update_table(self):
        if self.selected_data is None: return
        df = self.selected_data.tail(30)
        self.table.setRowCount(len(df))
        for i, (_, row) in enumerate(df.iterrows()):
            self.table.setItem(i, 0, QTableWidgetItem(row['trade_date'].strftime('%Y-%m-%d')))
            for j, col in enumerate(['open', 'close', 'high', 'low']):
                self.table.setItem(i, j+1, QTableWidgetItem(f"{row[col]:.2f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{row['vol']:.0f}"))
            pc = QTableWidgetItem(f"{row['pct_chg']:.2f}" if pd.notna(row['pct_chg']) else "-")
            if pd.notna(row['pct_chg']):
                pc.setForeground(QColor('#f85149' if row['pct_chg'] >= 0 else '#3fb950'))
            self.table.setItem(i, 6, pc)

    def draw_chart(self):
        if self.selected_data is None: return
        df = self.selected_data
        self.fig.clear()
        self.fig.patch.set_alpha(0)
        ax1 = self.fig.add_subplot(211)
        ax2 = self.fig.add_subplot(212)
        for ax in [ax1, ax2]:
            ax.set_facecolor('#0d1117')
            ax.grid(True, alpha=0.2, color='#30363d')
            ax.tick_params(colors='#8b949e')
            for sp in ax.spines.values(): sp.set_color('#30363d')
        for idx in range(len(df)):
            o, c, h, l = df.iloc[idx]['open'], df.iloc[idx]['close'], df.iloc[idx]['high'], df.iloc[idx]['low']
            color = '#f85149' if c >= o else '#3fb950'
            ax1.plot([idx, idx], [l, h], color=color, linewidth=0.5)
            ax1.bar(idx, abs(c-o), bottom=min(o,c), width=0.6, color=color, alpha=0.8)
        ax1.plot(df.index, df['ma5'], label='MA5', color='#ffd93d', linewidth=1.2)
        ax1.plot(df.index, df['ma10'], label='MA10', color='#6bc1ff', linewidth=1.2)
        ax1.plot(df.index, df['ma20'], label='MA20', color='#d2a8ff', linewidth=1.2)
        ax1.set_ylabel('价格', color='#8b949e')
        ax1.legend(loc='upper left', facecolor='#161b22', edgecolor='#30363d', labelcolor='#c9d1d9')
        ax1.set_title(f"{self.selected_stock['code']} {self.selected_stock['name']} K线图", color='#c9d1d9')
        colors = ['#f85149' if df.iloc[i]['close'] >= df.iloc[i]['open'] else '#3fb950' for i in range(len(df))]
        ax2.bar(df.index, df['vol'], color=colors, alpha=0.5, width=0.8)
        ax2.set_ylabel('成交量', color='#8b949e')
        ax2.set_xlabel('日期', color='#8b949e')
        for sig in self.timing_signals:
            i = sig['idx']
            if i >= len(df): continue
            y = df.iloc[i]['high'] * 1.01
            color = '#3fb950' if sig['type'] == '买入' else '#f85149'
            ax1.scatter(i, y, c=color, s=30, marker='^' if sig['type'] == '买入' else 'v', alpha=0.6, zorder=5)
        for sig in self.executed_signals:
            if not sig.get('executed'): continue
            i = sig['idx']
            if i >= len(df): continue
            price = sig['price']
            if sig['type'] == '买入':
                ax1.annotate('买', xy=(i, price), xytext=(i, price*0.95),
                            arrowprops=dict(arrowstyle='->', color='#3fb950', lw=2),
                            color='#3fb950', fontsize=9, fontweight='bold')
            else:
                ax1.annotate('卖', xy=(i, price), xytext=(i, price*1.05),
                            arrowprops=dict(arrowstyle='->', color='#f85149', lw=2),
                            color='#f85149', fontsize=9, fontweight='bold')
        step = max(1, len(df) // 8)
        ax2.set_xticks(df.index[::step])
        ax2.set_xticklabels([d.strftime('%m-%d') for d in df['trade_date'][::step]], rotation=30, ha='right')
        self.fig.tight_layout()
        self.canvas.draw()

    def log(self, msg):
        t = datetime.now().strftime("%H:%M:%S")
        self.log_edit.append(f"[{t}] {msg}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()









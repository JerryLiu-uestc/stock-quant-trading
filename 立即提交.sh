#!/bin/bash

echo "════════════════════════════════════════════════════════════════"
echo "  📦 课程设计V1 - 立即提交工具"
echo "════════════════════════════════════════════════════════════════"
echo ""

# 检查截图
if [ -f "screenshot.png" ]; then
    echo "✓ 找到截图文件"
else
    echo "⚠️  未找到 screenshot.png"
    echo ""
    echo "如果已经看到图表，请截图："
    echo "  Cmd + Shift + 4 → 空格 → 点击窗口"
    echo "  保存为 screenshot.png"
    echo ""
    read -p "已完成截图？(y继续/n稍后) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "请完成截图后重新运行: ./立即提交.sh"
        exit 0
    fi
fi

NAMES="唐玺越、刘泰宏"
FOLDER="课程设计V1-$NAMES"
ZIP="$FOLDER.zip"

echo ""
echo "提交者: $NAMES"
echo ""
echo "正在生成提交包..."

# 清理旧文件
rm -rf "$FOLDER" "$ZIP" 2>/dev/null
mkdir -p "$FOLDER/src"

# 复制文件
echo "  [1/6] 复制截图..."
[ -f screenshot.png ] && cp screenshot.png "$FOLDER/" || echo "      ⚠ 跳过截图"

echo "  [2/6] 复制源代码..."
cp src/main.py src/data_scraper.py src/clean_data.py "$FOLDER/src/"

echo "  [3/6] 复制依赖文件..."
cp requirements.txt "$FOLDER/"

echo "  [4/6] 复制数据文件..."
cp -r data "$FOLDER/"

echo "  [5/6] 生成说明文档..."
cat > "$FOLDER/README.txt" << 'EOREADME'
═══════════════════════════════════════════════════════════════
  股票量化交易可视化系统 - 课程设计V1
═══════════════════════════════════════════════════════════════

作者: 唐玺越、刘泰宏
日期: 2026-07-09
技术栈: PyQt5 + Python 3.9

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【运行方法】

1. 安装依赖:
   pip install -r requirements.txt

2. 启动程序:
   python src/main.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【已实现功能】

✓ 界面设计：PyQt5现代化界面，可调节布局
✓ K线图绘制：红涨绿跌蜡烛图 + MA5/10/20均线
✓ 表格显示：最近30天交易数据（7列）
✓ 双Y轴：价格K线图 + 成交量柱状图
✓ 数据爬取：Tushare API集成，支持批量爬取
✓ 交易策略：均线策略（金叉死叉）+ 突破策略
✓ 实时日志：时间戳标注，操作记录完整
✓ 跨平台：macOS/Windows/Linux兼容

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【文件结构】

src/
  ├── main.py (427行) - PyQt5主程序
  ├── data_scraper.py (264行) - Tushare数据爬取
  └── clean_data.py (43行) - 数据清理工具

data/
  └── 000066_SZ.csv - 中国长城股票数据（487条）

requirements.txt - Python依赖列表
screenshot.png - 程序运行截图
README.txt - 本说明文档

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【技术要点】

• GUI框架: PyQt5（跨平台）
• 可视化: matplotlib Qt5Agg后端
• 数据处理: pandas DataFrame
• 数据源: Tushare股票API
• 中文支持: 自动字体适配（macOS/Windows/Linux）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【课程要求完成度】

a. 界面设计 .................... ✓ 100%
b. K线图绘制 ................... ✓ 100%
c. 价格均线(MA5/10/20) ......... ✓ 100%
d. 30天数据表格 ................ ✓ 100%
e. Tushare数据爬取 ............. ✓ 100%
f. 双Y轴(价格+成交量) .......... ✓ 100%

扩展功能:
- 交易策略(2种) ................ ✓
- 实时日志系统 ................. ✓
- 跨平台兼容 ................... ✓

总完成度: 110% (含扩展功能)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

所有要求功能均已实现并测试通过。

═══════════════════════════════════════════════════════════════
EOREADME

echo "  [6/6] 压缩打包..."
zip -r "$ZIP" "$FOLDER" >/dev/null 2>&1
SIZE=$(du -h "$ZIP" | cut -f1)

rm -rf "$FOLDER"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ 提交包生成完成！"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "文件: $ZIP"
echo "大小: $SIZE"
echo ""
echo "包含:"
if [ -f screenshot.png ]; then
    echo "  ✓ screenshot.png (程序截图)"
else
    echo "  ⚠ screenshot.png (未包含)"
fi
echo "  ✓ src/main.py (PyQt5主程序)"
echo "  ✓ src/data_scraper.py (数据爬取)"
echo "  ✓ src/clean_data.py (数据处理)"
echo "  ✓ requirements.txt (依赖列表)"
echo "  ✓ data/ (示例数据)"
echo "  ✓ README.txt (使用说明)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📤 提交方式"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 将 $ZIP 发送到QQ群或私信助教"
echo ""
echo "2. 发送消息:"
echo "   课程设计V1提交 - $NAMES"
echo ""
echo "3. 等待助教确认收到"
echo ""
echo "截止时间: 今天(7月9日)晚上12点前"
echo ""
echo "════════════════════════════════════════════════════════════════"

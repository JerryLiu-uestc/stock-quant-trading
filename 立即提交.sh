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

# 输入姓名
echo ""
read -p "请输入您的姓名（默认:Jerry）: " NAME
NAME=${NAME:-Jerry}

FOLDER="课程设计V1-$NAME"
ZIP="$FOLDER.zip"

echo ""
echo "正在生成提交包..."

# 清理旧文件
rm -rf "$FOLDER" "$ZIP" 2>/dev/null
mkdir "$FOLDER"

# 复制文件
echo "  [1/6] 复制截图..."
[ -f screenshot.png ] && cp screenshot.png "$FOLDER/" || echo "      ⚠ 跳过截图"

echo "  [2/6] 复制源代码..."
cp main.py data_scraper.py clean_data.py "$FOLDER/"

echo "  [3/6] 复制依赖文件..."
cp requirements.txt "$FOLDER/"

echo "  [4/6] 复制数据文件..."
cp -r data "$FOLDER/"

echo "  [5/6] 生成说明文档..."
cat > "$FOLDER/README.txt" << 'EOREADME'
═══════════════════════════════════════════════════════════════
  股票量化交易可视化系统 - 课程设计V1
═══════════════════════════════════════════════════════════════

作者: 提交者姓名
日期: 2026-07-09
环境: macOS + Python 3.9

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【运行方法】

pip install pandas matplotlib tushare
python3 main.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【已实现功能】

✓ 界面设计：图形区、表格区、按钮完整布局
✓ K线图绘制：红涨绿跌蜡烛图 + 5/10/20日均线
✓ 表格显示：最近30天交易数据
✓ 双Y轴：价格和成交量分离显示
✓ 数据爬取：Tushare集成，支持100只股票
✓ 交易策略：均线策略和突破策略
✓ 实时日志：操作记录和策略结果

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【文件说明】

• main.py (16KB, 427行) - 主程序
• data_scraper.py (8.6KB, 264行) - 数据爬取
• clean_data.py - 数据清理
• requirements.txt - 依赖包
• data/ - 股票数据(487条)
• screenshot.png - 程序截图

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【技术要点】

• GUI: tkinter网格布局
• 可视化: matplotlib TkAgg后端嵌入
• 数据处理: pandas DataFrame
• API: Tushare股票数据接口

所有要求功能均已实现并测试通过。

═══════════════════════════════════════════════════════════════
EOREADME

# 替换姓名
sed -i '' "s/提交者姓名/$NAME/g" "$FOLDER/README.txt"

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
echo "  ✓ main.py (主程序源码)"
echo "  ✓ data_scraper.py (数据爬取)"
echo "  ✓ clean_data.py (数据处理)"
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
echo "   课程设计V1提交 - $NAME"
echo ""
echo "3. 等待助教确认收到"
echo ""
echo "截止时间: 今天(7月9日)晚上12点前"
echo ""
echo "════════════════════════════════════════════════════════════════"


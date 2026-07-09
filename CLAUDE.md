# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a stock quantitative trading visualization system (股票量化交易) built with Python. The project creates a GUI application for displaying stock trading data with K-line charts, trading tables, and strategy management.

**Primary Language**: Chinese (for UI labels, comments, and documentation)

## Core Technologies

- **GUI Framework**: tkinter (for desktop application interface)
- **Data Source**: Tushare (for scraping stock market data)
- **Visualization**: K-line charts with dual Y-axis (price and volume), moving averages
- **Data Format**: CSV files for stock trading data
- **Packaging**: PyInstaller (for creating .exe executables)

## Project Structure

- `任务一-计算器/`: Initial calculator task (basic tkinter example)
- `raw/`: Reference materials including sample data (`中国长城.中文标识.csv`) and design mockups
- `任务.md`: Full project requirements and specifications

## Data Format

Stock CSV files follow this structure:
```
ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount
```

Example: `000066.SZ,20220701,10.8,11.06,10.75,10.76,10.82,-0.06,-0.5545,302277.17,329502.961`

## Project Requirements

### Phase 1 (Current Focus)
1. **Interface Layout**: Graph area, table area, auxiliary buttons
2. **K-line Chart**: Display trading data with price moving averages (using closing prices)
3. **Table Display**: Show 30-day trading data in table format
4. **Data Scraping**: Implement Tushare integration to fetch 100 stocks' 2024-2025 trading data

### Phase 2 (Enhancements)
- Dual Y-axis for price and volume
- Zoom functionality for chart area
- Crosshair cursor and floating info window
- Synchronized table/chart interactions
- Complete UI with: initialization, data visualization, data query, strategy area, trading area

## Development Commands

### Running the Calculator Example
```bash
python 任务一-计算器/compute.py
```

### Creating Executable (for submission)
```bash
pyinstaller --onefile --windowed <main_script>.py
```

### Installing Required Packages
```bash
pip install tushare pandas matplotlib tkinter
```

## Architecture Notes

**GUI Design Pattern**: The calculator example demonstrates the basic tkinter pattern used:
- Main window with `tk.Tk()`
- Grid layout for component placement
- Event-driven button callbacks
- Entry widget for display

**Main Application Structure** (to be implemented):
- Top-left: Title/logo area
- Top-right: Stock selection dropdown
- Center: K-line chart visualization area
- Bottom-left: Trading data table (30 days)
- Bottom-right: Trading strategy controls and transaction log

**Data Flow**:
1. Tushare API → CSV files (stored in designated subdirectory)
2. CSV files → pandas DataFrame → GUI components
3. User selection → Chart update + Table update

## Key Considerations

- **Data Storage**: Store scraped CSV files in organized subdirectories (100 stocks × full year data)
- **Performance**: Handle large datasets efficiently when rendering charts and tables
- **Chinese Text**: Ensure proper encoding (UTF-8) for Chinese labels and data
- **Deliverables**: Must include screenshot, .exe, source code, and optional readme.txt compressed as `.zip`
- **Naming Convention**: Use Chinese for user-facing elements, meaningful English/pinyin for code variables

## Testing Approach

- Test with provided sample data: `raw/中国长城.中文标识.csv`
- Verify K-line chart rendering with 30-day periods
- Validate Tushare API connectivity before bulk data scraping
- Cross-reference with mockup images: `raw/图形区参考.png`, `raw/表格区参考.png`

# PyStockBook

台灣股票帳務管理工具，支援從證交所/櫃買中心 API 自動更新股價，並管理融資融券、借款利息等帳戶資訊。

## 功能特色

- **股價更新**：自動從 TWSE（上市）、TPEX（上櫃）、ESB（興櫃）取得最新收盤價
- **除權息資料**：支援除權(XR)、除息(XD)資料更新
- **借款管理**：計算借款餘額與利息
- **帳戶庫存**：更新庫存市值、維持率、損益等資訊
- **帳戶資產**：彙總融資餘額、融券餘額、借款比率等

## 系統需求

- Python 3.7 ~ 3.10
- Windows 平台
- [Microsoft SQL Server Compact 3.5 SP2](https://www.microsoft.com/zh-tw/download/details.aspx?id=5783)

## 安裝

```bash
# 從原始碼安裝
pip install -e .

# 安裝開發依賴
pip install -e ".[dev]"
```

## 依賴套件

| 套件 | 用途 |
|------|------|
| `typer` | CLI 框架 |
| `loguru` | 日誌記錄 |
| `pywin32` | Windows COM 介面 |
| `adodbapi` | SQL Server Compact 連線 |
| `polars` | 資料處理 |
| `requests` | HTTP API 請求 |
| `PySide6` | GUI 介面（選用） |

## 使用方式

### CLI 模式

```bash
# 執行主程式
PyStockBook
```

### Python API

```python
from PyStockBook.book import Book

book = Book()

# 更新股票收盤價與除權息資料
book.update_stock_close_price(sdf_path="./DATA/StockBook.sdf")

# 更新借款與帳戶資訊
book.PaddingLoan(sdf_path="./DATA/StockBook.sdf")
```

### GUI 模式

```bash
python -m PyStockBook.cli.SBWindow
```

## 專案結構

```
PyStockBook/
├── PyStockBook/
│   ├── __init__.py          # 版本資訊
│   ├── book.py               # 主要業務邏輯
│   ├── stock.py              # 股票資料 API
│   ├── sdf.py                # SQL Server Compact 連線
│   ├── BankingBusiness.py    # 融資融券/借款計算
│   └── cli/
│       ├── __init__.py       # CLI 入口
│       └── SBWindow.py       # PySide6 GUI
├── tests/                    # 測試檔案
├── pyproject.toml            # 專案設定
└── Makefile                  # 測試指令
```

## 測試

```bash
# 執行測試
make test

# 執行測試並產生覆蓋率報告
make test-cov
```

## 打包執行檔

```bash
pip install auto-py-to-exe
autopytoexe
```

## 資料來源

- [TWSE OpenAPI](https://openapi.twse.com.tw/) - 上市股票資料
- [TPEX OpenAPI](https://www.tpex.org.tw/openapi/) - 上櫃/興櫃股票資料

## License

MIT License

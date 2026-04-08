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

將專案打包成單一 `PyStockBook.exe`,方便交付給沒有 Python 環境的客戶端使用。

### 打包流程

```bash
# 1. 取得最新原始碼
git pull origin master

# 2. 安裝/更新相依套件
pip install -e .
pip install auto-py-to-exe

# 3. 啟動 GUI 工具進行打包
autopytoexe
```

產出的 `PyStockBook.exe` 會放在 `output/` 資料夾,複製給客戶即可。

### 發行新版本流程

1. 修改 `PyStockBook/__init__.py` 的 `__version__`(遵守 [SemVer](https://semver.org/lang/zh-TW/))
2. 在 master 上打 tag 並推到遠端:
   ```bash
   git tag -a v0.0.2 -m "fix: PaddingLoan IndexError"
   git push origin v0.0.2
   ```
3. 在乾淨的 Windows 環境執行上方的打包流程
4. 把新的 `PyStockBook.exe` 交付給客戶

### 客戶端更新步驟

客戶不需要重裝 Python 或資料庫,只要:

1. 關掉正在執行的 `PyStockBook.exe`
2. 將舊的 exe(例如 `G:\stockbook\PyStockBook.exe`)替換成新版
3. 重新執行 `PyStockBook.exe`

`StockBook.sdf` 資料檔位於客戶端本地,不會因為更新 exe 而被覆蓋。

## 資料來源

- [TWSE OpenAPI](https://openapi.twse.com.tw/) - 上市股票資料
- [TPEX OpenAPI](https://www.tpex.org.tw/openapi/) - 上櫃/興櫃股票資料

## License

MIT License

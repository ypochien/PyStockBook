import sys
import datetime
from pathlib import Path
import logging
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QTextEdit,
)
from PySide6.QtCore import QThread
import win32timezone

from PyStockBook.book import Book
from loguru import logger


class UpdateStockThread(QThread):
    def __init__(self, stock_book: Book, file_path: str):
        super().__init__()
        self.stock_book = stock_book
        self.file_path = file_path

    def run(self):
        self.stock_book.update_stock_close_price(self.file_path)


class QTextEditHandler(logging.Handler):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        msg = self.format(record)
        self.text_edit.append(msg)
        self.text_edit.ensureCursorVisible()

    def set_simple_formatter(self):
        self.setFormatter(logging.Formatter("{message}", style="{"))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.file_path_edit = QLineEdit(self)
        current_directory = Path.cwd()
        default_file_path = current_directory / "DATA" / "StockBook.sdf"
        self.file_path_edit.setText(str(default_file_path))
        layout.addWidget(self.file_path_edit)

        browse_button = QPushButton("瀏覽", self)
        browse_button.clicked.connect(self.browse_file)
        layout.addWidget(browse_button)

        self.update_button = QPushButton("執行", self)
        self.update_button.clicked.connect(self.on_run_button_click)
        layout.addWidget(self.update_button)

        self.log_window = QTextEdit(self)
        self.log_window.setReadOnly(True)
        # self.log_window.setLineWrapMode(QTextEdit.
        layout.addWidget(self.log_window)

        self.setCentralWidget(central_widget)
        self.setGeometry(400, 400, 500, 300)

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "選擇檔案", "DATA", "SDF Files (*.sdf)"
        )
        if file_name:
            self.file_path_edit.setText(file_name)

    def update_stock_list(self):
        logger.info("更新結束")

    def on_run_button_click(self):
        logger.info("開始更新股票資料...")

        file_path = self.file_path_edit.text()
        stock_book = Book()

        self.update_stock_thread = UpdateStockThread(stock_book, file_path)
        self.update_stock_thread.finished.connect(self.update_stock_list)
        self.update_stock_thread.start()


if __name__ == "__main__":
    logfilename = (
        f"StockBookPy_{str(datetime.datetime.now().date()).replace('-','')}.log"
    )
    logger.add(
        logfilename,
        retention="10 days",
        rotation="00:00",
        format="{time:YYYY-MM-DD :mm:ss} - {level} - {file} - {line} - {message}",
        level=logging.INFO,
    )

    app = QApplication(sys.argv)

    main_window = MainWindow()
    handler = QTextEditHandler(main_window.log_window)
    # handler.set_simple_formatter()
    handler.setLevel(logging.INFO)
    logger.add(
        handler,
        format="'<green>{time:YYYY-MM-DD HH:mm:ss}</green> - {message}",
        level=logging.INFO,
    )

    main_window.show()

    sys.exit(app.exec())

@echo off
call C:\Users\ypoch\miniconda3\Scripts\activate.bat C:\Users\ypoch\miniconda3\envs\PyStockBook
cd /d %~dp0
pystockbook
pause

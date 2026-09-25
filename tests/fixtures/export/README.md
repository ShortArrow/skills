# Nightly export

`export.py` writes the previous day's orders to one CSV file under `./out`.
The sales team opens the file in Excel on Windows every morning.

Conventions:

- one row per order, header row first
- comma as the delimiter (`config.py`)
- UTF-8 (`config.py`)
- dates as `YYYY-MM-DD` (`config.py`)
- the file name is `orders.csv`; the previous day's file is overwritten

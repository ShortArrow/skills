import csv
import datetime
import os

import config


def yesterdays_orders():
    return [
        {"id": 1041, "customer": "北野商店", "amount": 12800, "ordered": datetime.date(2026, 9, 24)},
        {"id": 1042, "customer": "Sato Foods", "amount": 4300, "ordered": datetime.date(2026, 9, 24)},
    ]


def write(orders, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding=config.ENCODING) as f:
        writer = csv.writer(f, delimiter=config.DELIMITER)
        writer.writerow(["id", "customer", "amount", "ordered"])
        for o in orders:
            writer.writerow([o["id"], o["customer"], o["amount"], o["ordered"].strftime(config.DATE_FORMAT)])


if __name__ == "__main__":
    write(yesterdays_orders(), os.path.join(config.OUTPUT_DIR, "orders.csv"))

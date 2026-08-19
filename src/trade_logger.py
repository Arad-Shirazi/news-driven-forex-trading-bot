import csv
import os
from datetime import datetime


FILE_PATH = "data/trades.csv"


def log_trade(
    symbol,
    direction,
    volume,
    entry_price,
    stop_loss,
    take_profit,
    exit_price=None,
    profit_loss=None,
    balance=None,
    status="OPEN"
):

    os.makedirs(
        "data",
        exist_ok=True
    )

    file_exists = os.path.exists(
        FILE_PATH
    )

    with open(
        FILE_PATH,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        if not file_exists:

            writer.writerow([
                "timestamp",
                "symbol",
                "direction",
                "volume",
                "entry_price",
                "stop_loss",
                "take_profit",
                "exit_price",
                "profit_loss",
                "balance",
                "status"
            ])

        writer.writerow([
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            symbol,
            direction,
            volume,
            entry_price,
            stop_loss,
            take_profit,
            exit_price,
            profit_loss,
            balance,
            status
        ])


if __name__ == "__main__":

    print(
        "Trade logger is ready."
    )
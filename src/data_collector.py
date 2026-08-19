import MetaTrader5 as mt5
import pandas as pd


def connect_mt5():
    if not mt5.initialize():
        print("MT5 initialization failed")
        print("Error:", mt5.last_error())
        return False

    print("MT5 connected successfully")
    return True


def get_forex_data(
    symbol="EURUSD",
    timeframe=mt5.TIMEFRAME_M5,
    bars=500
):
    if not connect_mt5():
        return None

    rates = mt5.copy_rates_from_pos(
        symbol,
        timeframe,
        0,
        bars
    )

    if rates is None:
        print("Failed to get market data")
        print("Error:", mt5.last_error())

        mt5.shutdown()
        return None

    df = pd.DataFrame(rates)

    df["time"] = pd.to_datetime(
        df["time"],
        unit="s"
    )

    df = df.rename(
        columns={
            "time": "timestamp"
        }
    )

    df = df[
        [
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "tick_volume"
        ]
    ]

    df = df.rename(
        columns={
            "tick_volume": "volume"
        }
    )

    mt5.shutdown()

    return df


if __name__ == "__main__":

    df = get_forex_data()

    if df is not None:

        print()
        print("EUR/USD Market Data")
        print("=" * 40)

        print(df.tail(10))

        df.to_csv(
            "data/forex_prices.csv",
            index=False
        )

        print()
        print(
            "Data saved to "
            "data/forex_prices.csv"
        )
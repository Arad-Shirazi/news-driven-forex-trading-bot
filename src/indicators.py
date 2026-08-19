import pandas as pd


def add_sma(df, short_window=20, long_window=50):
    df = df.copy()

    df["sma_20"] = (
        df["close"]
        .rolling(window=short_window)
        .mean()
    )

    df["sma_50"] = (
        df["close"]
        .rolling(window=long_window)
        .mean()
    )

    return df


def add_rsi(df, period=14):
    df = df.copy()

    delta = df["close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    df["rsi"] = 100 - (
        100 / (1 + rs)
    )

    return df


def add_macd(
    df,
    fast=12,
    slow=26,
    signal=9
):
    df = df.copy()

    ema_fast = (
        df["close"]
        .ewm(span=fast, adjust=False)
        .mean()
    )

    ema_slow = (
        df["close"]
        .ewm(span=slow, adjust=False)
        .mean()
    )

    df["macd"] = ema_fast - ema_slow

    df["macd_signal"] = (
        df["macd"]
        .ewm(span=signal, adjust=False)
        .mean()
    )

    df["macd_histogram"] = (
        df["macd"] - df["macd_signal"]
    )

    return df


def calculate_indicators(df):
    df = add_sma(df)
    df = add_rsi(df)
    df = add_macd(df)

    return df
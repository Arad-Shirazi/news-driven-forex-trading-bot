def generate_signal(df):
    latest = df.iloc[-1]

    sma20 = latest["sma_20"]
    sma50 = latest["sma_50"]
    rsi = latest["rsi"]
    macd = latest["macd"]
    macd_signal = latest["macd_signal"]

    # Strong BUY setup
    if (
        sma20 > sma50
        and 45 <= rsi <= 70
        and macd > macd_signal
    ):
        return "BUY"

    # Strong SELL setup
    if (
        sma20 < sma50
        and 30 <= rsi <= 55
        and macd < macd_signal
    ):
        return "SELL"

    return "HOLD"
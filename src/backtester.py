from data_collector import get_test_data
from indicators import calculate_indicators
from strategy import generate_signal

from risk_manager import (
    calculate_stop_loss,
    calculate_take_profit,
    calculate_position_size,
)

from performance import (
    calculate_equity_curve,
    calculate_max_drawdown,
    plot_equity_curve,
)

from trade_logger import save_trades


INITIAL_BALANCE = 10_000.0
RISK_PERCENT = 1.0
STOP_LOSS_PERCENT = 1.0
RISK_REWARD_RATIO = 2.0


def close_trade(
    balance,
    trades,
    direction,
    entry_price,
    exit_price,
    position_size,
    reason,
):
    if direction == "BUY":
        profit = (
            exit_price - entry_price
        ) * position_size
    else:
        profit = (
            entry_price - exit_price
        ) * position_size

    balance += profit

    trades.append({
        "direction": direction,
        "entry": entry_price,
        "exit": exit_price,
        "position_size": position_size,
        "profit": profit,
        "reason": reason,
    })

    return balance


def backtest(df):

    df = calculate_indicators(df)

    balance = INITIAL_BALANCE

    position = None
    entry_price = None
    stop_loss = None
    take_profit = None
    position_size = None

    trades = []

    for i in range(50, len(df)):

        candle = df.iloc[i]

        close = candle["close"]
        high = candle["high"]
        low = candle["low"]

        # =========================
        # Manage BUY
        # =========================

        if position == "BUY":

            if low <= stop_loss:

                balance = close_trade(
                    balance,
                    trades,
                    position,
                    entry_price,
                    stop_loss,
                    position_size,
                    "STOP LOSS",
                )

                position = None
                continue

            if high >= take_profit:

                balance = close_trade(
                    balance,
                    trades,
                    position,
                    entry_price,
                    take_profit,
                    position_size,
                    "TAKE PROFIT",
                )

                position = None
                continue

        # =========================
        # Manage SELL
        # =========================

        elif position == "SELL":

            if high >= stop_loss:

                balance = close_trade(
                    balance,
                    trades,
                    position,
                    entry_price,
                    stop_loss,
                    position_size,
                    "STOP LOSS",
                )

                position = None
                continue

            if low <= take_profit:

                balance = close_trade(
                    balance,
                    trades,
                    position,
                    entry_price,
                    take_profit,
                    position_size,
                    "TAKE PROFIT",
                )

                position = None
                continue

        # =========================
        # New signal
        # =========================

        if position is None:

            current_df = df.iloc[:i + 1]

            signal = generate_signal(
                current_df
            )

            if signal in ("BUY", "SELL"):

                entry_price = close

                stop_loss = calculate_stop_loss(
                    entry_price,
                    signal,
                    STOP_LOSS_PERCENT,
                )

                take_profit = calculate_take_profit(
                    entry_price,
                    signal,
                    stop_loss,
                    RISK_REWARD_RATIO,
                )

                position_size = calculate_position_size(
                    balance,
                    RISK_PERCENT,
                    entry_price,
                    stop_loss,
                )

                position = signal

    # =========================
    # Close at end of data
    # =========================

    if position is not None:

        final_price = df.iloc[-1]["close"]

        balance = close_trade(
            balance,
            trades,
            position,
            entry_price,
            final_price,
            position_size,
            "END OF DATA",
        )

    return balance, trades


def print_results(
    balance,
    trades
):

    total_profit = (
        balance - INITIAL_BALANCE
    )

    return_percent = (
        total_profit
        / INITIAL_BALANCE
    ) * 100

    print()
    print(
        "Forex Trading Bot - "
        "Risk Managed Backtest"
    )

    print("=" * 50)

    print(
        f"Initial balance: "
        f"${INITIAL_BALANCE:,.2f}"
    )

    print(
        f"Final balance:   "
        f"${balance:,.2f}"
    )

    print(
        f"Total P/L:       "
        f"${total_profit:,.2f}"
    )

    print(
        f"Return:          "
        f"{return_percent:.2f}%"
    )

    print(
        f"Completed trades: "
        f"{len(trades)}"
    )

    if not trades:

        print("No completed trades.")
        return

    winning = sum(
        1
        for trade in trades
        if trade["profit"] > 0
    )

    losing = sum(
        1
        for trade in trades
        if trade["profit"] < 0
    )

    win_rate = (
        winning / len(trades)
    ) * 100

    gross_profit = sum(
        trade["profit"]
        for trade in trades
        if trade["profit"] > 0
    )

    gross_loss = abs(
        sum(
            trade["profit"]
            for trade in trades
            if trade["profit"] < 0
        )
    )

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0
        else float("inf")
    )

    print(
        f"Winning trades:  "
        f"{winning}"
    )

    print(
        f"Losing trades:   "
        f"{losing}"
    )

    print(
        f"Win rate:        "
        f"{win_rate:.2f}%"
    )

    print(
        f"Profit factor:   "
        f"{profit_factor:.2f}"
    )


def main():

    print(
        "Running risk-managed backtest..."
    )

    df = get_test_data(500)

    balance, trades = backtest(df)

    print_results(
        balance,
        trades
    )

    # Save trades
    save_trades(trades)

    # Performance
    equity_curve = calculate_equity_curve(
        INITIAL_BALANCE,
        trades
    )

    max_drawdown = calculate_max_drawdown(
        equity_curve
    )

    print(
        f"Maximum Drawdown: "
        f"{max_drawdown:.2f}%"
    )

    plot_equity_curve(
        equity_curve
    )


if __name__ == "__main__":
    main()
import os
import pandas as pd
import matplotlib.pyplot as plt


def calculate_equity_curve(initial_balance, trades):
    equity = initial_balance
    curve = [equity]

    for trade in trades:
        equity += trade["profit"]
        curve.append(equity)

    return curve


def calculate_max_drawdown(equity_curve):
    series = pd.Series(equity_curve)

    peak = series.cummax()

    drawdown = (
        (series - peak) / peak
    ) * 100

    return drawdown.min()


def plot_equity_curve(
    equity_curve,
    filename="reports/equity_curve.png"
):
    os.makedirs("reports", exist_ok=True)

    plt.figure(figsize=(10, 5))

    plt.plot(
        equity_curve,
        linewidth=2
    )

    plt.title(
        "Forex Trading Bot - Equity Curve"
    )

    plt.xlabel("Completed Trade")
    plt.ylabel("Account Balance ($)")

    plt.grid(True)
    plt.tight_layout()

    plt.savefig(filename)
    plt.close()

    print(
        f"Equity curve saved to {filename}"
    )
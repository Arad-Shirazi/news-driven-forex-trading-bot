import os
import pandas as pd


def create_report(
    initial_balance,
    final_balance,
    trades,
    max_drawdown
):
    os.makedirs("reports", exist_ok=True)

    total_profit = final_balance - initial_balance

    if initial_balance != 0:
        total_return = (
            total_profit / initial_balance
        ) * 100
    else:
        total_return = 0

    total_trades = len(trades)

    winning_trades = sum(
        1
        for trade in trades
        if trade["profit"] > 0
    )

    losing_trades = sum(
        1
        for trade in trades
        if trade["profit"] < 0
    )

    if total_trades > 0:
        win_rate = (
            winning_trades
            / total_trades
        ) * 100
    else:
        win_rate = 0

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

    if gross_loss > 0:
        profit_factor = (
            gross_profit / gross_loss
        )
    else:
        profit_factor = 0

    report = f"""
FOREX TRADING BOT
PERFORMANCE REPORT
========================================

Initial Balance:
${initial_balance:,.2f}

Final Balance:
${final_balance:,.2f}

Total Profit / Loss:
${total_profit:,.2f}

Total Return:
{total_return:.2f}%

----------------------------------------

Total Trades:
{total_trades}

Winning Trades:
{winning_trades}

Losing Trades:
{losing_trades}

Win Rate:
{win_rate:.2f}%

Profit Factor:
{profit_factor:.2f}

Maximum Drawdown:
{max_drawdown:.2f}%

========================================
"""

    filename = "reports/backtest_report.txt"

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(report)

    print(report)

    print(
        f"Report saved to {filename}"
    )


def main():

    # Test report
    trades = [
        {"profit": -100},
        {"profit": 33.70},
    ]

    create_report(
        initial_balance=10_000,
        final_balance=9_933.70,
        trades=trades,
        max_drawdown=-1.0
    )


if __name__ == "__main__":
    main()
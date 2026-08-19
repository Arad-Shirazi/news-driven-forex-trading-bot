import MetaTrader5 as mt5
from datetime import datetime


# ============================================================
# RISK SETTINGS
# ============================================================

RISK_PER_TRADE_PERCENT = 1.0
MAX_DAILY_LOSS_PERCENT = 2.0
MAX_OPEN_POSITIONS = 1


# ============================================================
# ACCOUNT
# ============================================================

def get_account_info():

    account = mt5.account_info()

    if account is None:
        return None

    return {
        "balance": float(account.balance),
        "equity": float(account.equity),
        "currency": account.currency,
    }


# ============================================================
# TODAY'S CLOSED P/L
# ============================================================

def get_today_profit(symbol=None):

    now = datetime.now()

    start = datetime(
        now.year,
        now.month,
        now.day
    )

    deals = mt5.history_deals_get(
        start,
        now
    )

    if deals is None:
        return 0.0

    profit = 0.0

    for deal in deals:

        if symbol is not None:

            if deal.symbol != symbol:
                continue

        profit += float(deal.profit)
        profit += float(deal.swap)
        profit += float(deal.commission)

    return profit


# ============================================================
# FLOATING P/L
# ============================================================

def get_floating_profit(symbol=None):

    if symbol is None:

        positions = mt5.positions_get()

    else:

        positions = mt5.positions_get(
            symbol=symbol
        )

    if positions is None:
        return 0.0

    floating_profit = 0.0

    for position in positions:

        floating_profit += float(
            position.profit
        )

        floating_profit += float(
            position.swap
        )

    return floating_profit


# ============================================================
# OPEN POSITIONS
# ============================================================

def get_open_positions_count(symbol=None):

    if symbol is None:

        positions = mt5.positions_get()

    else:

        positions = mt5.positions_get(
            symbol=symbol
        )

    if positions is None:
        return 0

    return len(positions)


# ============================================================
# RISK CHECK
# ============================================================

def risk_allowed(symbol="EURUSD"):

    account = get_account_info()

    if account is None:

        print(
            "Could not read MT5 account."
        )

        return False

    balance = account["balance"]
    equity = account["equity"]
    currency = account["currency"]

    risk_per_trade = (
        balance
        * RISK_PER_TRADE_PERCENT
        / 100
    )

    max_daily_loss = (
        balance
        * MAX_DAILY_LOSS_PERCENT
        / 100
    )

    closed_profit = get_today_profit(
        symbol
    )

    floating_profit = get_floating_profit(
        symbol
    )

    total_today_pnl = (
        closed_profit
        + floating_profit
    )

    open_positions = (
        get_open_positions_count(
            symbol
        )
    )

    print(
        f"Balance: "
        f"{balance:.2f} {currency}"
    )

    print(
        f"Equity: "
        f"{equity:.2f} {currency}"
    )

    print(
        f"Risk per trade: "
        f"{risk_per_trade:.2f} {currency}"
    )

    print(
        f"Maximum daily loss: "
        f"{max_daily_loss:.2f} {currency}"
    )

    print(
        f"Closed P/L today: "
        f"{closed_profit:.2f} {currency}"
    )

    print(
        f"Floating P/L: "
        f"{floating_profit:.2f} {currency}"
    )

    print(
        f"Total today's P/L: "
        f"{total_today_pnl:.2f} {currency}"
    )

    print(
        f"Open positions: "
        f"{open_positions}"
    )

    # ========================================================
    # DAILY LOSS PROTECTION
    # ========================================================

    if total_today_pnl <= -max_daily_loss:

        print()
        print(
            "DAILY LOSS LIMIT REACHED!"
        )

        print(
            "Trading disabled for today."
        )

        return False

    # ========================================================
    # POSITION PROTECTION
    # ========================================================

    if open_positions >= MAX_OPEN_POSITIONS:

        print()
        print(
            "Maximum open positions reached."
        )

        return False

    return True
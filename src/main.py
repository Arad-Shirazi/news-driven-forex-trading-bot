import time
import MetaTrader5 as mt5

from news_analyzer import scan_all_markets, select_best_opportunity
from order_manager import send_demo_order
from risk_guard import risk_allowed


# ============================================================
# SETTINGS
# ============================================================

SCAN_INTERVAL = 3600

RISK_PER_TRADE = 0.01
TARGET_PROFIT = 0.02
MAX_DAILY_LOSS = 0.02
MAX_OPEN_POSITIONS = 1


# ============================================================
# MT5 SYMBOL MAPPING
# ============================================================

MARKET_SYMBOLS = {
    "EURUSD": "EURUSD",
    "GBPUSD": "GBPUSD",
    "USDJPY": "USDJPY",
    "XAUUSD": "XAUUSD",
    "USOIL": "WTI",
}


# ============================================================
# MT5 CONNECTION
# ============================================================

def connect_mt5():

    if mt5.initialize():

        print("MT5 connected successfully")
        return True

    print("MT5 initialization failed.")
    print("Error:", mt5.last_error())

    return False


# ============================================================
# FIND SYMBOL
# ============================================================

def find_mt5_symbol(market):

    candidates = []

    preferred = MARKET_SYMBOLS.get(
        market,
        market
    )

    candidates.append(preferred)

    candidates.extend([
        market,
        f"{market}.",
        f"{market}m",
        f"{market}a",
        f"{market}c",
        f"{market}pro",
        f"{market}_",
    ])

    if market == "USOIL":

        candidates.extend([
            "WTI",
            "WTI.",
            "WTI.a",
            "WTI.m",
            "USOIL",
            "USOIL.",
            "USOILm",
            "XTIUSD",
        ])

    if market == "XAUUSD":

        candidates.extend([
            "XAUUSD",
            "XAUUSD.",
            "XAUUSDm",
            "GOLD",
            "GOLD.",
        ])

    checked = set()

    for symbol in candidates:

        if symbol in checked:
            continue

        checked.add(symbol)

        info = mt5.symbol_info(symbol)

        if info is None:
            continue

        if not info.visible:

            mt5.symbol_select(
                symbol,
                True
            )

        print(
            f"{market} -> {symbol} OK"
        )

        return symbol

    print(
        f"{market} -> NO MT5 SYMBOL FOUND"
    )

    return None


# ============================================================
# RESOLVE SYMBOLS
# ============================================================

def resolve_symbols():

    print()
    print("Checking MT5 market symbols...")

    resolved = {}

    for market in MARKET_SYMBOLS:

        symbol = find_mt5_symbol(market)

        if symbol is not None:

            resolved[market] = symbol

    return resolved


# ============================================================
# ACCOUNT
# ============================================================

def print_account_info():

    account = mt5.account_info()

    if account is None:

        print(
            "Could not read MT5 account."
        )

        return

    print()
    print("ACCOUNT")
    print("-" * 60)

    print(
        f"Balance: {account.balance:.2f}"
    )

    print(
        f"Equity: {account.equity:.2f}"
    )

    print(
        f"Profit: {account.profit:.2f}"
    )


# ============================================================
# OPEN POSITIONS
# ============================================================

def get_open_positions():

    positions = mt5.positions_get()

    if positions is None:
        return []

    return list(positions)


# ============================================================
# POSITION LIMIT
# ============================================================

def position_limit_reached():

    positions = get_open_positions()

    count = len(positions)

    print(
        f"Open positions: {count}"
    )

    if count >= MAX_OPEN_POSITIONS:

        print(
            "Maximum open positions reached."
        )

        return True

    return False


# ============================================================
# NEWS SCAN OUTPUT
# ============================================================

def print_scan(results, best):

    print()
    print("TODAY'S NEWS MARKET SCAN")
    print("=" * 60)

    for market, data in results.items():

        score = data["score"]
        confidence = data["confidence"]

        if score > 0:
            signal = "BUY"

        elif score < 0:
            signal = "SELL"

        else:
            signal = "HOLD"

        print()
        print(market)

        print(
            f"Signal: {signal}"
        )

        print(
            f"News Score: {score:+d}"
        )

        print(
            f"Confidence: {confidence:.0f}%"
        )

        print(
            f"Relevant News: "
            f"{data['article_count']}"
        )

        print(
            f"Important News: "
            f"{data['important_news']}"
        )

        print(
            f"Directional Score: "
            f"{data['directional_score']:+.2f}"
        )

    print()
    print("=" * 60)

    if best is None:

        print(
            "BEST OPPORTUNITY: NONE"
        )

        print(
            "NO TRADE TODAY"
        )

        print("=" * 60)

        return

    direction = (
        "BUY"
        if best["score"] > 0
        else "SELL"
    )

    print("BEST OPPORTUNITY")

    print(
        f"{best['market']} → {direction}"
    )

    print(
        f"Confidence: "
        f"{best['confidence']:.0f}%"
    )

    print(
        f"News Score: "
        f"{best['score']:+d}"
    )

    print(
        f"Directional Score: "
        f"{best['directional_score']:+.2f}"
    )

    print(
        f"Important News: "
        f"{best['important_news']}"
    )

    print(
        f"Opportunity Strength: "
        f"{best['opportunity_strength']:.2f}"
    )

    print("=" * 60)


# ============================================================
# TOP NEWS
# ============================================================

def print_top_news(results, best):

    if best is None:
        return

    market = best["market"]

    data = results[market]

    articles = data.get(
        "news",
        []
    )

    print()
    print(
        f"TOP NEWS FOR {market}"
    )

    print("-" * 60)

    for article in articles[:5]:

        title = article.get(
            "title",
            "Unknown"
        )

        sentiment = article.get(
            "_sentiment",
            article.get(
                "overall_sentiment_score",
                0
            )
        )

        directional = article.get(
            "_direction",
            article.get(
                "_directional_effect",
                0
            )
        )

        print()
        print(
            f"Title: {title}"
        )

        print(
            f"Sentiment: "
            f"{float(sentiment):+.4f}"
        )

        print(
            f"Directional Effect: "
            f"{int(directional):+d}"
        )


# ============================================================
# EXECUTE TRADE
# ============================================================

def execute_best_opportunity(
    best,
    resolved_symbols
):

    if best is None:

        print()
        print(
            "No sufficiently strong news opportunity."
        )

        return

    market = best["market"]

    score = best["score"]

    confidence = best["confidence"]

    direction = (
        "BUY"
        if score > 0
        else "SELL"
    )

    print()
    print("TRADE DECISION")
    print("-" * 60)

    print(
        f"Selected market: {market}"
    )

    print(
        f"Direction: {direction}"
    )

    print(
        f"Confidence: {confidence:.0f}%"
    )

    # --------------------------------------------------------
    # SYMBOL
    # --------------------------------------------------------

    symbol = resolved_symbols.get(
        market
    )

    if symbol is None:

        print(
            f"MT5 symbol for {market} "
            f"was not found."
        )

        print("TRADE CANCELLED.")

        return

    print(
        f"MT5 symbol: {symbol}"
    )

    # --------------------------------------------------------
    # CHECK OPEN POSITIONS FIRST
    # --------------------------------------------------------

    print()
    print("POSITION CHECK")
    print("-" * 60)

    positions = get_open_positions()

    open_count = len(positions)

    print(
        f"Open positions: {open_count}"
    )

    if open_count >= MAX_OPEN_POSITIONS:

        print(
            "Maximum open positions reached."
        )

        print(
            "TRADE BLOCKED."
        )

        return

    # --------------------------------------------------------
    # RISK GUARD
    # --------------------------------------------------------

    print()
    print("RISK CHECK")
    print("-" * 60)

    print(
        f"Risk per trade: "
        f"{RISK_PER_TRADE * 100:.0f}%"
    )

    print(
        f"Maximum daily loss: "
        f"{MAX_DAILY_LOSS * 100:.0f}%"
    )

    allowed = risk_allowed(
        symbol
    )

    if not allowed:

        print()
        print(
            "TRADE BLOCKED BY RISK GUARD"
        )

        return

    # --------------------------------------------------------
    # FINAL POSITION CHECK
    # --------------------------------------------------------
    #
    # risk_allowed() must NOT open a position.
    # We verify again immediately before sending.
    # --------------------------------------------------------

    positions_after_risk = (
        get_open_positions()
    )

    if len(positions_after_risk) >= MAX_OPEN_POSITIONS:

        print()
        print(
            "A position appeared during "
            "risk validation."
        )

        print(
            "TRADE BLOCKED."
        )

        return

    # --------------------------------------------------------
    # SEND ORDER
    # --------------------------------------------------------

    print()
    print(
        f"Sending {direction} "
        f"order for {symbol}..."
    )

    result = send_demo_order(
        symbol=symbol,
        direction=direction
    )

    if result is None:

        print()
        print(
            "ORDER RESULT: None"
        )

        return

    print()
    print("ORDER RESULT")
    print("-" * 60)

    print(result)

    # --------------------------------------------------------
    # MT5 RETCODES
    # --------------------------------------------------------

    if result.retcode == mt5.TRADE_RETCODE_DONE:

        print()
        print(
            "ORDER EXECUTED SUCCESSFULLY"
        )

        print(
            f"Ticket: "
            f"{result.order}"
        )

    elif result.retcode == mt5.TRADE_RETCODE_PLACED:

        print()
        print(
            "ORDER PLACED SUCCESSFULLY"
        )

        print(
            f"Ticket: "
            f"{result.order}"
        )

    else:

        print()
        print(
            "ORDER WAS NOT EXECUTED"
        )

        print(
            f"Retcode: "
            f"{result.retcode}"
        )

        print(
            f"Comment: "
            f"{result.comment}"
        )


# ============================================================
# ONE CYCLE
# ============================================================

def run_cycle(
    cycle,
    resolved_symbols
):

    print()
    print("=" * 60)

    print(
        f"NEWS-ONLY TRADING CYCLE #{cycle}"
    )

    print("=" * 60)

    # Account

    print_account_info()

    # News

    print()
    print(
        "Scanning today's market news..."
    )

    results = scan_all_markets()

    # Best opportunity

    best = select_best_opportunity(
        results
    )

    # Output

    print_scan(
        results,
        best
    )

    print_top_news(
        results,
        best
    )

    # Execute

    execute_best_opportunity(
        best,
        resolved_symbols
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)

    print(
        "Starting News-Only Forex Trading Bot"
    )

    print("=" * 60)

    print("Account: DEMO")

    print("Strategy: NEWS ONLY")

    print(
        "Markets:"
    )

    print(
        "EURUSD / GBPUSD / USDJPY / "
        "XAUUSD / USOIL"
    )

    print(
        "Risk per trade: 1%"
    )

    print(
        "Target profit: 2%"
    )

    print(
        "Maximum daily loss: 2%"
    )

    print(
        "Maximum open positions: 1"
    )

    print(
        f"Scan interval: "
        f"{SCAN_INTERVAL} seconds"
    )

    print("=" * 60)

    # --------------------------------------------------------
    # CONNECT
    # --------------------------------------------------------

    if not connect_mt5():
        return

    # --------------------------------------------------------
    # SYMBOLS
    # --------------------------------------------------------

    resolved_symbols = resolve_symbols()

    if not resolved_symbols:

        print()
        print(
            "No tradable MT5 symbols found."
        )

        mt5.shutdown()

        return

    cycle = 1

    while True:

        try:

            # ------------------------------------------------
            # CHECK TERMINAL
            # ------------------------------------------------

            if not mt5.terminal_info():

                mt5.shutdown()

                if not connect_mt5():

                    time.sleep(
                        SCAN_INTERVAL
                    )

                    continue

                resolved_symbols = (
                    resolve_symbols()
                )

            # ------------------------------------------------
            # RUN
            # ------------------------------------------------

            run_cycle(
                cycle,
                resolved_symbols
            )

            # ------------------------------------------------
            # SHUTDOWN
            # ------------------------------------------------

            mt5.shutdown()

            print()
            print(
                f"Next market scan in "
                f"{SCAN_INTERVAL // 60} minutes..."
            )

            time.sleep(
                SCAN_INTERVAL
            )

            cycle += 1

            # ------------------------------------------------
            # RECONNECT
            # ------------------------------------------------

            if not connect_mt5():

                time.sleep(
                    SCAN_INTERVAL
                )

                continue

            resolved_symbols = (
                resolve_symbols()
            )

        except KeyboardInterrupt:

            print()
            print(
                "Bot stopped by user."
            )

            try:
                mt5.shutdown()
            except Exception:
                pass

            break

        except Exception as error:

            print()
            print(
                "BOT ERROR:"
            )

            print(error)

            try:
                mt5.shutdown()
            except Exception:
                pass

            print()
            print(
                f"Retrying in "
                f"{SCAN_INTERVAL} seconds..."
            )

            time.sleep(
                SCAN_INTERVAL
            )

            try:

                if connect_mt5():

                    resolved_symbols = (
                        resolve_symbols()
                    )

            except Exception:
                pass


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()
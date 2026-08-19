import MetaTrader5 as mt5

from trade_logger import log_trade


RISK_PERCENT = 1.0
REWARD_RISK_RATIO = 2.0

STOP_DISTANCE_PERCENT = 0.5


def get_account_info():

    return mt5.account_info()


def calculate_volume(
    symbol,
    entry_price,
    stop_loss,
    risk_money
):

    info = mt5.symbol_info(symbol)

    if info is None:
        return None

    tick_size = info.trade_tick_size
    tick_value = info.trade_tick_value

    if tick_size <= 0 or tick_value <= 0:
        print("Invalid tick information.")
        return None

    price_distance = abs(
        entry_price - stop_loss
    )

    ticks = price_distance / tick_size

    if ticks <= 0:
        return None

    risk_per_lot = ticks * tick_value

    if risk_per_lot <= 0:
        return None

    volume = risk_money / risk_per_lot

    volume_min = info.volume_min
    volume_max = info.volume_max
    volume_step = info.volume_step

    volume = max(
        volume,
        volume_min
    )

    volume = min(
        volume,
        volume_max
    )

    volume = (
        volume // volume_step
    ) * volume_step

    volume = round(
        volume,
        2
    )

    if volume < volume_min:
        volume = volume_min

    return volume


def calculate_order(
    symbol,
    direction,
    risk_money
):

    info = mt5.symbol_info(symbol)
    tick = mt5.symbol_info_tick(symbol)

    if info is None or tick is None:
        return None

    if direction == "BUY":

        price = tick.ask

        order_type = (
            mt5.ORDER_TYPE_BUY
        )

        stop_loss = (
            price
            * (
                1
                - STOP_DISTANCE_PERCENT / 100
            )
        )

    else:

        price = tick.bid

        order_type = (
            mt5.ORDER_TYPE_SELL
        )

        stop_loss = (
            price
            * (
                1
                + STOP_DISTANCE_PERCENT / 100
            )
        )

    volume = calculate_volume(
        symbol=symbol,
        entry_price=price,
        stop_loss=stop_loss,
        risk_money=risk_money
    )

    if volume is None:
        return None

    sl_distance = abs(
        price - stop_loss
    )

    tp_distance = (
        sl_distance
        * REWARD_RISK_RATIO
    )

    if direction == "BUY":

        take_profit = (
            price + tp_distance
        )

    else:

        take_profit = (
            price - tp_distance
        )

    digits = info.digits

    return {
        "price": round(
            price,
            digits
        ),
        "stop_loss": round(
            stop_loss,
            digits
        ),
        "take_profit": round(
            take_profit,
            digits
        ),
        "volume": volume,
        "order_type": order_type
    }


def get_filling_mode(info):

    filling_mode = info.filling_mode

    if filling_mode & 1:

        return mt5.ORDER_FILLING_FOK

    if filling_mode & 2:

        return mt5.ORDER_FILLING_IOC

    return mt5.ORDER_FILLING_RETURN


def send_demo_order(
    symbol="EURUSD",
    direction="BUY"
):

    if not mt5.initialize():

        print(
            "MT5 initialization failed"
        )

        print(
            "Error:",
            mt5.last_error()
        )

        return None

    account = get_account_info()

    if account is None:

        print(
            "Could not read account."
        )

        mt5.shutdown()

        return None

    info = mt5.symbol_info(
        symbol
    )

    if info is None:

        print(
            f"{symbol} not found."
        )

        mt5.shutdown()

        return None

    if not info.visible:

        if not mt5.symbol_select(
            symbol,
            True
        ):

            print(
                "Could not select symbol."
            )

            mt5.shutdown()

            return None

    balance = float(
        account.balance
    )

    currency = account.currency

    risk_money = (
        balance
        * RISK_PERCENT
        / 100
    )

    order = calculate_order(
        symbol=symbol,
        direction=direction,
        risk_money=risk_money
    )

    if order is None:

        mt5.shutdown()

        return None

    price = order["price"]
    stop_loss = order["stop_loss"]
    take_profit = order["take_profit"]
    volume = order["volume"]
    order_type = order["order_type"]

    filling = get_filling_mode(
        info
    )

    print()
    print("DEMO ORDER")
    print("=" * 55)

    print(
        f"Balance: "
        f"{balance:.2f} {currency}"
    )

    print(
        f"Risk: "
        f"{risk_money:.2f} {currency}"
    )

    print(
        f"Risk percentage: "
        f"{RISK_PERCENT:.2f}%"
    )

    print(
        f"Reward/Risk: "
        f"1:{REWARD_RISK_RATIO:.0f}"
    )

    print(
        f"Symbol: {symbol}"
    )

    print(
        f"Direction: {direction}"
    )

    print(
        f"Price: {price:.{info.digits}f}"
    )

    print(
        f"Volume: {volume:.2f}"
    )

    print(
        f"Stop Loss: "
        f"{stop_loss:.{info.digits}f}"
    )

    print(
        f"Take Profit: "
        f"{take_profit:.{info.digits}f}"
    )

    print(
        f"Filling mode: {filling}"
    )

    request = {

        "action":
            mt5.TRADE_ACTION_DEAL,

        "symbol":
            symbol,

        "volume":
            volume,

        "type":
            order_type,

        "price":
            price,

        "sl":
            stop_loss,

        "tp":
            take_profit,

        "deviation":
            20,

        "magic":
            123456,

        "comment":
            "Forex Bot Demo",

        "type_time":
            mt5.ORDER_TIME_GTC,

        "type_filling":
            filling
    }

    print()
    print(
        "Sending DEMO order..."
    )

    result = mt5.order_send(
        request
    )

    if result is None:

        print(
            "Order failed."
        )

        print(
            "Error:",
            mt5.last_error()
        )

        mt5.shutdown()

        return None

    print()
    print("ORDER RESULT")
    print("=" * 55)

    print(
        f"Retcode: "
        f"{result.retcode}"
    )

    print(
        f"Comment: "
        f"{result.comment}"
    )

    if result.retcode == 10009:

        print()
        print("SUCCESS!")
        print("Demo order executed.")

        print(
            f"Order ID: "
            f"{result.order}"
        )

        print(
            f"Deal ID: "
            f"{result.deal}"
        )

        # -----------------------------------------
        # Save executed trade
        # -----------------------------------------

        log_trade(
            symbol=symbol,
            direction=direction,
            volume=volume,
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            balance=balance,
            status="OPEN"
        )

        print(
            "Trade saved to data/trades.csv"
        )

    else:

        print(
            "Order was not executed."
        )

    mt5.shutdown()

    return result
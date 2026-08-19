def calculate_position_size(
    balance,
    risk_percent,
    entry_price,
    stop_loss_price
):
    """
    Calculate position size based on
    the amount of money we are willing to risk.
    """

    risk_amount = balance * (risk_percent / 100)

    price_difference = abs(
        entry_price - stop_loss_price
    )

    if price_difference == 0:
        raise ValueError(
            "Entry price and stop-loss price "
            "cannot be the same."
        )

    position_size = (
        risk_amount / price_difference
    )

    return position_size


def calculate_stop_loss(
    entry_price,
    direction,
    stop_loss_percent=1.0
):
    """
    Calculate stop-loss price.
    """

    if direction == "BUY":
        return entry_price * (
            1 - stop_loss_percent / 100
        )

    if direction == "SELL":
        return entry_price * (
            1 + stop_loss_percent / 100
        )

    raise ValueError(
        "Direction must be BUY or SELL."
    )


def calculate_take_profit(
    entry_price,
    direction,
    stop_loss_price,
    risk_reward_ratio=2.0
):
    """
    Calculate take-profit using
    a risk/reward ratio.
    """

    risk = abs(
        entry_price - stop_loss_price
    )

    if direction == "BUY":
        return entry_price + (
            risk * risk_reward_ratio
        )

    if direction == "SELL":
        return entry_price - (
            risk * risk_reward_ratio
        )

    raise ValueError(
        "Direction must be BUY or SELL."
    )
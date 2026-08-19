import os
import requests

from datetime import datetime, timezone

from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

API_KEY = os.getenv(
    "ALPHA_VANTAGE_API_KEY"
)

BASE_URL = (
    "https://www.alphavantage.co/query"
)


# ============================================================
# MARKETS
# ============================================================

MARKETS = {

    "EURUSD": [
        "euro",
        "eur",
        "eurozone",
        "ecb",
        "european central bank",
        "eurozone inflation",
        "eurozone gdp",
        "germany inflation",
        "germany gdp",
        "federal reserve",
        "fed",
        "fomc",
        "dollar",
        "usd",
        "us inflation",
        "us cpi",
        "us gdp",
        "nonfarm payroll",
        "nfp",
        "interest rate",
        "rate cut",
        "rate hike",
        "monetary policy"
    ],

    "GBPUSD": [
        "pound",
        "sterling",
        "gbp",
        "bank of england",
        "boe",
        "uk economy",
        "uk inflation",
        "uk cpi",
        "uk gdp",
        "uk employment",
        "federal reserve",
        "fed",
        "fomc",
        "dollar",
        "usd",
        "us inflation",
        "us cpi",
        "us gdp",
        "nonfarm payroll",
        "nfp",
        "interest rate",
        "rate cut",
        "rate hike",
        "monetary policy"
    ],

    "USDJPY": [
        "yen",
        "japanese yen",
        "japan",
        "japanese economy",
        "japan inflation",
        "japan cpi",
        "japan gdp",
        "bank of japan",
        "boj",
        "federal reserve",
        "fed",
        "fomc",
        "dollar",
        "usd",
        "us inflation",
        "us cpi",
        "us gdp",
        "nonfarm payroll",
        "nfp",
        "interest rate",
        "rate cut",
        "rate hike",
        "monetary policy"
    ],

    "XAUUSD": [
        "gold",
        "gold price",
        "bullion",
        "precious metals",
        "safe haven",
        "federal reserve",
        "fed",
        "fomc",
        "dollar",
        "usd",
        "dxy",
        "inflation",
        "cpi",
        "interest rate",
        "rate cut",
        "rate hike",
        "geopolitical",
        "war",
        "conflict"
    ],

    "USOIL": [
        "oil",
        "crude oil",
        "oil price",
        "wti",
        "brent",
        "opec",
        "opec+",
        "eia",
        "oil inventories",
        "crude inventories",
        "oil production",
        "oil supply",
        "oil demand",
        "energy supply",
        "energy demand",
        "middle east",
        "iran",
        "iraq",
        "saudi arabia",
        "russia",
        "ukraine",
        "shipping",
        "strait of hormuz",
        "geopolitical"
    ]
}


# ============================================================
# HIGH IMPACT TERMS
# ============================================================

HIGH_IMPACT = [

    "federal reserve",
    "fed",
    "fomc",

    "ecb",
    "european central bank",

    "bank of england",
    "boe",

    "bank of japan",
    "boj",

    "opec",
    "opec+",
    "eia",

    "nonfarm payroll",
    "nfp",

    "cpi",
    "inflation",

    "interest rate",
    "rate cut",
    "rate hike",

    "monetary policy",

    "oil inventories",
    "crude inventories",
    "oil production",
    "oil supply",
    "oil demand",

    "war",
    "conflict",
    "geopolitical",

    "strait of hormuz"
]


# ============================================================
# BULLISH TERMS
# ============================================================

BULLISH_TERMS = [

    "supply disruption",
    "supply shortage",

    "production cut",
    "production cuts",

    "output cut",
    "output cuts",

    "sanctions",

    "shipping disruption",

    "supply concerns",
    "supply shock",

    "rate cut",
    "rate cuts",

    "lower interest rates",

    "dollar weakness",
    "weaker dollar",

    "better than expected",
    "beats expectations",

    "positive surprise"
]


# ============================================================
# BEARISH TERMS
# ============================================================

BEARISH_TERMS = [

    "oversupply",
    "supply glut",

    "production increase",
    "production increases",

    "output increase",
    "output increases",

    "demand weakness",
    "weak demand",
    "demand slowdown",

    "rate hike",
    "rate hikes",

    "higher interest rates",

    "dollar strength",
    "stronger dollar",

    "economic slowdown",
    "recession",

    "worse than expected",
    "misses expectations",

    "negative surprise"
]


# ============================================================
# EXCLUDED TERMS
# ============================================================

EXCLUDED_TERMS = [

    "earnings call",
    "earnings transcript",
    "quarterly earnings",
    "quarterly results",

    "shareholders",
    "securities fraud",
    "lawsuit",
    "class action",

    "bitcoin",
    "crypto",
    "cryptocurrency",
    "ethereum",
    "xrp",
    "dogecoin",
    "nft",
    "mstr"
]


# ============================================================
# GET REAL NEWS
# ============================================================

def get_all_news(limit=50):

    if not API_KEY:

        raise RuntimeError(
            "ALPHA_VANTAGE_API_KEY is missing "
            "from .env"
        )

    params = {

        "function":
            "NEWS_SENTIMENT",

        "tickers":
            "FOREX:USD",

        "sort":
            "LATEST",

        "limit":
            limit,

        "apikey":
            API_KEY
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if "feed" not in data:

        if "Information" in data:

            raise RuntimeError(
                data["Information"]
            )

        if "Note" in data:

            raise RuntimeError(
                data["Note"]
            )

        raise RuntimeError(
            f"Unexpected API response: {data}"
        )

    return data["feed"]


# ============================================================
# ARTICLE TEXT
# ============================================================

def article_text(article):

    title = article.get(
        "title",
        ""
    )

    summary = article.get(
        "summary",
        ""
    )

    return (
        f"{title} {summary}"
    ).lower()


# ============================================================
# EXCLUDED ARTICLE?
# ============================================================

def is_excluded(article):

    text = article_text(
        article
    )

    return any(
        term in text
        for term in EXCLUDED_TERMS
    )


# ============================================================
# FRESHNESS
# ============================================================

def freshness_weight(article):

    timestamp = article.get(
        "time_published",
        ""
    )

    if not timestamp:

        return 0.7

    try:

        published = datetime.strptime(
            timestamp[:15],
            "%Y%m%dT%H%M%S"
        ).replace(
            tzinfo=timezone.utc
        )

        now = datetime.now(
            timezone.utc
        )

        hours = (
            now - published
        ).total_seconds() / 3600

        if hours <= 6:
            return 1.0

        if hours <= 12:
            return 0.9

        if hours <= 24:
            return 0.75

        if hours <= 48:
            return 0.55

        if hours <= 72:
            return 0.35

        return 0.2

    except Exception:

        return 0.7


# ============================================================
# RELEVANCE
# ============================================================

def calculate_relevance(
    article,
    market
):

    if market not in MARKETS:

        return 0

    if is_excluded(article):

        return 0

    text = article_text(
        article
    )

    score = 0

    # --------------------------------------------------------
    # GENERAL MARKET KEYWORDS
    # --------------------------------------------------------

    for keyword in MARKETS[market]:

        if keyword in text:

            score += 1

    if score == 0:

        return 0

    # --------------------------------------------------------
    # HIGH IMPACT
    # --------------------------------------------------------

    for term in HIGH_IMPACT:

        if term in text:

            score += 4

    # --------------------------------------------------------
    # DIRECT MARKET TERMS
    # --------------------------------------------------------

    direct_terms = {

        "EURUSD": [
            "euro",
            "eurozone",
            "ecb",
            "european central bank"
        ],

        "GBPUSD": [
            "pound",
            "sterling",
            "bank of england",
            "boe"
        ],

        "USDJPY": [
            "yen",
            "japan",
            "bank of japan",
            "boj"
        ],

        "XAUUSD": [
            "gold",
            "gold price",
            "bullion"
        ],

        "USOIL": [
            "oil",
            "crude oil",
            "wti",
            "brent",
            "opec",
            "opec+",
            "eia"
        ]
    }

    for term in direct_terms[market]:

        if term in text:

            score += 5

    return score


# ============================================================
# DIRECTIONAL EFFECT
# ============================================================

def directional_effect(
    article,
    market
):

    text = article_text(
        article
    )

    effect = 0

    # --------------------------------------------------------
    # GENERAL BULLISH / BEARISH
    # --------------------------------------------------------

    for term in BULLISH_TERMS:

        if term in text:

            effect += 1

    for term in BEARISH_TERMS:

        if term in text:

            effect -= 1

    # --------------------------------------------------------
    # EURUSD
    # --------------------------------------------------------

    if market == "EURUSD":

        if (
            "dollar weakness" in text
            or "weaker dollar" in text
        ):

            effect += 2

        if (
            "dollar strength" in text
            or "stronger dollar" in text
        ):

            effect -= 2

        if (
            "ecb rate hike" in text
            or "ecb raises rates" in text
        ):

            effect += 2

        if (
            "ecb rate cut" in text
            or "ecb cuts rates" in text
        ):

            effect -= 2

    # --------------------------------------------------------
    # GBPUSD
    # --------------------------------------------------------

    if market == "GBPUSD":

        if (
            "dollar weakness" in text
            or "weaker dollar" in text
        ):

            effect += 2

        if (
            "dollar strength" in text
            or "stronger dollar" in text
        ):

            effect -= 2

        if (
            "boe rate hike" in text
            or "bank of england raises rates"
            in text
        ):

            effect += 2

        if (
            "boe rate cut" in text
            or "bank of england cuts rates"
            in text
        ):

            effect -= 2

    # --------------------------------------------------------
    # USDJPY
    # --------------------------------------------------------

    if market == "USDJPY":

        if (
            "dollar strength" in text
            or "stronger dollar" in text
            or "rate hike" in text
            or "higher interest rates" in text
        ):

            effect += 2

        if (
            "dollar weakness" in text
            or "weaker dollar" in text
            or "rate cut" in text
            or "lower interest rates" in text
        ):

            effect -= 2

        if (
            "boj rate hike" in text
            or "bank of japan raises rates"
            in text
        ):

            effect -= 2

        if (
            "boj rate cut" in text
            or "bank of japan cuts rates"
            in text
        ):

            effect += 2

    # --------------------------------------------------------
    # GOLD
    # --------------------------------------------------------

    if market == "XAUUSD":

        if (
            "dollar weakness" in text
            or "weaker dollar" in text
            or "rate cut" in text
            or "lower interest rates" in text
            or "safe haven" in text
            or "geopolitical" in text
            or "war" in text
            or "conflict" in text
        ):

            effect += 2

        if (
            "dollar strength" in text
            or "stronger dollar" in text
            or "rate hike" in text
            or "higher interest rates" in text
        ):

            effect -= 2

    # --------------------------------------------------------
    # OIL
    # --------------------------------------------------------

    if market == "USOIL":

        bullish_oil = [

            "supply disruption",
            "supply shortage",
            "production cut",
            "production cuts",
            "output cut",
            "output cuts",
            "sanctions",
            "shipping disruption",
            "supply concerns",
            "supply shock",
            "war",
            "conflict",
            "strait of hormuz"
        ]

        bearish_oil = [

            "oversupply",
            "supply glut",
            "production increase",
            "production increases",
            "output increase",
            "output increases",
            "demand weakness",
            "weak demand",
            "demand slowdown"
        ]

        for term in bullish_oil:

            if term in text:

                effect += 3

        for term in bearish_oil:

            if term in text:

                effect -= 3

    return effect


# ============================================================
# FILTER NEWS
# ============================================================

def filter_market_news(
    all_news,
    market
):

    results = []

    for article in all_news:

        relevance = calculate_relevance(
            article,
            market
        )

        if relevance <= 0:

            continue

        try:

            sentiment = float(
                article.get(
                    "overall_sentiment_score",
                    0
                ) or 0
            )

        except Exception:

            sentiment = 0.0

        freshness = freshness_weight(
            article
        )

        item = dict(
            article
        )

        item["_relevance"] = (
            relevance
        )

        item["_sentiment"] = (
            sentiment
        )

        item["_freshness"] = (
            freshness
        )

        item["_direction"] = (
            directional_effect(
                article,
                market
            )
        )

        results.append(
            item
        )

    results.sort(
        key=lambda x:
            x["_relevance"]
            * x["_freshness"],
        reverse=True
    )

    return results


# ============================================================
# MARKET SCORE
# ============================================================

def calculate_market_score(
    articles,
    market
):

    if not articles:

        return {

            "score": 0,

            "confidence": 0,

            "average_sentiment": 0,

            "article_count": 0,

            "directional_score": 0,

            "important_news": 0
        }

    weighted_sentiment = 0

    total_weight = 0

    directional_score = 0

    important_count = 0

    # --------------------------------------------------------
    # ANALYZE ARTICLES
    # --------------------------------------------------------

    for article in articles:

        relevance = min(
            article["_relevance"],
            20
        )

        freshness = article[
            "_freshness"
        ]

        sentiment = article[
            "_sentiment"
        ]

        weight = (
            relevance
            * freshness
        )

        weighted_sentiment += (
            sentiment
            * weight
        )

        total_weight += weight

        effect = article[
            "_direction"
        ]

        directional_score += (
            effect
            * freshness
        )

        if relevance >= 10:

            important_count += 1

    # --------------------------------------------------------
    # NO WEIGHT
    # --------------------------------------------------------

    if total_weight == 0:

        return {

            "score": 0,

            "confidence": 0,

            "average_sentiment": 0,

            "article_count":
                len(articles),

            "directional_score": 0,

            "important_news": 0
        }

    # --------------------------------------------------------
    # SENTIMENT
    # --------------------------------------------------------

    average_sentiment = (
        weighted_sentiment
        / total_weight
    )

    # --------------------------------------------------------
    # COMBINED SIGNAL
    # --------------------------------------------------------

    combined = (
        average_sentiment * 10
        + directional_score
    )

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    if combined >= 5:

        score = 3

    elif combined >= 2.5:

        score = 2

    elif combined >= 1:

        score = 1

    elif combined <= -5:

        score = -3

    elif combined <= -2.5:

        score = -2

    elif combined <= -1:

        score = -1

    else:

        score = 0

    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    sentiment_strength = min(
        abs(average_sentiment) * 200,
        45
    )

    directional_strength = min(
        abs(directional_score) * 8,
        30
    )

    article_strength = min(
        len(articles) * 4,
        20
    )

    important_strength = min(
        important_count * 8,
        20
    )

    confidence = min(

        sentiment_strength
        + directional_strength
        + article_strength
        + important_strength,

        100
    )

    # --------------------------------------------------------
    # IMPORTANT NEWS BONUS
    #
    # A strong directional macro event can be enough
    # even if average sentiment is close to zero.
    # --------------------------------------------------------

    if (
        abs(directional_score) >= 2
        and important_count >= 2
    ):

        confidence += 5

    # Strong direct market news.
    if (
        abs(directional_score) >= 3
        and important_count >= 1
    ):

        confidence += 5

    confidence = min(
        confidence,
        100
    )

    return {

        "score": score,

        "confidence": confidence,

        "average_sentiment":
            average_sentiment,

        "article_count":
            len(articles),

        "directional_score":
            directional_score,

        "important_news":
            important_count
    }


# ============================================================
# SCAN ALL MARKETS
# ============================================================

def scan_all_markets():

    all_news = get_all_news()

    results = {}

    for market in MARKETS:

        articles = filter_market_news(
            all_news,
            market
        )

        analysis = calculate_market_score(
            articles,
            market
        )

        results[market] = {

            **analysis,

            "news":
                articles
        }

    return results


# ============================================================
# SELECT BEST OPPORTUNITY
# ============================================================

def select_best_opportunity(
    results
):

    candidates = []

    for market, data in results.items():

        score = data[
            "score"
        ]

        confidence = data[
            "confidence"
        ]

        directional = data[
            "directional_score"
        ]

        important = data[
            "important_news"
        ]

        article_count = data[
            "article_count"
        ]

        # ----------------------------------------------------
        # HOLD
        # ----------------------------------------------------

        if score == 0:

            continue

        # ----------------------------------------------------
        # MINIMUM QUALITY
        #
        # Slightly below 60 is allowed when there is strong
        # directional macro evidence.
        # ----------------------------------------------------

        strong_direction = (
            abs(directional) >= 2
        )

        enough_confidence = (
            confidence >= 58
        )

        enough_important_news = (
            important >= 2
        )

        if not enough_confidence:

            continue

        if (
            confidence < 60
            and not strong_direction
        ):

            continue

        # ----------------------------------------------------
        # OPPORTUNITY STRENGTH
        # ----------------------------------------------------

        opportunity_strength = (

            abs(score) * 30

            + confidence * 0.7

            + abs(directional) * 10

            + important * 5
        )

        candidates.append({

            "market":
                market,

            "score":
                score,

            "confidence":
                confidence,

            "article_count":
                article_count,

            "directional_score":
                directional,

            "important_news":
                important,

            "opportunity_strength":
                opportunity_strength
        })

    # --------------------------------------------------------
    # NO CANDIDATE
    # --------------------------------------------------------

    if not candidates:

        return None

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    candidates.sort(

        key=lambda x:
            x["opportunity_strength"],

        reverse=True
    )

    return candidates[0]


# ============================================================
# PRINT SCAN
# ============================================================

def print_scan(
    results,
    best
):

    print()

    print(
        "TODAY'S NEWS MARKET SCAN"
    )

    print(
        "=" * 60
    )

    for market, data in results.items():

        score = data[
            "score"
        ]

        confidence = data[
            "confidence"
        ]

        if score > 0:

            signal = "BUY"

        elif score < 0:

            signal = "SELL"

        else:

            signal = "HOLD"

        print()

        print(
            market
        )

        print(
            f"Signal: {signal}"
        )

        print(
            f"News Score: {score:+d}"
        )

        print(
            f"Confidence: "
            f"{confidence:.0f}%"
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

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # BEST
    # --------------------------------------------------------

    if best is None:

        print(
            "BEST OPPORTUNITY: NONE"
        )

        print(
            "NO TRADE TODAY"
        )

    else:

        direction = (

            "BUY"
            if best["score"] > 0
            else "SELL"
        )

        print(
            "BEST OPPORTUNITY"
        )

        print(
            f"{best['market']} "
            f"→ {direction}"
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

    print(
        "=" * 60
    )


# ============================================================
# SHOW TOP NEWS FOR SELECTED MARKET
# ============================================================

def print_top_news(
    results,
    best,
    limit=5
):

    if best is None:

        return

    market = best[
        "market"
    ]

    data = results[
        market
    ]

    articles = data[
        "news"
    ]

    print()

    print(
        f"TOP NEWS FOR {market}"
    )

    print(
        "-" * 60
    )

    shown = 0

    for article in articles:

        title = article.get(
            "title",
            "Unknown"
        )

        sentiment = article.get(
            "overall_sentiment_score",
            0
        )

        direction = article.get(
            "_direction",
            0
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
            f"{direction:+d}"
        )

        shown += 1

        if shown >= limit:

            break


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    try:

        results = scan_all_markets()

        best = select_best_opportunity(
            results
        )

        print_scan(
            results,
            best
        )

        print_top_news(
            results,
            best
        )

    except Exception as error:

        print()

        print(
            "NEWS SCANNER ERROR:"
        )

        print(
            error
        )
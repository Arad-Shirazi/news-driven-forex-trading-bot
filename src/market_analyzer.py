import os
import requests
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

BASE_URL = "https://www.alphavantage.co/query"


# ============================================================
# MARKETS
# ============================================================

MARKETS = {

    "EURUSD": {
        "keywords": [
            "euro",
            "eur",
            "eurozone",
            "euro area",
            "ecb",
            "european central bank",
            "eurozone inflation",
            "eurozone gdp",
            "eurozone employment",
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
            "employment",
            "interest rate",
            "rate cut",
            "rate hike",
            "monetary policy"
        ]
    },

    "GBPUSD": {
        "keywords": [
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
        ]
    },

    "USDJPY": {
        "keywords": [
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
        ]
    },

    "XAUUSD": {
        "keywords": [
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
        ]
    },

    "USOIL": {
        "keywords": [
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
}


# ============================================================
# IMPORTANT NEWS
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
# POSITIVE / NEGATIVE ECONOMIC TERMS
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

    "strong economic growth",
    "economic growth",
    "better than expected",
    "beats expectations",
    "positive surprise"
]


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
# EXCLUDED NEWS
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
# API
# ============================================================

def get_all_news(limit=50):

    if not API_KEY:

        raise RuntimeError(
            "ALPHA_VANTAGE_API_KEY is missing."
        )

    params = {

        "function": "NEWS_SENTIMENT",

        "tickers": "FOREX:USD",

        "sort": "LATEST",

        "limit": limit,

        "apikey": API_KEY
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
# TEXT
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
# EXCLUSION
# ============================================================

def is_excluded(article):

    text = article_text(
        article
    )

    for term in EXCLUDED_TERMS:

        if term in text:

            return True

    return False


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

    keywords = MARKETS[
        market
    ]["keywords"]

    matches = []

    for keyword in keywords:

        if keyword in text:

            matches.append(
                keyword
            )

    if not matches:

        return 0

    score = len(
        matches
    )

    # Important macro events.
    for term in HIGH_IMPACT:

        if term in text:

            score += 4

    # Direct market-specific news.
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

        results.append(
            item
        )

    results.sort(

        key=lambda x: (

            x["_relevance"]
            * x["_freshness"]
        ),

        reverse=True
    )

    return results


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
    # Generic bullish / bearish language
    # --------------------------------------------------------

    for term in BULLISH_TERMS:

        if term in text:

            effect += 1

    for term in BEARISH_TERMS:

        if term in text:

            effect -= 1

    # --------------------------------------------------------
    # Market-specific logic
    # --------------------------------------------------------

    if market in [
        "EURUSD",
        "GBPUSD"
    ]:

        # Dollar weakness usually helps
        # EURUSD / GBPUSD.
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

    # --------------------------------------------------------
    # Gold
    # --------------------------------------------------------

    if market == "XAUUSD":

        if (
            "dollar weakness" in text
            or "weaker dollar" in text
            or "rate cut" in text
            or "rate cuts" in text
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
            or "rate hikes" in text
            or "higher interest rates" in text
        ):

            effect -= 2

    # --------------------------------------------------------
    # Oil
    # --------------------------------------------------------

    if market == "USOIL":

        if (
            "supply disruption" in text
            or "supply shortage" in text
            or "production cut" in text
            or "production cuts" in text
            or "output cut" in text
            or "output cuts" in text
            or "sanctions" in text
            or "shipping disruption" in text
            or "supply concerns" in text
            or "supply shock" in text
            or "war" in text
            or "conflict" in text
            or "strait of hormuz" in text
        ):

            effect += 3

        if (
            "oversupply" in text
            or "supply glut" in text
            or "production increase" in text
            or "production increases" in text
            or "output increase" in text
            or "output increases" in text
            or "demand weakness" in text
            or "weak demand" in text
            or "demand slowdown" in text
        ):

            effect -= 3

    return effect


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

            "article_count": 0
        }

    weighted_sentiment = 0.0

    total_weight = 0.0

    directional_score = 0.0

    important_count = 0

    for article in articles:

        sentiment = article[
            "_sentiment"
        ]

        relevance = min(

            article[
                "_relevance"
            ],

            20
        )

        freshness = article[
            "_freshness"
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

        effect = directional_effect(

            article,

            market
        )

        directional_score += (

            effect
            * freshness
        )

        if relevance >= 10:

            important_count += 1

    if total_weight == 0:

        return {

            "score": 0,

            "confidence": 0,

            "average_sentiment": 0,

            "article_count":
                len(articles)
        }

    average_sentiment = (

        weighted_sentiment
        / total_weight
    )

    # --------------------------------------------------------
    # Final combined score
    # --------------------------------------------------------

    combined = (

        average_sentiment * 10
        + directional_score
    )

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
    # Confidence
    # --------------------------------------------------------

    sentiment_strength = min(

        abs(
            average_sentiment
        ) * 200,

        45
    )

    directional_strength = min(

        abs(
            directional_score
        ) * 8,

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

    confidence = (

        sentiment_strength
        + directional_strength
        + article_strength
        + important_strength
    )

    confidence = min(
        confidence,
        100
    )

    # A score of 3 needs strong confidence.
    if score == 3:

        confidence = max(
            confidence,
            70
        )

    # Score 2 needs reasonable confidence.
    elif score == 2:

        confidence = max(
            confidence,
            62
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
# SCAN
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

            "news": articles
        }

    return results


# ============================================================
# BEST OPPORTUNITY
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

        if score == 0:

            continue

        if confidence < 60:

            continue

        candidates.append({

            "market": market,

            "score": score,

            "confidence": confidence,

            "article_count":
                data[
                    "article_count"
                ]
        })

    if not candidates:

        return None

    candidates.sort(

        key=lambda x: (

            abs(
                x["score"]
            ),

            x["confidence"],

            x["article_count"]
        ),

        reverse=True
    )

    return candidates[0]


# ============================================================
# PRINT
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
            f"News Score: "
            f"{score:+d}"
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
            f"{data.get('important_news', 0)}"
        )

        print(
            f"Directional Score: "
            f"{data.get('directional_score', 0):+.2f}"
        )

    print()

    print(
        "=" * 60
    )

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
        "=" * 60
    )


# ============================================================
# TEST
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

    except Exception as error:

        print()

        print(
            "NEWS SCANNER ERROR:"
        )

        print(error)
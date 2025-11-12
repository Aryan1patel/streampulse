# services/ingestors/trending_ingestor/filters.py

# services/ingestors/trending_ingestor/filters.py

IMPORTANT_KEYWORDS = [

    # 🔥 Market indexes
    "sensex", "nifty", "bank nifty", "dow", "nasdaq", "s&p",
    "market crash", "market falls", "market rises",

    # 🔥 Company events
    "acquisition", "acquires", "acquired",
    "merger", "m&a", "buyout", "joint venture",
    "stake", "invests in", "investment",
    "fundraise", "funding", "valuation",
    "ipo", "pre-ipo", "listing", "delisting",
    "rights issue", "bonus issue", "share split", "dividend",

    # 🔥 Regulation & policy
    "rbi", "sebi", "income tax", "gst", "budget",
    "fema", "compliance", "regulator", "ban", "sanction",
    "rules", "guidelines", "policy change",

    # 🔥 Corporate issues
    "fraud", "scam", "illegal", "probe", "investigation",
    "ed", "cbi", "raid", "audit", "whistleblower",
    "lawsuit", "settlement", "class action",

    # 🔥 Management
    "ceo", "cfo", "coo", "director", "chairman",
    "resigns", "steps down", "removed", "appointed",

    # 🔥 Layoffs & workforce
    "layoffs", "fired", "job cuts", "hiring freeze",
    "salary cuts",

    # 🔥 Economic indicators
    "gdp", "inflation", "cpi", "wpi",
    "recession", "slowdown", "economic growth",
    "exports", "imports", "trade deficit",
    "fdi", "fpi", "repo rate", "interest rate",

    # 🔥 Banking & finance
    "npas", "loan default", "liquidity crisis",
    "bankruptcy", "insolvency", "nbfc", "credit rating",
    "downgraded", "upgrade", "moratorium",

    # 🔥 Global macro
    "oil price", "brent", "opec", "gold prices",
    "dollar index", "currency depreciation",
    "bond yields", "treasury yields",

    # 🔥 Geopolitics & Security
    "war", "attack", "missile", "explosion", "blast",
    "terrorist", "bomb",
    "border clash", "border tension",
    "china", "pakistan", "russia", "ukraine", "us",
    "tariff", "trade war", "sanctions",
    "nia", "encounter", "security threat",
    "emergency", "curfew", "lockdown", "riot",
    "military", "strike", "clash", "airstrike", "drone",
    "missile launch", "evacuation", "embassy",
    "hostage", "ceasefire", "terror attack",

    # 🔥 Technology & AI
    "ai", "chip", "semiconductor", "gpu",
    "data breach", "cyberattack", "hacked",
    "server outage",

    # 🔥 Transport / Energy / Infra
    "aviation", "plane crash", "airlines",
    "power grid", "coal", "renewable",
    "pipeline explosion", "factory fire",

    # 🔥 Misc big-impact
    "covid", "pandemic", "variant",
    "natural disaster", "earthquake", "tsunami",
]


IGNORED_KEYWORDS = [
    # Sports & entertainment
    "cricket", "ipl", "match", "tournament", "world cup", "t20",
    "test match", "odi", "football", "fifa", "premier league",
    "champions league", "tennis", "badminton", "hockey", "kabaddi",
    "olympics", "sports", "player", "captain", "coach", "wicket",
    "runs", "century", "refuses to walk", "umpire", "dismissal",
    "hundred", "india a vs pakistan a",

    # Bollywood & entertainment
    "actor", "actress", "movie", "film", "bollywood", "hollywood",
    "celebrity", "birthday", "wedding", "trailer", "song", "music",
    "tv show", "series", "amazon prime", "netflix",
    "malaika", "shahrukh", "salman", "aamir", "deepika", "priyanka",
    "katrina", "sushant singh rajput", "ankita lokhande",
    "disha patani", "paris hilton", "item number",
    "sister most beautiful", "husband in focus",

    # Random noise
    "viral video", "funny", "weird", "meme",
    "astrology", "horoscope", "zodiac",
    "traffic", "weather", "festival",
    "temple", "church", "mosque",
    "school", "college", "exam", "student",
    "rainfall deficit", "metro stations", "renamed",

    # Low-impact crime / personal news
    "kills wife", "love affair", "divorce", "romance",
    "wheelchair", "bag returned", "auto driver",
    "gun licence", "maoists killed", "mayor urges",

    # Political gossip (not market-impacting)
    "nitish kumar after", "praise for", "eyebrows",
    "raises eyebrows", "boyfriend from white house",
    "boot out mtg", "epstein emails",
]


def is_market_impacting(title: str) -> bool:
    title = title.lower()

    # Ignore junk
    for w in IGNORED_KEYWORDS:
        if w in title:
            return False

    # Allow market-impacting news
    for w in IMPORTANT_KEYWORDS:
        if w in title:
            return True

    return False
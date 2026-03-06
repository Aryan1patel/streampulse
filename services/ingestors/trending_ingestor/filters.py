# services/ingestors/trending_ingestor/filters.py

# services/ingestors/trending_ingestor/filters.py

IMPORTANT_KEYWORDS = [

    # 🔥 Market indexes
    "sensex", "nifty", "bank nifty", "dow jones", "nasdaq", "s&p 500",
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

    # 🔥 Economic indicators (India specific)
    "gdp", "inflation", "cpi", "wpi",
    "recession", "slowdown", "economic growth",
    "exports", "imports", "trade deficit",
    "fdi", "fpi", "repo rate", "interest rate",

    # 🔥 Banking & finance
    "npas", "loan default", "liquidity crisis",
    "bankruptcy", "insolvency", "nbfc", "credit rating",
    "downgraded", "upgrade", "moratorium",

    # 🔥 Global macro (only impactful ones)
    "oil price", "brent crude", "opec",
    "gold prices", "dollar index", "rupee",
    "bond yields", "us fed", "us tariff", "us sanctions",
    "us rate", "fed rate", "fed cut", "fed hike",

    # 🔥 Technology (India-impacting)
    "data breach", "cyberattack", "hacked",
    "server outage", "semiconductor",

    # 🔥 Transport / Energy / Infra (India)
    "aviation", "plane crash", "airlines",
    "power grid", "coal india", "renewable energy",

    # 🔥 Disasters (India-relevant)
    "earthquake", "tsunami", "cyclone", "flood",
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
    
    # Local politics (not market-impacting)
    "statue", "bust", "memorial", "portrait", "monument",
    "protest march", "slogan", "rally", "demonstration",
    "shivaji maharaj", "ambedkar", "gandhi statue",
    "removal of", "sparks protest", "local protest",
    "city protest", "municipal", "civic", "township",
    "pilgrims", "accident", "bus accident", "road accident",
    "tibetan", "dalai lama", "exile",

    # Political gossip (not market-impacting)
    "nitish kumar after", "praise for", "eyebrows",
    "raises eyebrows", "boyfriend from white house",
    "boot out mtg", "epstein emails",
]


# India-related terms - article should mention India to be relevant
INDIA_CONTEXT = [
    "india", "indian", "rbi", "sebi", "rupee", "nifty", "sensex", "bse", "nse",
    "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "chennai",
    "gujarat", "maharashtra", "modi", "government of india", "ministry",
    "tata", "reliance", "infosys", "wipro", "hdfc", "icici", "sbi",
    "adani", "bajaj", "mahindra", "ola", "zomato", "paytm", "flipkart",
    "gnews_", "newsdata_", "newsapi_", "worldnews_india", "hindustan_times",
    "times_of_india", "livemint", "financial_express", "india_today",

    # Global but India-impacting
    "us tariff", "us fed", "us sanctions", "us rate",
    "oil price", "brent", "opec", "gold", "dollar",
]


def is_market_impacting(title: str, source: str = "") -> bool:
    title_lower = title.lower()
    source_lower = source.lower()

    # Always ignore junk
    for w in IGNORED_KEYWORDS:
        if w in title_lower:
            return False

    # Check if passes keyword filter
    passes_keyword = any(w in title_lower for w in IMPORTANT_KEYWORDS)
    if not passes_keyword:
        return False

    # Check India relevance (title OR source must be India-related)
    india_relevant = any(ctx in title_lower or ctx in source_lower for ctx in INDIA_CONTEXT)
    if not india_relevant:
        return False

    return True
"""
Event Classification Module
Classifies financial event types and calculates severity
"""

def classify_event_type(headline: str, content: str = None) -> str:
    """
    Classify the type of financial event using keyword matching
    
    Returns one of:
    - earnings
    - m&a (mergers & acquisitions)
    - regulation
    - product_launch
    - funding
    - legal
    - analyst_rating
    - macro (macroeconomic news)
    - layoffs
    - partnership
    - supply_chain
    - other
    """
    text = f"{headline} {content if content else ''}".lower()
    
    # Event patterns (order matters - check specific before general)
    patterns = {
        'earnings': ['earnings', 'quarterly results', 'q1 results', 'q2 results', 'q3 results', 'q4 results',
                     'profit', 'revenue', 'beats estimates', 'misses estimates', 'eps', 'ebitda',
                     'net profit', 'operating income', 'fiscal year', 'fy20', 'fy21', 'fy22', 'fy23', 'fy24'],
        'm&a': ['merger', 'acquisition', 'acquires', 'acquired', 'takeover', 'buyout', 'deal',
                'consolidation', 'combine', 'stake sale', 'divest'],
        'funding': ['funding', 'raises', 'investment', 'series a', 'series b', 'series c', 'venture capital',
                    'vc', 'valuation', 'unicorn', 'investors', 'round'],
        'regulation': ['regulation', 'policy', 'rbi', 'sebi', 'government', 'central bank', 'compliance',
                       'penalty', 'fine', 'investigation', 'probe', 'ban', 'sanctions'],
        'product_launch': ['launch', 'unveils', 'announces new', 'introduces', 'product', 'service',
                           'innovation', 'expansion', 'opens', 'enters market'],
        'legal': ['lawsuit', 'litigation', 'court', 'legal', 'sued', 'settlement', 'fraud', 'scam',
                  'conviction', 'sentenced'],
        'analyst_rating': ['upgrade', 'downgrade', 'rating', 'target price', 'buy', 'sell', 'hold',
                           'recommendation', 'analyst', 'brokerage'],
        'layoffs': ['layoffs', 'job cuts', 'firing', 'downsizing', 'restructuring', 'redundancies'],
        'partnership': ['partnership', 'collaboration', 'tie-up', 'joint venture', 'alliance', 'agreement',
                        'contract', 'signs deal'],
        'supply_chain': ['supply chain', 'shortage', 'disruption', 'logistics', 'inventory', 'raw material',
                         'production halt', 'factory'],
        'macro': ['inflation', 'gdp', 'interest rate', 'recession', 'economic growth', 'employment',
                  'trade war', 'tariff', 'currency', 'forex', 'oil prices', 'crude']
    }
    
    # Count matches for each event type
    event_scores = {}
    for event_type, keywords in patterns.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            event_scores[event_type] = score
    
    # Return event type with highest score
    if event_scores:
        return max(event_scores, key=event_scores.get)
    
    return 'other'


def calculate_severity(event_type: str, sentiment_score: float, keyword_count: int) -> str:
    """
    Calculate event severity (low, medium, high)
    
    Based on:
    - Event type importance
    - Sentiment strength
    - Number of keywords extracted
    """
    # High-impact event types
    high_impact_events = ['earnings', 'm&a', 'regulation', 'legal', 'funding']
    
    # Calculate base severity score
    severity_score = 0
    
    # Event type weight
    if event_type in high_impact_events:
        severity_score += 2
    elif event_type in ['product_launch', 'partnership', 'analyst_rating']:
        severity_score += 1
    
    # Sentiment strength weight
    if abs(sentiment_score) >= 0.8:
        severity_score += 2
    elif abs(sentiment_score) >= 0.5:
        severity_score += 1
    
    # Keyword count weight (more keywords = more important)
    if keyword_count >= 8:
        severity_score += 1
    
    # Classify severity
    if severity_score >= 4:
        return 'high'
    elif severity_score >= 2:
        return 'medium'
    else:
        return 'low'

import spacy
from keybert import KeyBERT
import re
import csv
from pathlib import Path
from collections import Counter
from sentence_transformers import SentenceTransformer, util

nlp = spacy.load("en_core_web_sm")
kw_model = KeyBERT()

# Semantic similarity model (lightweight, only 80MB)
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')

# Load company data from CSV
COMPANIES = {}
SYMBOLS = {}

def load_company_data():
    """Load company names and symbols from CSV"""
    csv_path = Path("/app/data/companies.csv")
    if not csv_path.exists():
        print("⚠️ companies.csv not found, skipping company detection")
        return
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = row['SYMBOL'].strip()
            company_name = row['NAME OF COMPANY'].strip()
            
            # Store both symbol and company name
            SYMBOLS[symbol.lower()] = {
                'symbol': symbol,
                'name': company_name
            }
            COMPANIES[company_name.lower()] = {
                'symbol': symbol,
                'name': company_name
            }
            
            # Also store shortened versions (without Limited, Ltd, etc.)
            # E.g., "HDFC Bank Limited" -> "hdfc bank"
            short_name = company_name.lower()
            for suffix in [' limited', ' ltd', ' ltd.', ' corporation', ' corp', ' inc', ' plc']:
                if short_name.endswith(suffix):
                    short_name = short_name.replace(suffix, '').strip()
                    if short_name not in COMPANIES:
                        COMPANIES[short_name] = {
                            'symbol': symbol,
                            'name': company_name
                        }
                    break
    
    print(f"✅ Loaded {len(SYMBOLS)} companies from CSV")

# Load company data on module import
load_company_data()

def extract_keywords(headline: str, content: str = None):
    """
    Extract keywords from headline and optionally full article content
    Uses semantic similarity and frequency scoring for better ranking
    
    Args:
        headline: Article headline
        content: Full article content (optional, improves accuracy)
    """
    # Use article content if available, otherwise just headline
    text_to_analyze = content if content and len(content) > 100 else headline
    
    doc = nlp(text_to_analyze)

    # Check if article is business/finance related
    business_keywords = {'bank', 'stock', 'shares', 'market', 'profit', 'revenue', 'earnings', 
                        'quarter', 'financial', 'investment', 'trading', 'equity', 'dividend',
                        'ipo', 'merger', 'acquisition', 'nifty', 'sensex', 'bse', 'nse'}
    
    text_lower = text_to_analyze.lower()
    is_business_news = any(keyword in text_lower for keyword in business_keywords)

    # Build word frequency map for scoring
    all_words = re.findall(r'\b\w+\b', text_lower)
    word_freq = Counter([w for w in all_words if len(w) >= 3])
    max_freq = max(word_freq.values()) if word_freq else 1
    
    def get_frequency_score(phrase: str) -> float:
        """Calculate frequency score (0-1) based on word occurrence"""
        words = re.findall(r'\b\w+\b', phrase.lower())
        if not words:
            return 0.0
        freq_scores = [word_freq.get(w, 0) / max_freq for w in words]
        return sum(freq_scores) / len(freq_scores)
    
    def get_semantic_score(candidate: str, reference: str) -> float:
        """Calculate semantic similarity between candidate and reference text"""
        try:
            # Encode both texts
            emb1 = semantic_model.encode(candidate, convert_to_tensor=True)
            emb2 = semantic_model.encode(reference[:512], convert_to_tensor=True)  # Limit reference length
            
            # Compute cosine similarity
            similarity = util.cos_sim(emb1, emb2)[0][0].item()
            return max(0.0, min(1.0, similarity))  # Clamp to [0,1]
        except Exception as e:
            print(f"Semantic scoring error: {e}")
            return 0.5  # Neutral default

    # Priority 0: Exact stock symbols and company names from CSV
    matched_companies = []
    headline_lower = headline.lower()
    content_lower = content.lower() if content else ""
    
    # Generic words to skip
    generic_words = {'bank', 'india', 'indian', 'corporation', 'limited', 'company', 'technologies', 'industries', 
                     'first', 'record', 'level', 'fresh', 'stock', 'market', 'share', 'rally', 'nifty',
                     'sensex', 'index', 'surge', 'high', 'hits', 'time', 'what', 'this', 'that', 'dozen',
                     'dozens', 'accident', 'killed', 'saudi', 'arabia', 'pilgrims', 'saudi arabia',
                     'exile', 'resolve', 'title', 'china', 'monday', 'tibetan', 'tibet', 'conflict',
                     'calls', 'during', 'lifetime', 'years', 'parliament'}
    
    # Step 1: Check for multi-word company names (e.g., "hdfc bank limited")
    # Only extract companies if this is business/finance news
    # Search in both headline and content
    if is_business_news:
        search_text = content_lower if content_lower else headline_lower
        for company_lower, company_data in COMPANIES.items():
            if company_lower in search_text:
                # Count how many times company appears (frequency = importance)
                frequency = search_text.count(company_lower)
                if not any(m['text'] == company_data['symbol'] for m in matched_companies):
                    matched_companies.append({
                        'text': company_data['symbol'],
                        'name': company_data['name'],
                        'type': 'STOCK_SYMBOL',
                        'priority': 0,
                        'frequency': frequency,
                        'match_type': 'full_company_name'
                    })
    
    # Step 2: Search for words IN company names (not in stock symbols)
    # Only search in HEADLINE words to avoid false matches from article content
    # Only do this for business/finance news
    # E.g., "dam" in headline should match "Dam Capital Advisors Limited" → DAMCAPITAL
    if is_business_news:
        headline_words = [w for w in re.findall(r'\b\w+\b', headline_lower) if len(w) >= 5]
        
        for word in headline_words:
            # Skip generic words
            if word in generic_words:
                continue
            
            # Search in company names
            for company_lower, company_data in COMPANIES.items():
                # Check if word appears as a complete word in company name
                company_words = company_lower.split()
                
                # Match if word is one of the words in company name
                # Also ensure the company name word is long enough to be meaningful
                for company_word in company_words:
                    if word == company_word and len(company_word) >= 5:
                        # Avoid duplicates
                        if not any(m['text'] == company_data['symbol'] for m in matched_companies):
                            matched_companies.append({
                                'text': company_data['symbol'],
                                'name': company_data['name'],
                                'type': 'STOCK_SYMBOL',
                                'priority': 0,
                                'match_type': f'word_in_company:{word}'
                            })
                            break  # Found match in this company, move to next word
    
    # Limit to top 8 most relevant company matches
    matched_companies = matched_companies[:8]

    # Priority 1: Named entities (people, locations, organizations not in CSV)
    entities = []
    for ent in doc.ents:
        # Skip if already matched as a company
        if any(ent.text.lower() in comp['name'].lower() for comp in matched_companies):
            continue
            
        # Prioritize PERSON, GPE (locations), MONEY, PERCENT
        if ent.label_ in ['PERSON', 'GPE', 'MONEY', 'PERCENT', 'DATE', 'CARDINAL', 'ORG', 'EVENT']:
            entities.append({
                'text': ent.text,
                'type': ent.label_,
                'priority': 1
            })

    # Priority 1: Important events and actions (verbs + nouns)
    event_keywords = [
        'ipo', 'merger', 'acquisition', 'buyback', 'dividend', 'split', 'bonus',
        'results', 'earnings', 'profit', 'loss', 'revenue', 'sales',
        'launch', 'announced', 'reports', 'files', 'approves', 'rejects',
        'crash', 'collapse', 'explosion', 'fire', 'disaster', 'emergency',
        'surge', 'plunge', 'rally', 'drops', 'gains', 'falls', 'rises',
        'investigation', 'fraud', 'scam', 'penalty', 'fine', 'lawsuit',
        'partnership', 'deal', 'contract', 'agreement', 'expansion',
        'layoffs', 'hiring', 'resignation', 'appointment', 'ceo', 'cfo'
    ]
    
    events = []
    for event in event_keywords:
        if event in headline_lower:
            events.append({
                'text': event,
                'type': 'EVENT',
                'priority': 1
            })

    # Priority 2: Stock market terms and numbers
    market_patterns = [
        r'\b(IPO|Q[1-4]|FY\d{2,4}|H[1-2])\b',  # IPO, Q2, FY25, H1
        r'\b(NIFTY|SENSEX|NASDAQ|NYSE|BSE|NSE)\b',  # Stock exchanges
        r'\b\d+%',  # Percentages like 25%
        r'\bRs\.?\s*\d+',  # Currency Rs 100
        r'\$\d+',  # Dollar amounts
        r'\b(crore|lakh|million|billion|trillion)\b',  # Large numbers
    ]
    
    market_terms = []
    for pattern in market_patterns:
        matches = re.findall(pattern, headline, re.IGNORECASE)
        for match in matches:
            market_terms.append({
                'text': match,
                'type': 'MARKET',
                'priority': 2
            })

    # Priority 3: KeyBERT extracted phrases (broader context)
    keywords = kw_model.extract_keywords(
        headline,
        keyphrase_ngram_range=(1, 3),
        stop_words='english',
        top_n=8
    )
    
    keyword_phrases = []
    for kw, score in keywords:
        # Skip if it's already captured in companies or events
        if any(kw.lower() in comp['text'].lower() or comp['text'].lower() in kw.lower() for comp in matched_companies):
            continue
        if any(kw.lower() == event['text'].lower() for event in events):
            continue
            
        keyword_phrases.append({
            'text': kw,
            'type': 'PHRASE',
            'priority': 3,
            'score': score
        })

    # Combine: companies → events/entities → market terms → phrases
    all_keywords = matched_companies + entities + events + market_terms + keyword_phrases
    
    # Add semantic and frequency scores to each keyword
    for kw in all_keywords:
        # Frequency score based on word occurrence
        kw['freq_score'] = get_frequency_score(kw['text'])
        
        # Semantic similarity to headline (primary context)
        kw['semantic_score'] = get_semantic_score(kw['text'], headline)
        
        # Combined final score:
        # - priority 0 (companies) always rank highest
        # - then combine base score + semantic + frequency
        base_score = kw.get('score', 0.7)  # KeyBERT score or default
        
        # Company boost (priority 0 = companies)
        company_boost = 1.0 if kw.get('priority') == 0 else 0.0
        
        # Weighted combination:
        # 40% base (KeyBERT/NER), 30% semantic, 20% frequency, 10% company boost
        kw['final_score'] = (
            0.40 * base_score +
            0.30 * kw['semantic_score'] +
            0.20 * kw['freq_score'] +
            0.10 * company_boost
        )
    
    # Remove duplicates (case-insensitive, keep highest scored)
    seen = {}
    for kw in all_keywords:
        text_lower = kw['text'].lower()
        if text_lower not in seen or kw['final_score'] > seen[text_lower]['final_score']:
            seen[text_lower] = kw
    
    unique_keywords = list(seen.values())
    
    # Sort by priority (0 = highest = companies), then by final_score (desc)
    unique_keywords.sort(key=lambda x: (x['priority'], -x['final_score']))
    
    # Return top 12 keywords to include companies, events, and context
    return [kw['text'] for kw in unique_keywords[:12]]
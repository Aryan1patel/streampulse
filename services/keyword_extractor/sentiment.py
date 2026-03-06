"""
Sentiment Analysis Module
Uses FinBERT for financial sentiment analysis
"""

def analyze_sentiment(headline: str, content: str = None) -> dict:
    """
    Analyze financial sentiment using FinBERT
    
    Returns:
        {
            "label": "positive" | "negative" | "neutral",
            "score": float (0-1, confidence),
            "raw_score": float (-1 to +1, negative to positive)
        }
    """
    try:
        from transformers import pipeline
        
        # Initialize FinBERT (cached after first load)
        if not hasattr(analyze_sentiment, '_pipeline'):
            print("🔄 Loading FinBERT model...")
            analyze_sentiment._pipeline = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                device=-1  # CPU (use 0 for GPU)
            )
            print("✅ FinBERT loaded")
        
        # Analyze text (prioritize headline, use content as context)
        text = headline
        if content and len(content) > 50:
            # Include first paragraph of content for better context
            text = f"{headline}. {content[:300]}"
        
        # FinBERT has max 512 tokens
        text = text[:512]
        
        result = analyze_sentiment._pipeline(text)[0]
        
        # FinBERT returns: positive, negative, neutral
        label = result['label'].lower()
        confidence = result['score']
        
        # Convert to sentiment score (-1 to +1)
        if label == 'positive':
            raw_score = confidence
        elif label == 'negative':
            raw_score = -confidence
        else:  # neutral
            raw_score = 0.0
        
        return {
            "label": label,
            "score": confidence,
            "raw_score": raw_score
        }
        
    except Exception as e:
        print(f"⚠️ Sentiment analysis error: {e}")
        # Fallback to neutral if model fails
        return {
            "label": "neutral",
            "score": 0.5,
            "raw_score": 0.0
        }

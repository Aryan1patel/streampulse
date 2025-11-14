from fastapi import FastAPI
from keyword_extractor.extractor import extract_keywords

app = FastAPI(title="StreamPulse Keyword Extractor")

@app.get("/keywords")
def get_keywords(headline: str):
    return {
        "headline": headline,
        "keywords": extract_keywords(headline)
    }
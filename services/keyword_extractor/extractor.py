import spacy
from keybert import KeyBERT

nlp = spacy.load("en_core_web_sm")
kw_model = KeyBERT()

def extract_keywords(headline: str):
    doc = nlp(headline)

    # 1) Named entities
    entities = [ent.text for ent in doc.ents]

    # 2) Keyword phrases
    keywords = kw_model.extract_keywords(
        headline,
        keyphrase_ngram_range=(1, 2),
        stop_words='english',
        top_n=5
    )
    keywords = [k[0] for k in keywords]

    final = list(set(entities + keywords))

    return final
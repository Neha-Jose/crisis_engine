from transformers import pipeline

urgency_model = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

ner_model = pipeline(
    "ner",
    model="dslim/bert-base-NER",
    grouped_entities=True
)

TREND_WORDS = ["rising","spreading","worsening","flooding","burning"]

def base_urgency(text):
    labels = ["high emergency","medium emergency","low emergency"]
    r = urgency_model(text, labels)
    return r["scores"][0]

def extract_entities(text):
    return ner_model(text)

def vulnerability_score(ents):
    for e in ents:
        if e["word"].lower() in ["child","children","elderly","infant"]:
            return 1.0
    return 0.3

def severity_score(text):
    for k in ["fire","bleeding","trapped","collapse"]:
        if k in text.lower():
            return 1.0
    return 0.4

def trend_score(text):
    return 1.0 if any(t in text.lower() for t in TREND_WORDS) else 0.0

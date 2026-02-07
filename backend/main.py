from fastapi import FastAPI, Request
from supabase import create_client
from models.nlp import base_urgency, extract_entities, vulnerability_score, severity_score, trend_score
from utils.pluscode import extract_plus_code, decode_plus

SUPABASE_URL="https://ocmblkbinzezlpksnezj.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9jbWJsa2Jpbnplemxwa3NuZXpqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA0MzAwMTEsImV4cCI6MjA4NjAwNjAxMX0.d43E0wvcIda-vrzr5r7ZoI-AN4Zr5J6EBzMC9nTjaFg"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

@app.post("/simulate")
async def simulate(req: Request):

    data = await req.json()
    sms = data["message"]

    base = base_urgency(sms)
    ents = extract_entities(sms)

    vuln = vulnerability_score(ents)
    sev = severity_score(sms)
    tr = trend_score(sms)

    final = base*0.45 + vuln*0.25 + sev*0.20 + tr*0.10

    plus = extract_plus_code(sms)
    lat, lng = (None, None)
    if plus:
        lat, lng = decode_plus(plus)

    reason = f"Base:{round(base,2)} Vul:{vuln} Sev:{sev} Trend:{tr}"

    supabase.table("alerts").insert({
        "sms": sms,
        "urgency": final,
        "severity": sev,
        "vulnerability": vuln,
        "trend": tr,
        "latitude": lat,
        "longitude": lng,
        "reasoning": reason
    }).execute()

    return {"status": "processed"}

# 🚨 AI-Driven Crisis Priority Dashboard

This project ingests SOS messages, assigns urgency scores using NLP, decodes Plus Codes
to latitude/longitude, and dynamically prioritizes emergencies on a real-time Streamlit dashboard
with explainable AI.

## Features
- Transformer-based urgency scoring
- Entity extraction (severity, vulnerability, trends)
- Plus Code geolocation
- Supabase storage
- Real-time priority dashboard
- Explainable AI
- Interactive map

## Run

Backend:
uvicorn backend.main:app --port 8000

Dashboard:
streamlit run dashboard/app.py

Simulator:
python backend/simulator.py

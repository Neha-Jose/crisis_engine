import time
import pandas as pd
import requests

BACKEND_URL = "http://localhost:8000/simulate"

df = pd.read_csv("data/sos_messages.csv")

for _, row in df.iterrows():
    payload = {"message": row["message"]}
    print("Sending:", row["message"])
    requests.post(BACKEND_URL, json=payload)
    time.sleep(5)  # simulate real-time arrival

import httpx
import datetime
import os
import numpy as np

import os

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

async def fetch_last_days(base: str, target: str, days: int = 7):
    url = (
        f"https://www.alphavantage.co/query"
        f"?function=FX_DAILY"
        f"&from_symbol={base}"
        f"&to_symbol={target}"
        f"&apikey={ALPHA_VANTAGE_API_KEY}"
        f"&outputsize=compact"
    )
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()
        if "Time Series FX (Daily)" not in data:
            print("⚠️ API yanıtı bozuk:", data)
            return []

        timeseries = data["Time Series FX (Daily)"]
        sorted_days = sorted(timeseries.items())[-days:]
        rates = [float(entry[1]["4. close"]) for entry in sorted_days]
        return rates


async def fetch_last_days_until(base: str, target: str, until: datetime.date, days: int = 7):
    url = (
        f"https://www.alphavantage.co/query"
        f"?function=FX_DAILY"
        f"&from_symbol={base}"
        f"&to_symbol={target}"
        f"&apikey={ALPHA_VANTAGE_API_KEY}"
        f"&outputsize=compact"
    )
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()
        if "Time Series FX (Daily)" not in data:
            print("⚠️ API yanıtı bozuk:", data)
            return []

        timeseries = data["Time Series FX (Daily)"]
        # Belirli bir tarihten önceki verileri al
        filtered = {
            k: v for k, v in timeseries.items()
            if datetime.datetime.strptime(k, "%Y-%m-%d").date() < until
        }
        sorted_days = sorted(filtered.items())[-days:]
        rates = [float(entry[1]["4. close"]) for entry in sorted_days]
        return rates

def predict_forex(values):
    if len(values) < 2:
        return {"error": "not enough data"}

    diffs = np.diff(values)
    avg_change = np.mean(diffs)
    last_price = values[-1]
    predicted = round(last_price + avg_change, 4)

    # Calculate dynamic band based on standard deviation
    std_dev = np.std(diffs)
    band_lower = round(predicted - std_dev, 4)
    band_upper = round(predicted + std_dev, 4)

    # Calculate Mean Absolute Error (MAE)
    errors = [abs(values[i] + avg_change - values[i + 1]) for i in range(len(values) - 1)]
    mae = round(sum(errors) / len(errors), 4)

    return {
        "current": last_price,
        "predicted": predicted,
        "band": [band_lower, band_upper],
        "direction": "up" if avg_change > 0 else "down",
        "confidence": {
            "trend": 0.6 if avg_change > 0 else 0.4,
            "volatilityWarning": 0.1
        },
        "metrics": {
            "std_dev": round(std_dev, 4),
            "mae": mae
        }
    }
from fastapi import FastAPI, Query
import datetime
from forex_service import fetch_last_days, predict_forex,fetch_last_days_until
from comment_with_gpt import gpt_comment

app = FastAPI()

@app.get("/predict")
async def predict(
        base: str = Query(..., description="Source currency, e.g., USD"),
        target: str = Query(..., description="Target currency, e.g., TRY"),
        days: int = Query(7, description="Number of days for historical data")
):
    history = await fetch_last_days(base, target, days)
    result = predict_forex(history)
    result["base"] = base
    result["target"] = target

    if "error" not in result:
        result["comment"] = gpt_comment(history, result)

        # 🔥 Tarihleri hesaplayıp geçmişi ekleyelim
        end = datetime.date.today() - datetime.timedelta(days=1)
        dates = [(end - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(len(history)-1, -1, -1)]
        result["history"] = [
            {"date": date, "rate": rate}
            for date, rate in zip(dates, history)
        ]
    else:
        result["comment"] = "Yorum yapılamadı çünkü yeterli veri alınamadı."

    return result


@app.get("/predict-date")
async def predict_date(base: str, target: str, date: str):  # örnek: "2025-07-21"
    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    history = await fetch_last_days_until(base, target, until=date_obj, days=7)
    result = predict_forex(history)
    if "error" in result:
        return result

    result["base"] = base
    result["target"] = target
    result["date"] = date
    result["comment"] = gpt_comment(history, result)
    result["history"] = history  # bu satırı ekliyoruz

    return result
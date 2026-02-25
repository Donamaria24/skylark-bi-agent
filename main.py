import os
from fastapi import FastAPI
import pandas as pd
from dotenv import load_dotenv
from monday_client import fetch_board_items
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")
WORK_BOARD_ID = os.getenv("WORK_BOARD_ID")


# ===============================
# DATA PROCESSING
# ===============================

def get_deals_df():
    items = fetch_board_items(DEALS_BOARD_ID)
    df = pd.DataFrame(items)

    if "Masked Deal value" in df.columns:
        df["Masked Deal value"] = pd.to_numeric(
            df["Masked Deal value"], errors="coerce"
        )

    df = df.dropna(subset=["Masked Deal value"])

    return df


def get_work_orders_df():
    items = fetch_board_items(WORK_BOARD_ID)
    df = pd.DataFrame(items)
    return df


# ===============================
# CORE ANALYTICS ENGINE
# ===============================

def compute_cross_board_metrics():

    deals_df = get_deals_df()
    work_df = get_work_orders_df()

    total_pipeline = deals_df["Masked Deal value"].sum()

    pipeline_by_sector = (
        deals_df.groupby("Sector/service")["Masked Deal value"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )

    pipeline_by_stage = (
        deals_df.groupby("Deal Stage")["Masked Deal value"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )

    total_work_orders = len(work_df)

    won_deals = deals_df[
        deals_df["Deal Stage"].str.contains("Won", case=False, na=False)
    ]

    conversion_rate = 0
    if len(deals_df) > 0:
        conversion_rate = len(won_deals) / len(deals_df)

    return {
        "total_pipeline": total_pipeline,
        "pipeline_by_sector": pipeline_by_sector,
        "pipeline_by_stage": pipeline_by_stage,
        "total_work_orders": total_work_orders,
        "conversion_rate": conversion_rate
    }


# ===============================
# API ENDPOINTS
# ===============================

@app.get("/")
def home():
    return {"status": "Skylark BI Agent Running"}


@app.get("/deals")
def get_deals():
    return compute_cross_board_metrics()


@app.get("/leadership-update")
def leadership_update():
    summary = compute_cross_board_metrics()

    narrative = f"""
    Total pipeline stands at ₹ {summary['total_pipeline']:,.2f}.
    Current deal-to-win conversion rate is {summary['conversion_rate']*100:.2f}%.
    We have {summary['total_work_orders']} active work orders.
    Top performing sector is {max(summary['pipeline_by_sector'], key=summary['pipeline_by_sector'].get)}.
    """

    return {
        "metrics": summary,
        "leadership_summary": narrative
    }


class QuestionRequest(BaseModel):
    question: str


@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.lower()
    summary = compute_cross_board_metrics()

    if "total" in question:
        return {"answer": f"Total pipeline is ₹ {summary['total_pipeline']:,.2f}"}

    elif "sector" in question:
        return {"answer": summary["pipeline_by_sector"]}

    elif "stage" in question:
        return {"answer": summary["pipeline_by_stage"]}

    elif "conversion" in question:
        return {
            "answer": f"Deal conversion rate is {summary['conversion_rate']*100:.2f}%"
        }

    elif "work order" in question:
        return {
            "answer": f"There are {summary['total_work_orders']} active work orders."
        }

    else:
        return {
            "answer": "You can ask about total pipeline, sector performance, stage distribution, conversion rate, or work orders."
        }
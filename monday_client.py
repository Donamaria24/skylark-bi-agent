import os
import requests
from dotenv import load_dotenv

load_dotenv()

MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")

HEADERS = {
    "Authorization": MONDAY_API_TOKEN,
    "Content-Type": "application/json"
}

def fetch_board_items(board_id):
    query = f"""
    query {{
      boards(ids: {board_id}) {{
        columns {{
          id
          title
        }}
        items_page(limit: 500) {{
          items {{
            id
            name
            column_values {{
              id
              text
            }}
          }}
        }}
      }}
    }}
    """

    response = requests.post(
        "https://api.monday.com/v2",
        json={"query": query},
        headers=HEADERS
    )

    response.raise_for_status()

    data = response.json()["data"]["boards"][0]

    columns = data["columns"]
    items = data["items_page"]["items"]

    # Map column id → column title
    column_map = {col["id"]: col["title"] for col in columns}

    formatted_items = []

    for item in items:
        row = {"Item Name": item["name"]}

        for col in item["column_values"]:
            column_title = column_map.get(col["id"], col["id"])
            row[column_title] = col["text"]

        formatted_items.append(row)

    return formatted_items
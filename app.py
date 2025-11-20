import os
import json
import base64
import mimetypes
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from config.config import Config


load_dotenv()


app = FastAPI(
    title=Config.API_TITLE,
    description=Config.API_DESCRIPTION,
    version=Config.API_VERSION
)


if os.environ.get("DOCKER"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


client = ChatGoogleGenerativeAI(
    model=Config.MODEL_NAME,
    temperature=Config.MODEL_TEMPERATURE,
    max_retries=Config.MODEL_MAX_RETRIES,
)


class SplitEvenRequest(BaseModel):
    receipt: dict
    num_people: int

    @field_validator("num_people")
    def validate_people(cls, v):
        if v <= 0:
            raise ValueError("num_people must be > 0")
        return v


class SplitItemRequest(BaseModel):
    receipt: dict
    assignments: dict


def split_evenly_handler(receipt_dict, num_people):
    sub_total = sum(item["price_per_unit"] * item["quantity"] for item in receipt_dict["items"])
    total_price = sub_total + receipt_dict.get("service_price", 0) + receipt_dict.get("tax_price", 0) - receipt_dict.get("discount_price", 0)
    return round(total_price / num_people)


def split_by_items_handler(receipt_dict, assignments):
    sub_total = sum(item["price_per_unit"] * item["quantity"] for item in receipt_dict["items"])
    items_dict = {item["name"]: {"quantity": item["quantity"], "price_per_unit": item["price_per_unit"]} for item in receipt_dict["items"]}

    result = {}
    for user, items in assignments.items():
        sub_total_user = 0
        for name, quantity in items.items():
            sub_total_user += items_dict[name]["price_per_unit"] * quantity

        proportion = sub_total_user / sub_total
        result[user] = round(sub_total_user + proportion * (receipt_dict.get("service_price", 0) + receipt_dict.get("tax_price", 0) - receipt_dict.get("discount_price", 0)))
    return result


@app.post("/upload-receipt")
async def upload_receipt(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")

    image_bytes = await file.read()
    mime_type = file.content_type
    # mime_type, _ = mimetypes.guess_type(file.filename)
    encoded = base64.b64encode(image_bytes).decode('utf-8')
    image_uri = f"data:{mime_type};base64,{encoded}"

    message = HumanMessage(
        content=[
            {"type": "text", "text": Config.PROMPT},
            {"type": "image_url", "image_url": {"url": image_uri}},
        ]
    )
    response = client.invoke([message])

    try:
        json_string = response.content.replace("```json", "").replace("```", "")
        data = json.loads(json_string)
        return data
    except:
        raise HTTPException(500, "Failed to parse receipt JSON")


@app.post("/split-evenly")
async def split_evenly(even_req: SplitEvenRequest = None):
    if not even_req:
        raise HTTPException(400, "split-evenly mode requires SplitEvenRequest")
    return {"result": split_evenly_handler(even_req.receipt, even_req.num_people)}


@app.post("/split-by-items")
async def split_by_items(item_req: SplitItemRequest = None):
    if not item_req:
        raise HTTPException(400, "split-by-items mode requires SplitItemRequest")
    return {"result": split_by_items_handler(item_req.receipt, item_req.assignments)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app", 
        host=Config.API_HOST, 
        port=Config.API_PORT, 
        reload=True
    )

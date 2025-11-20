# Assignment: SmartSplit Bill AI

## Stack:
1. Runtime: Python 3.10.
2. LLM model: gemini-2.5-flash.
3. Backend: FastAPI.
4. Interface: Streamlit.

## Prerequisites:
1. Gemini API key from: https://aistudio.google.com/

## Setup:
1. `git clone https://github.com/RifqiAnshariR/smart-split-bill.git`
2. `cd smart-split-bill`
3. `py -3.10 -m venv .venv` and activate it `.venv\Scripts\activate`
4. `pip install -r requirements.txt`
5. Make .env file contains: GOOGLE_API_KEY.

## How to run:
1. To run API: python app.py
2. To run Streamlit: streamlit run Home.py

## Demo:
https://youtu.be/6CO3TUrcAuA

## Evaluation:
Evaluation done on: 
- Models: gemini-2.5-flash, gemini-2.0-flash, gemini-2.0-flash-lite.
- Images: receipt_1.jpg, receipt_2.png, receipt_3.jpg.
- Num trials: 3 per model per image.

Results:
1. Speed of bill extraction (average):
   - gemini-2.5-flash: 4.4s on receipt_1.jpg, 8.1s on receipt_2.png, 14.0s on receipt_3.jpg.
   - gemini-2.0-flash: 3.9s on receipt_1.jpg, 8.3s on receipt_2.png, 11.6s on receipt_3.jpg.
   - gemini-2.0-flash-lite: 4.2s on receipt_1.jpg, 8.5s on receipt_2.png, 13.5s on receipt_3.jpg.

2. Accuracy of bill extraction (manual):
   - gemini-2.5-flash: 100%
   - gemini-2.0-flash: 100%
   - gemini-2.0-flash-lite: 100%
from fastapi import FastAPI, File, UploadFile
import cv2
import numpy as np
import time
from app.ocr_engine import extract_text

app = FastAPI()

@app.post("/extract-text/")
async def extract_text_api(file: UploadFile = File(...)):
    # Read file into memory
    file_bytes = await file.read()
    
    # Decode bytes to image array
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return {"extracted_text": "Error: Invalid image file", "time_taken_seconds": 0}
    
    # Extract text and measure time
    start_time = time.perf_counter()
    extracted_text = extract_text(img)
    elapsed_time = time.perf_counter() - start_time

    return {
        "extracted_text": extracted_text,
        "time_taken_seconds": round(elapsed_time, 2)
    }
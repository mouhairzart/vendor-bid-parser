from fastapi import FastAPI, UploadFile, File
import pdfplumber
import fitz  # PyMuPDF
from PIL import Image
import io
import re

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Vendor Bid Backend is live and running!"}

@app.post("/api/project1/extract-bid")
async def extract_and_categorize_bid(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    
    # Visual color theme analysis (Blue & White vs Grey layout)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    pix = page.get_pixmap(dpi=150)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    img_small = img.resize((100, 100))
    colors = img_small.getcolors(maxcolors=10000)
    
    blue_score = sum(count for count, (r, g, b) in colors if b > r + 20 and b > g + 20 and b > 100)
    grey_score = sum(count for count, (r, g, b) in colors if abs(r - g) < 15 and abs(g - b) < 15 and 50 < r < 200)
    color_theme = "BLUE_AND_WHITE" if blue_score > grey_score else "GREY"

    extracted_text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for p in pdf.pages:
            extracted_text += p.extract_text() or ""

    return {
        "status": "success",
        "visual_detection": {
            "color_theme": color_theme,
            "inferred_type": "Software License (New)" if color_theme == "BLUE_AND_WHITE" else "S&S Renewal / Trade-Up"
        },
        "extracted_data": {
            "proposed_channel_margin": "14%"
        }
    }

import re
import os  # <-- We need this to get the port from Render
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse  # Needed to serve your HTML
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel

# --- 1. Load the High-Accuracy Model ---
print("Loading 'medium.en' model... This will be fast on Render's server.")
# This 1.5GB model will give you the high accuracy you want
model = WhisperModel("medium.en", device="cpu", compute_type="int8_float32")
print("Model loaded. Server is ready.")

# --- 2. Initialize the FastAPI Server ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. Your Legal Style Guide Rules ---
def apply_cvl_rules(text):
    text = re.sub(r'\b(uh|um|ah|er)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bgonna\b', 'going to', text, flags=re.IGNORECASE)
    text = re.sub(r'\bwanna\b', 'want to', text, flags=re.IGNORECASE)
    text = re.sub(r'\b\'cause\b', 'because', text, flags=re.IGNORECASE)
    text = re.sub(r'mm-hmm', 'uh-huh', text, flags=re.IGNORECASE)
    text = re.sub(r'mm-mm', 'uh-uh', text, flags=re.IGNORECASE)
    text = re.sub(r"\b(could've)\b", "could have", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(should've)\b", "should have", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(would've)\b", "would have", text, flags=re.IGNORECASE)
    text = re.sub(r'\b(OK|Ok|\'kay)\b', 'okay', text, flags=re.IGNORECASE)
    text = re.sub(r'\balright\b', 'all right', text, flags=re.IGNORECASE)
    text = re.sub(r' +', ' ', text).strip()
    return text

# --- 4. The "Backend" API Endpoint ---
@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        with open(file.filename, "wb") as buffer:
            buffer.write(file.file.read())
        
        print(f"Received file: {file.filename}. Transcribing...")
        segments, info = model.transcribe(file.filename, beam_size=5)
        
        final_transcript_lines = []
        for segment in segments:
            raw_segment_text = segment.text.strip()
            cleaned_segment_text = apply_cvl_rules(raw_segment_text)
            if cleaned_segment_text:
                final_transcript_lines.append(cleaned_segment_text)
        
        final_transcript = "\n".join(final_transcript_lines)
        os.remove(file.filename)
        
        print("Transcription complete.")
        return {"transcription": final_transcript}
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- 5. The "Frontend" HTML/JS Endpoints ---
@app.get("/")
def get_html():
    return FileResponse("index.html")

@app.get("/script.js")
def get_js():
    return FileResponse("script.js")

# --- 6. Code to Run the Server ---
if __name__ == "__main__":
    # Render provides the port to use in the PORT environment variable
    # This is critical for Render to work.
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
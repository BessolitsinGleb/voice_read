import io
import re
from fastapi import APIRouter, File, HTTPException, UploadFile, Response, Form, Depends
import edge_tts
import io
import re
import edge_tts
import pytesseract
from fastapi import HTTPException, UploadFile, File, Form, Response
from pypdf import PdfReader
from pdf2image import convert_from_bytes
from ..dependencies import get_current_user
from ..models import Users

router = APIRouter(prefix="/audio_pdf", tags=["audio_pdf"])

def split_text(text: str, max_chars: int = 2000) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_chars:
            current_chunk += (" " if current_chunk else "") + sentence
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

@router.post("/tts-play")
async def process_any_pdf(
    file: UploadFile = File(...),
    voice: str = Form("ru-RU-SvetlanaNeural"),
    current_user: Users = Depends(get_current_user)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Поддерживаются только .pdf файлы")

    try:
        pdf_bytes = await file.read()
        
        reader = PdfReader(io.BytesIO(pdf_bytes))
        extracted_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
        
        if not extracted_text.strip():
            images = convert_from_bytes(pdf_bytes)
            
            if not images:
                raise HTTPException(status_code=400, detail="Не удалось преобразовать PDF в изображения")
            
            for img in images:
                page_text = pytesseract.image_to_string(img, lang="rus+eng")
                extracted_text += page_text + "\n"

        extracted_text = extracted_text.strip()

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка обработки файла: {str(e)}")

    if not extracted_text:
        raise HTTPException(status_code=400, detail="В файле не обнаружен текст для распознавания")

    text_chunks = split_text(extracted_text)
    audio_buffer = io.BytesIO()

    try:
        for chunk in text_chunks:
            communicate = edge_tts.Communicate(chunk, voice)
            async for sub_chunk in communicate.stream():
                if sub_chunk["type"] == "audio":
                    audio_buffer.write(sub_chunk["data"])

        audio_bytes = audio_buffer.getvalue()
        content_length = len(audio_bytes)

        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
                "Content-Length": str(content_length),
                "Accept-Ranges": "bytes"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка синтеза речи: {str(e)}")

@router.get("/tts-play")
async def rrr():
    return True
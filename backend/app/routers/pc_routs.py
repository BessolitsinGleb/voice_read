import io
import re
import os
import sys
import asyncio
import subprocess
import edge_tts
import pytesseract
import pyautogui
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse, HTMLResponse
from PIL import Image, ImageGrab
from ..models import Users
from ..dependencies import get_current_user

router = APIRouter(prefix="/PC_screen", tags=["PC Screen"])

SAVED_BBOX = None
SCROLL = None

def split_text(text: str, max_chars: int = 2000) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_chars:
            current_chunk += (" " if current_chunk else "") + sentence
        else:
            if current_chunk: chunks.append(current_chunk)
            current_chunk = sentence
    if current_chunk: chunks.append(current_chunk)
    return chunks

def capture_screen_by_os() -> Image.Image:
    global SAVED_BBOX
    current_os = sys.platform
    temp_image_path = "temp_capture.png"

    if current_os == "darwin":
        if SAVED_BBOX is None:
            try:
                subprocess.run(["screencapture", "-i", temp_image_path], check=True)
                if not os.path.exists(temp_image_path):
                    raise HTTPException(status_code=400, detail="Отменено")
                with Image.open(temp_image_path) as img:
                    screenshot = img.copy()
                
                width, height = screenshot.size
                sw, sh = pyautogui.size()
                SAVED_BBOX = (sw//2 - width//2, sh//2 - height//2, sw//2 + width//2, sh//2 + height//2)
                
                os.remove(temp_image_path)
                return screenshot
            except Exception:
                raise HTTPException(status_code=500, detail="Ошибка ручного захвата Mac")
        
        else:
            try:
                return ImageGrab.grab(bbox=SAVED_BBOX)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Ошибка тихого снимка: {str(e)}")
    else:
        if SAVED_BBOX is None:
            sw, sh = pyautogui.size()
            SAVED_BBOX = (sw // 4, sh // 4, sw * 3 // 4, sh * 3 // 4)
        return ImageGrab.grab(bbox=SAVED_BBOX)

@router.get("/reset")
async def reset_zone(current_user: Users = Depends(get_current_user)):
    global SAVED_BBOX
    SAVED_BBOX = None
    return {"status": "Зона чтения сброшена. Следующий запуск потребует выделения."}

@router.get("/capture-and-play")
async def capture_read_and_scroll(
    voice: str = Query("ru-RU-SvetlanaNeural"),
    current_user: Users = Depends(get_current_user)
):
    screenshot = capture_screen_by_os()
    global SCROLL
    try:
        extracted_text = pytesseract.image_to_string(screenshot, lang="rus+eng", config="--psm 3").strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR error: {str(e)}")

    if not extracted_text:
        pyautogui.scroll(-20)
        raise HTTPException(status_code=400, detail="Текст не найден. Страница прокручена.")

    text_chunks = split_text(extracted_text)

    async def audio_stream_generator():
        loop = asyncio.get_running_loop()
        loop.run_in_executor(None, pyautogui.scroll, SCROLL)
        
        for chunk in text_chunks:
            communicate = edge_tts.Communicate(chunk, voice)
            async for sub_chunk in communicate.stream():
                if sub_chunk["type"] == "audio":
                    yield sub_chunk["data"]
                    await asyncio.sleep(0.001)

    return StreamingResponse(
        audio_stream_generator(),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=live_speech.mp3"}
    )

@router.post('/setting_scroll')
async def set_scroll(value: int, current_user: Users = Depends(get_current_user)):
    v = -value
    global SCROLL
    SCROLL = v
    return SCROLL

@router.post("/test-scroll")
async def test_scroll_only(current_user: Users = Depends(get_current_user)):
    try:
        capture_screen_by_os()
        pyautogui.scroll(SCROLL) 
        return {"status": "success", "message": "Зона зафиксирована, скролл выполнен"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка теста: {str(e)}")

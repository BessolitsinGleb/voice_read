from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.files_rout import router as files_router
from .routers.pc_routs import router as pc_router
from .database import Base, engine
from .routers.auth_routs import router as auth_router

app = FastAPI(title="Voice Read")

app.include_router(files_router)
app.include_router(pc_router)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
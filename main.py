import warnings
import os

# Suppress hardware resource incompatible warning
warnings.filterwarnings("ignore", category=UserWarning, module="ctranslate2")
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")
warnings.filterwarnings("ignore", message="Some weights of the model checkpoint")
os.environ["TRANSFORMERS_VERBOSITY"] = "error"


import uvicorn
from fastapi import FastAPI

from app.db.setup import Base, engine
from app.routers.chat import chat_router
from app.routers.file_io import file_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(file_router)
app.include_router(chat_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7000)


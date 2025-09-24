from fastapi import FastAPI
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware

from .routes import AdminRoutes
from .routes import QueryRoutes



app = FastAPI()

router = APIRouter()

origins = [
    "http://localhost:5173",   # React local dev
    "http://127.0.0.1:5173",
    "https://chatbot-iota-black.vercel.app", # React production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allowed origins
    allow_credentials=True,           # Allow cookies/auth headers
    allow_methods=["*"],               # Allow all HTTP methods
    allow_headers=["*"],               # Allow all headers
)


@app.get("/")
async def root():

    return {"message": "Hello World"}


app.include_router(QueryRoutes.router, prefix="/api/user", tags=["query"])
app.include_router(AdminRoutes.router, prefix="/api", tags=["admin"])


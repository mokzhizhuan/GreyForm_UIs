from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Define allowed origins
allowed_origins = [
    "http://localhost:3000",     # React development server
    "http://127.0.0.1:3000",     # Localhost with IP
    "http://localhost:8000",     # FastAPI server itself
    "http://127.0.0.1:8000",     # FastAPI server with IP
    "file://",                   # Local file access for QWebEngineView
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],         # Allow all HTTP methods
    allow_headers=["*"],         # Allow all headers
)

@app.get("/api/data")
async def get_data():
    return {"message": "Hello from FastAPI"}

@app.post("/api/update")
async def update_data(data: dict):
    print("Received from React:", data)
    return {"status": "success", "message": "Data received"}

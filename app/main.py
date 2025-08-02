from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.db.database import init_db

# Initialize database tables
init_db()

app = FastAPI(
    title="FinGuard Agents + AgentScope",
    description="A modular GenAI system for real-time fraud detection, narrative explanations, and agent traceability.",
    version="1.0.0"
)

# Optional: Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to Reflex frontend origin later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(router)

# Health check route
@app.get("/")
def root():
    return {"message": "FinGuard Agents API is running."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

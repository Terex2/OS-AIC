from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Open Source AI Company API")

class Query(BaseModel):
    prompt: str

@app.get("/")
async def root():
    return {"message": "Welcome to OS-AIC API", "status": "online"}

@app.post("/ask")
async def ask_ai(query: Query):
    # هنا يتم استدعاء الأوركسترا (Orchestrator)
    return {"answer": f"Processing: {query.prompt}", "agent": "Core-Orchestrator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

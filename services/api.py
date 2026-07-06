from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json

app = FastAPI(title="Open Source AI Company API")

class Query(BaseModel):
    prompt: str

@app.get("/")
async def root():
    return {"message": "Welcome to OS-AIC API", "status": "online"}

@app.post("/ask")
async def ask_ai(query: Query):
    try:
        # استدعاء Ollama للحصول على استجابة ذكية
        ollama_url = "http://ollama:11434/api/generate"
        payload = {
            "model": "llama3",  # استخدام نموذج Llama 3 الذي تم تحميله
            "prompt": query.prompt,
            "stream": False
        }
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(ollama_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status() # Raise an exception for HTTP errors
        
        result = response.json()
        ai_response = result["response"]
        
        return {"answer": ai_response, "agent": "Ollama-Llama3"}
    except requests.exceptions.ConnectionError:
        return {"answer": "Ollama service is not reachable. Please ensure it's running.", "agent": "Error"}
    except Exception as e:
        return {"answer": f"An error occurred: {str(e)}", "agent": "Error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""Run the FastAPI server"""
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting PALM API Server with SQLite...")
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8888,
        reload=False,
        log_level="info"
    )

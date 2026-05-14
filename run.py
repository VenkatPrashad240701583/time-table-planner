import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",   # path to your FastAPI app
        host="0.0.0.0",
        port=800,
        reload=True       # auto-restart on changes
    )

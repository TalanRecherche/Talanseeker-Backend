import uvicorn
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    uvicorn.run(
        app="app.start_app:app",
        reload=True,
        workers=1,
    )

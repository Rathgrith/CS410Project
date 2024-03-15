from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def homepage():
    return {"message": "Hello World!"}

if __name__ == "__main__":
    import uvicorn
    # Run `uvicorn main:app - reload` to start backend
    uvicorn.run(app, host="0.0.0.0", port=8000)
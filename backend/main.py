from fastapi import FastAPI

app = FastAPI(title="Secret Scanner & Redactor")

@app.get("/")
async def root():
    return {"message": "Secret Scanner API is running"}
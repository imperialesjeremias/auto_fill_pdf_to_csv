from fastapi import FastAPI, File, UploadFile, HTTPException
from utils import pdfreader


app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})

@app.get("/")
async def Index():
    return {"message": "Hello World"}

@app.post("/upload")
async def process_pdf_type_one(file: UploadFile = File(...)):    
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are accepted.")
    # Procesa tu archivo PDF aquí
    pdfreader(file)
    
    return {"message": f"PDF Type One Processed: {file.filename}"}

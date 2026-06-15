from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from bson import ObjectId
import pandas as pd
from datetime import datetime

from app.core.database import get_db
from app.services.storage_service import save_upload, delete_file
from app.services.excel_service import read_excel_sheets

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "excel",
    "application/vnd.ms-excel": "excel",
    "application/pdf": "pdf",
}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    content_type = file.content_type or ""
    # Also infer from extension
    if file.filename.endswith(".xlsx") or file.filename.endswith(".xls"):
        file_type = "excel"
    elif file.filename.endswith(".pdf"):
        file_type = "pdf"
    else:
        file_type = ALLOWED_TYPES.get(content_type)

    if not file_type:
        raise HTTPException(status_code=400, detail="Only Excel and PDF files are supported")

    path, size = await save_upload(file)

    meta = {
        "filename": file.filename,
        "file_type": file_type,
        "upload_path": path,
        "uploaded_at": datetime.utcnow(),
        "size_bytes": size,
    }

    if file_type == "excel":
        try:
            xl = pd.ExcelFile(path)
            meta["sheet_names"] = xl.sheet_names
            df = xl.parse(xl.sheet_names[0])
            meta["row_count"] = len(df)
        except Exception:
            pass

    db = get_db()
    result = await db.documents.insert_one(meta)
    meta["_id"] = str(result.inserted_id)

    return {"id": str(result.inserted_id), "filename": file.filename, "file_type": file_type, "meta": meta}


@router.get("/")
async def list_documents():
    db = get_db()
    docs = []
    async for doc in db.documents.find():
        doc["id"] = str(doc.pop("_id"))
        doc["uploaded_at"] = doc["uploaded_at"].isoformat() if "uploaded_at" in doc else None
        docs.append(doc)
    return docs


@router.get("/{doc_id}")
async def get_document(doc_id: str):
    db = get_db()
    doc = await db.documents.find_one({"_id": ObjectId(doc_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    db = get_db()
    doc = await db.documents.find_one({"_id": ObjectId(doc_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    delete_file(doc["upload_path"])
    await db.documents.delete_one({"_id": ObjectId(doc_id)})
    return {"message": "Deleted"}


@router.get("/{doc_id}/sheets")
async def get_excel_sheets(doc_id: str):
    db = get_db()
    doc = await db.documents.find_one({"_id": ObjectId(doc_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc["file_type"] != "excel":
        raise HTTPException(status_code=400, detail="Not an Excel file")
    sheets = read_excel_sheets(doc["upload_path"])
    return {"sheets": list(sheets.keys()), "data": sheets}

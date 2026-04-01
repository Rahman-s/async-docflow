import os
import json
import shutil
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from app.db.database import Base, engine, get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentUpdate, FinalizeRequest
from app.core.config import settings
from app.workers.tasks import process_document_task
import pandas as pd

Base.metadata.create_all(bind=engine)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.EXPORT_DIR, exist_ok=True)

app = FastAPI(title="Async Document Workflow")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Backend running"}


@app.post("/documents/upload")
async def upload_documents(files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    created = []

    for file in files:
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        doc = Document(
            filename=file.filename,
            file_type=file.content_type,
            file_size=os.path.getsize(file_path),
            status="queued",
            progress=0
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        process_document_task.delay(doc.id)
        created.append({
            "id": doc.id,
            "filename": doc.filename,
            "status": doc.status
        })

    return {"documents": created}


@app.get("/documents", response_model=list[DocumentResponse])
def list_documents(
    search: str = "",
    status: str = "",
    sort_by: str = "created_at",
    order: str = "desc",
    db: Session = Depends(get_db)
):
    query = db.query(Document)

    if search:
        query = query.filter(Document.filename.ilike(f"%{search}%"))

    if status:
        query = query.filter(Document.status == status)

    sort_column = getattr(Document, sort_by, Document.created_at)
    query = query.order_by(desc(sort_column) if order == "desc" else asc(sort_column))

    return query.all()


@app.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@app.put("/documents/{document_id}/review", response_model=DocumentResponse)
def update_review(document_id: int, payload: DocumentUpdate, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.finalized_data = payload.finalized_data
    db.commit()
    db.refresh(doc)
    return doc


@app.put("/documents/{document_id}/finalize", response_model=DocumentResponse)
def finalize_document(document_id: int, payload: FinalizeRequest, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.finalized_data = payload.finalized_data
    doc.is_finalized = True
    db.commit()
    db.refresh(doc)
    return doc


@app.post("/documents/{document_id}/retry")
def retry_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status != "failed":
        raise HTTPException(status_code=400, detail="Only failed jobs can be retried")

    doc.status = "queued"
    doc.progress = 0
    doc.error_message = None
    db.commit()

    process_document_task.delay(doc.id)
    return {"message": "Retry started"}


@app.get("/export/json")
def export_json(db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.is_finalized == True).all()
    data = []

    for doc in docs:
        row = {
            "id": doc.id,
            "filename": doc.filename,
            "finalized_data": json.loads(doc.finalized_data) if doc.finalized_data else None
        }
        data.append(row)

    export_path = os.path.join(settings.EXPORT_DIR, "finalized_export.json")
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return {"file": export_path, "count": len(data)}


@app.get("/export/csv")
def export_csv(db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.is_finalized == True).all()
    rows = []

    for doc in docs:
        final_data = json.loads(doc.finalized_data) if doc.finalized_data else {}
        rows.append({
            "id": doc.id,
            "filename": doc.filename,
            "title": final_data.get("title", ""),
            "category": final_data.get("category", ""),
            "summary": final_data.get("summary", ""),
            "status": final_data.get("status", "")
        })

    df = pd.DataFrame(rows)
    export_path = os.path.join(settings.EXPORT_DIR, "finalized_export.csv")
    df.to_csv(export_path, index=False)

    return {"file": export_path, "count": len(rows)}
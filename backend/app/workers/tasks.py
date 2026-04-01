import json
import time
from celery_app import celery
from app.db.database import SessionLocal
from app.models.document import Document
from app.utils.progress import publish_progress


@celery.task
def process_document_task(document_id: int):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return

        doc.status = "processing"
        doc.progress = 10
        db.commit()
        publish_progress(document_id, "processing", 10, "document received")

        time.sleep(2)
        doc.progress = 25
        db.commit()
        publish_progress(document_id, "processing", 25, "parsing started")

        time.sleep(2)
        doc.progress = 45
        db.commit()
        publish_progress(document_id, "processing", 45, "parsing completed")

        time.sleep(2)
        doc.progress = 65
        db.commit()
        publish_progress(document_id, "processing", 65, "extraction started")

        time.sleep(2)
        extracted = {
            "title": doc.filename,
            "category": "general",
            "summary": f"Processed summary for {doc.filename}",
            "keywords": ["document", "processed", "sample"],
            "status": "review_pending"
        }

        doc.extracted_data = json.dumps(extracted)
        doc.progress = 85
        db.commit()
        publish_progress(document_id, "processing", 85, "extraction completed")

        time.sleep(1)
        doc.status = "completed"
        doc.progress = 100
        db.commit()
        publish_progress(document_id, "completed", 100, "job completed")

    except Exception as e:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = "failed"
            doc.error_message = str(e)
            db.commit()
        publish_progress(document_id, "failed", 0, f"job failed: {str(e)}")
    finally:
        db.close()
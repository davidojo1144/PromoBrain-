from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import csv
from io import StringIO
from ..database import SessionLocal
from ..models import Transaction
from datetime import datetime
router = APIRouter(prefix="/ingest", tags=["ingest"])
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.post("/csv")
async def ingest_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    s = content.decode("utf-8")
    f = StringIO(s)
    reader = csv.DictReader(f)
    count = 0
    for r in reader:
        t = Transaction(
            order_id=str(r.get("order_id") or ""),
            user_id=str(r.get("user_id") or ""),
            sku=str(r.get("sku") or ""),
            category=str(r.get("category") or ""),
            price=float(r.get("price") or 0),
            discount=float(r.get("discount") or 0),
            cost=float(r.get("cost") or 0),
            quantity=int(r.get("quantity") or 1),
            channel=str(r.get("channel") or "online"),
            ts=datetime.fromisoformat(r.get("ts")) if r.get("ts") else datetime.utcnow(),
        )
        db.add(t)
        count += 1
    db.commit()
    return {"rows": count}

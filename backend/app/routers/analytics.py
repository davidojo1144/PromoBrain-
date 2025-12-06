from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import SessionLocal
from ..models import Transaction
from ..schemas import OverviewMetrics, ProposalRequest, ProposalResponse, ABCreateRequest, ABResultResponse, ABResultItem
from ..services import promo, abtest
router = APIRouter(prefix="/analytics", tags=["analytics"])
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.get("/overview", response_model=OverviewMetrics)
def overview(db: Session = Depends(get_db)):
    rev = db.query(func.sum((Transaction.price - Transaction.discount) * Transaction.quantity)).scalar() or 0
    cost = db.query(func.sum(Transaction.cost * Transaction.quantity)).scalar() or 0
    orders = db.query(func.count(Transaction.order_id)).scalar() or 0
    cats = db.query(Transaction.category, func.sum((Transaction.price - Transaction.discount) * Transaction.quantity).label("rev")).group_by(Transaction.category).order_by(func.sum((Transaction.price - Transaction.discount) * Transaction.quantity).desc()).limit(5).all()
    top = [{"category": c[0], "revenue": float(c[1] or 0)} for c in cats]
    return {"revenue": float(rev), "margin": float(rev - cost), "orders": int(orders), "top_categories": top}
@router.post("/propose", response_model=ProposalResponse)
def propose(req: ProposalRequest, db: Session = Depends(get_db)):
    res = promo.propose(db, req.objective, req.min_margin_pct)
    return res
@router.post("/ab/create")
def create_ab(req: ABCreateRequest, db: Session = Depends(get_db)):
    tid = abtest.create_abtest(db, req.campaign_name, req.variant_a_pct, req.variant_b_pct, req.kpi)
    return {"abtest_id": tid}
@router.get("/ab/{abtest_id}", response_model=ABResultResponse)
def ab_results(abtest_id: int, db: Session = Depends(get_db)):
    items = abtest.compute_results(db, abtest_id)
    return {"items": [ABResultItem(**i) for i in items]}

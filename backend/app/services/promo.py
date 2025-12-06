import os
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Transaction
def propose(db: Session, objective: str, min_margin_pct: float) -> Dict:
    q = db.query(Transaction.category, func.sum((Transaction.price - Transaction.discount) * Transaction.quantity).label("rev"), func.sum((Transaction.price - Transaction.discount - Transaction.cost) * Transaction.quantity).label("margin")).group_by(Transaction.category).order_by(func.sum((Transaction.price - Transaction.discount) * Transaction.quantity).desc())
    rows = q.limit(3).all()
    if not rows:
        return {"name": "Starter Promo", "description": "Sitewide limited promo", "target_segment": "all", "discount_pct": 5.0, "expected_uplift_pct": 3.0}
    top = max(rows, key=lambda r: r.margin / r.rev if r.rev else 0)
    margin_rate = (top.margin / top.rev) if top.rev else 0
    base_discount = max(0.0, round((margin_rate - min_margin_pct) * 100 * 0.5, 1))
    discount = max(3.0, min(25.0, base_discount))
    uplift = round(2.0 + discount * 0.6, 1)
    return {"name": f"Boost {top.category}", "description": f"Targeted promo on {top.category}", "target_segment": top.category, "discount_pct": discount, "expected_uplift_pct": uplift}

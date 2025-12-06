from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from ..models import Transaction, ABTest, ABResult, Campaign
from datetime import datetime, timedelta
def create_abtest(db: Session, campaign_name: str, a_pct: float, b_pct: float, kpi: str) -> int:
    c = Campaign(name=campaign_name, status="draft", start_date=datetime.utcnow(), end_date=datetime.utcnow() + timedelta(days=14), created_at=datetime.utcnow())
    db.add(c)
    db.flush()
    t = ABTest(campaign_id=c.id, variant_a_pct=a_pct, variant_b_pct=b_pct, kpi=kpi, status="running")
    db.add(t)
    db.flush()
    return t.id
def compute_results(db: Session, abtest_id: int) -> List[Dict]:
    split = db.query(ABTest).filter(ABTest.id == abtest_id).first()
    if not split:
        return []
    users = db.query(Transaction.user_id).group_by(Transaction.user_id).all()
    users = [u[0] for u in users]
    a_users = set(users[: max(1, int(len(users) * split.variant_a_pct))])
    agg = db.query(
        Transaction.user_id,
        func.sum((Transaction.price - Transaction.discount) * Transaction.quantity).label("rev"),
        func.sum((Transaction.cost) * Transaction.quantity).label("cost"),
        func.count(Transaction.order_id).label("orders")
    ).group_by(Transaction.user_id).all()
    a_rev = 0.0
    a_cost = 0.0
    a_orders = 0
    b_rev = 0.0
    b_cost = 0.0
    b_orders = 0
    for row in agg:
        if row.user_id in a_users:
            a_rev += row.rev or 0
            a_cost += row.cost or 0
            a_orders += row.orders or 0
        else:
            b_rev += row.rev or 0
            b_cost += row.cost or 0
            b_orders += row.orders or 0
    res = [
        {"variant": "A", "impressions": a_orders, "conversions": a_orders, "revenue": round(a_rev, 2), "cost": round(a_cost, 2), "margin": round(a_rev - a_cost, 2)},
        {"variant": "B", "impressions": b_orders, "conversions": b_orders, "revenue": round(b_rev, 2), "cost": round(b_cost, 2), "margin": round(b_rev - b_cost, 2)}
    ]
    return res

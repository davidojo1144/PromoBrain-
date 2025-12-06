from app.services.promo import propose
from app.database import SessionLocal, Base, engine
from app.models import Transaction
from datetime import datetime
def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
def test_propose_returns_result():
    db = SessionLocal()
    t = Transaction(order_id="1", user_id="u1", sku="s1", category="Home", price=100, discount=10, cost=60, quantity=1, channel="online", ts=datetime.utcnow())
    db.add(t)
    db.commit()
    res = propose(db, "revenue", 0.2)
    assert "discount_pct" in res
    db.close()

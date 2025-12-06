from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base
class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, index=True)
    user_id = Column(String, index=True)
    sku = Column(String, index=True)
    category = Column(String, index=True)
    price = Column(Float)
    discount = Column(Float)
    cost = Column(Float)
    quantity = Column(Integer)
    channel = Column(String)
    ts = Column(DateTime, index=True)
class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    status = Column(String, index=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime)
class ABTest(Base):
    __tablename__ = "abtests"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    variant_a_pct = Column(Float)
    variant_b_pct = Column(Float)
    kpi = Column(String)
    status = Column(String)
    campaign = relationship("Campaign")
class ABResult(Base):
    __tablename__ = "abresults"
    id = Column(Integer, primary_key=True, index=True)
    abtest_id = Column(Integer, ForeignKey("abtests.id"))
    variant = Column(String)
    impressions = Column(Integer)
    conversions = Column(Integer)
    revenue = Column(Float)
    cost = Column(Float)
    margin = Column(Float)
    abtest = relationship("ABTest")

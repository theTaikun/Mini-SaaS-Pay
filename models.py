import datetime
from sqlalchemy import Column, Boolean, DateTime, Integer, String
from sqlalchemy.orm import  declarative_base

from definitions import engine

Base = declarative_base()

class User(Base):
    __tablename__ = "USERS"

    id = Column(Integer, primary_key=True, index=True)
    email= Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    createdDt = Column(
        String,
        nullable=False,
        default=lambda: datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00","Z"),
        )

    # -----------
    # Stripe Data
    # -----------
    customer_id = Column(String, nullable=True) # Initially created prior to Stripe
    subscription_id = Column(String, nullable=True)
    status = Column(String, nullable=True, default=None)
    price_id = Column(String, nullable=True)
    current_period_start = Column(Integer, nullable=True)
    current_period_end = Column(Integer, nullable=True)
    cancel_at_period_end = Column(Boolean, nullable=True)


Base.metadata.create_all(engine)

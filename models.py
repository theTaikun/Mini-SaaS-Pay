import datetime
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import  declarative_base

from definitions import engine

Base = declarative_base()

class User(Base):
    __tablename__ = "USERS"

    id = Column(Integer, primary_key=True, index=True)
    email= Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    customer_id = Column(String, nullable=True) # Initially created prior to Stripe
    createdDt = Column(
        String,
        nullable=False,
        default=lambda: datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00","Z"),
        )

Base.metadata.create_all(engine)

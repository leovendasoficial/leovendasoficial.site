from sqlalchemy import Column, Integer, String, Float, Text, Boolean
from backend.db import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(160), nullable=False)
    slug = Column(String(180), unique=True, index=True, nullable=False)
    description = Column(Text, default="")
    price = Column(Float, nullable=False)
    image_url = Column(String(500), default="")
    category = Column(String(80), default="Geral")
    is_active = Column(Boolean, default=True)

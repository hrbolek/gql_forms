import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .BaseModel import BaseModel, UUIDFKey

class RequestCategoryModel(BaseModel):
    """Model representing a form request."""

    __tablename__ = "formrequestcategories"

    name: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="Name of the request category")
    name_en: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="English name of the request category")
    
    
    # Relationships
    types = relationship(
        "RequestTypeModel", 
        uselist=True, 
        default_factory=list,
        viewonly=True
    )

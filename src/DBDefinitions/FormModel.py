import uuid
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .BaseModel import BaseModel, UUIDFKey

class FormModel(BaseModel):
    """Model representing a form."""

    __tablename__ = "forms"

    name: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="Name of the form")
    name_en: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="English name of the form")
    
    status: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="Status of the form")
    valid: Mapped[bool] = mapped_column(Boolean, default=True, comment="Indicates if the form is valid")
    
    type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("formtypes.id"), index=True, nullable=True, default=None, comment="Foreign key to form types")
    state_id: Mapped[uuid.UUID] = UUIDFKey(nullable=True, comment="State of the request")
    
    # Relationships
    type = relationship(
        "FormTypeModel", 
        back_populates="forms", 
        default=None, 
        uselist=False, 
        viewonly=True
    )
    sections = relationship(
        "SectionModel", 
        back_populates="form", 
        default_factory=list,
        uselist=True, 
        viewonly=True
    )
    history = relationship(
        "HistoryModel", 
        back_populates="form", 
        default=None, 
        uselist=False, 
        viewonly=True
    )

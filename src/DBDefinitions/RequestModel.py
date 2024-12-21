import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .BaseModel import BaseModel, UUIDFKey

class RequestModel(BaseModel):
    """Model representing a form request."""

    __tablename__ = "formrequests"

    name: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="Name of the request")
    name_en: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="English name of the request")
    
    form_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("forms.id"), 
        nullable=True, 
        default=None, 
        comment="Active request form, others are linked by histories"
    )
    
    state_id: Mapped[uuid.UUID] = UUIDFKey(nullable=True, comment="State of the request")
    
    # Relationships
    histories: Mapped[list["HistoryModel"]] = relationship(
        "HistoryModel", 
        back_populates="request", 
        uselist=True, 
        default_factory=list,
        viewonly=True, 
        lazy="selectin"
    )
    form: Mapped["FormModel"] = relationship(
        "FormModel", 
        uselist=False,
        default=None,  
        viewonly=True, 
        lazy="selectin"
    )

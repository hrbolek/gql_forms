import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .BaseModel import BaseModel, UUIDFKey

class HistoryModel(BaseModel):
    """Model representing a history record for forms."""

    __tablename__ = "formhistories"

    name: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="A notice describing a reason")
    name_en: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="English description of the reason")
    
    request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("formrequests.id"), 
        index=True, 
        nullable=True, 
        default=None, 
        comment="Foreign key to form requests"
    )
    form_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("forms.id"), 
        index=True, 
        nullable=True, 
        default=None, 
        comment="Foreign key to forms"
    )
    
    state_id: Mapped[uuid.UUID] = UUIDFKey(nullable=True, comment="State of the request")
    
    # Relationships
    form: Mapped["FormModel"] = relationship(
        "FormModel", 
        back_populates="history", 
        default=None, 
        uselist=False
    )
    request: Mapped["RequestModel"] = relationship(
        "RequestModel", 
        back_populates="histories", 
        default=None, 
        uselist=False
    )

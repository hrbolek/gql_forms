import uuid
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .BaseModel import BaseModel, UUIDFKey

class SectionModel(BaseModel):
    """Model representing a section within a form."""

    __tablename__ = "formsections"

    name: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="Name of the section")
    name_en: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="English name of the section")
    
    form_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("forms.id"), 
        index=True, 
        nullable=True, 
        default=None, 
        comment="Foreign key to the associated form"
    )
    order: Mapped[int] = mapped_column(Integer, nullable=True, default=None, comment="Order in the parent entity")
    status: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="Status of the section")
    
    state_id: Mapped[uuid.UUID] = UUIDFKey(nullable=True, comment="State of the request")
    
    # Relationships
    form: Mapped["FormModel"] = relationship(
        "FormModel", 
        default=None, 
        back_populates="sections"
    )
    parts: Mapped[list["PartModel"]] = relationship(
        "PartModel", 
        back_populates="section", 
        default_factory=list,
        uselist=True
    )

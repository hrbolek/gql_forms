import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .BaseModel import BaseModel, UUIDFKey

class RequestTypeModel(BaseModel):
    """Model representing a form request."""

    __tablename__ = "formrequesttypes"

    name: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="Name of the request type")
    name_en: Mapped[str] = mapped_column(String, nullable=True, default=None, comment="English name of the request type")
    
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("formrequestcategories.id"), 
        nullable=True, 
        default=None, 
        comment="category"
    )
    template_form_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("forms.id"), 
        nullable=True, 
        default=None, 
        comment="form which is template to new request"
    )
    statemachine_id: Mapped[uuid.UUID] = UUIDFKey(nullable=True, comment="set of states related to the request")
    state_id: Mapped[uuid.UUID] = UUIDFKey(nullable=True, comment="Starting state of the request")
    group_id: Mapped[uuid.UUID] = UUIDFKey(nullable=True, comment="Group od users allowed to create new request")

    # Relationships
    requests = relationship(
        "RequestModel", 
        uselist=True, 
        default_factory=list,
        viewonly=True
    )
    template_form = relationship(
        "FormModel", 
        uselist=False,
        default=None,  
        viewonly=True
    )    
    category = relationship(
        "RequestCategoryModel", 
        uselist=False,
        default=None,  
        viewonly=True
    )
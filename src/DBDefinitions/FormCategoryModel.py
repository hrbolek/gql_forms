from sqlalchemy.orm import relationship

from sqlalchemy.orm import Mapped, mapped_column
from .BaseModel import BaseModel

class FormCategoryModel(BaseModel):
    """Model representing a form category."""

    __tablename__ = "formcategories"

    name: Mapped[str] = mapped_column(nullable=False, default=None, comment="Name of the category")
    name_en: Mapped[str] = mapped_column(nullable=False, default=None, comment="English name of the category")

    types = relationship("FormTypeModel", back_populates="category", uselist=True)
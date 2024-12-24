import strawberry
import datetime
import typing
import uuid

from typing import Annotated
# from src.utils.Dataloaders import getLoadersFromInfo, getUserFromInfo
from uoishelpers.gqlpermissions import (
    OnlyForAuthentized, 
    SimpleInsertPermission,
    SimpleUpdatePermission,
    SimpleDeletePermission
)

from uoishelpers.resolvers import (
    getLoadersFromInfo,
    VectorResolver,
    PageResolver,
    ScalarResolver,
    Insert, InsertError,
    Update, UpdateError,
    Delete, DeleteError
)
from .BaseGQLModel import BaseGQLModel, IDType

FormCategoryGQLModel = Annotated["FormCategoryGQLModel", strawberry.lazy(".FormCategoryGQLModel")]
FormGQLModel = Annotated["FormGQLModel", strawberry.lazy(".FormGQLModel")]

@strawberry.federation.type(
    keys=["id"], description="Entity representing a form type"
)
class FormTypeGQLModel(BaseGQLModel):
    """
    GraphQL model for the FormType entity.
    Represents different types of forms with metadata such as name and category.
    """
    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        return getLoadersFromInfo(info=info).formtypes

    name: typing.Optional[str] = strawberry.field(
        description="Name of the form type",
        permission_classes=[OnlyForAuthentized]
    )
    name_en: typing.Optional[str] = strawberry.field(
        description="English name of the form type",
        permission_classes=[OnlyForAuthentized]
    )
    category_id: typing.Optional[IDType] = strawberry.field(
        description="Foreign key to the form category",
        permission_classes=[OnlyForAuthentized]
    )
    category: typing.Optional[FormCategoryGQLModel] = strawberry.field(
        description="The category this form type belongs to",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["FormCategoryGQLModel"](fkey_field_name="category_id")
    )
    
    @strawberry.field(
        description="",
        permission_classes=[OnlyForAuthentized])
    async def forms(self, info: strawberry.types.Info) -> typing.List["FormGQLModel"]:
        loader = getLoadersFromInfo(info).forms
        rows = await loader.filter_by(type_id=self.id)
        return rows
#############################################################
#
# Queries
#
#############################################################

@strawberry.field(
    description="Retrieves the form type",
    permission_classes=[OnlyForAuthentized])
async def form_type_by_id(
    self, info: strawberry.types.Info, id: uuid.UUID
) -> typing.Optional[FormTypeGQLModel]:
    result = await FormTypeGQLModel.resolve_reference(info=info, id=id)
    return result

from dataclasses import dataclass
from uoishelpers.resolvers import createInputs

# FormWhereFilter = Annotated["FormWhereFilter", strawberry.lazy(".FormGQLModel")]
@createInputs
@dataclass
class FormTypeInputFilter:
    name: str
    name_en: str
    id: uuid.UUID
    # from .FormGQLModel import FormWhereFilter
    # forms: FormWhereFilter

form_type_page = strawberry.field(
    description="Retrieves the form type",
    permission_classes=[OnlyForAuthentized],
    graphql_type=typing.List[FormTypeGQLModel],
    resolver=PageResolver[FormTypeGQLModel](whereType=FormTypeInputFilter)
    )
#############################################################
#
# Mutations
#
#############################################################

@strawberry.input(description="Attributes for creating a new form type")
class FormTypeInsertGQLModel:
    category_id: IDType = strawberry.field(description="ID of the form category")    
    id: typing.Optional[IDType] = strawberry.field(
        description="Client-generated ID for the form type (optional)", default=None
    )
    name: typing.Optional[str] = strawberry.field(description="Name of the form type", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="English name of the form type", default=None)
    createdby_id: strawberry.Private[uuid.UUID] = None 

@strawberry.input(description="Attributes for updating an existing form type")
class FormTypeUpdateGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the form type to update")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )
    name: typing.Optional[str] = strawberry.field(description="Updated name of the form type", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="Updated English name of the form type", default=None)
    changedby_id: strawberry.Private[uuid.UUID] = None

@strawberry.input(description="Attributes for deleting an existing form type")
class FormTypeDeleteGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the form type to delete")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )

@strawberry.mutation(
    description="Create a new form type",
    permission_classes=[
        OnlyForAuthentized,
        SimpleInsertPermission[FormTypeGQLModel](roles=["administrátor"]),
    ],
)
async def form_type_insert(
    self, info: strawberry.types.Info, form_type: FormTypeInsertGQLModel
) -> typing.Union[FormTypeGQLModel, InsertError[FormTypeGQLModel]]:
    return await Insert[FormTypeGQLModel].DoItSafeWay(info=info, entity=form_type)

@strawberry.mutation(
    description="Update an existing form type",
    permission_classes=[
        OnlyForAuthentized,
        SimpleUpdatePermission[FormTypeGQLModel](roles=["administrátor"]),
    ],
)
async def form_type_update(
    self, info: strawberry.types.Info, form_type: FormTypeUpdateGQLModel
) -> typing.Union[FormTypeGQLModel, UpdateError[FormTypeGQLModel]]:
    return await Update[FormTypeGQLModel].DoItSafeWay(info=info, entity=form_type)

@strawberry.mutation(
    description="Delete an existing form type",
    permission_classes=[
        OnlyForAuthentized,
        SimpleDeletePermission[FormTypeGQLModel](roles=["administrátor"]),
    ],
)
async def form_type_delete(
    self, info: strawberry.types.Info, form_type: FormTypeDeleteGQLModel
) -> typing.Optional[DeleteError[FormTypeGQLModel]]:
    return await Delete[FormTypeGQLModel].DoItSafeWay(info=info, entity=form_type)
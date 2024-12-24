import dataclasses
import strawberry
import datetime
import typing
import uuid

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
    Insert, InsertError,
    Update, UpdateError,
    Delete, DeleteError
)
from .BaseGQLModel import BaseGQLModel, IDType


FormTypeGQLModel = typing.Annotated["FormTypeGQLModel", strawberry.lazy(".FormTypeGQLModel")]

@strawberry.federation.type(
    keys=["id"], description="""Entity representing a category of form types"""
)
class FormCategoryGQLModel(BaseGQLModel):
    """
    """
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).formcategories

    @classmethod
    def from_dataclass(cls, db_row):
        db_row_dict = dataclasses.asdict(db_row)
        db_row_dict["valid"] = db_row.valid
        instance = cls(**db_row_dict)
        return instance

    # @classmethod
    # async def resolve_reference(cls, info: strawberry.types.Info, id: uuid.UUID):
    # implementation is inherited

    name: str = strawberry.field(
        description="Name of the form category",
        permission_classes=[OnlyForAuthentized]
    )

    name_en: str = strawberry.field(
        description="English name of the form category",
        permission_classes=[OnlyForAuthentized]
    )

    form_types: typing.List[FormTypeGQLModel] = strawberry.field(
        description="All types from this category",
        resolver=VectorResolver[FormTypeGQLModel](fkey_field_name="category_id")
    )

#############################################################
#
# Queries
#
#############################################################

from dataclasses import dataclass
from uoishelpers.resolvers import createInputs

@createInputs
@dataclass
class FormCategoryInputFilter:
    id: IDType
    name: str
    name_en: str

from src.DBResolvers import FormCategoryResolvers
@strawberry.field(
    description=""
)
async def form_category_by_id(self, info: strawberry.types.Info, id: uuid.UUID) -> typing.Optional["FormCategoryGQLModel"]:
    result = await FormCategoryGQLModel.resolve_reference(info=info, id=id)
    return result

form_category_page = strawberry.field(
    description='Retrieves the form categories',
    graphql_type=typing.List[FormCategoryGQLModel],
    resolver=PageResolver[FormCategoryGQLModel](whereType=FormCategoryInputFilter)
)

#############################################################
#
# Mutations
#
#############################################################

@strawberry.input(description="Attributes for creating a new form category")
class FormCategoryInsertGQLModel:
    name: str = strawberry.field(description="Name of the form category")
    name_en: str = strawberry.field(description="English name of the form category")
    id: typing.Optional[IDType] = strawberry.field(description="Client-generated ID (optional)", default=None)
    createdby_id: strawberry.Private[uuid.UUID] = None

@strawberry.input(description="Attributes for updating an existing form category")
class FormCategoryUpdateGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the form category to update")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification to ensure data consistency"
    )
    name: typing.Optional[str] = strawberry.field(description="Updated name of the form category", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="Updated English name of the form category", default=None)

    changedby_id: strawberry.Private[uuid.UUID] = None

@strawberry.input(description="Attributes for deleting an existing form category")
class FormCategoryDeleteGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the form category to delete")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification to ensure data consistency"
    )

@strawberry.mutation(
    description="Create a new form category",
    permission_classes=[
        OnlyForAuthentized,
        SimpleInsertPermission[FormCategoryGQLModel](roles=["administrátor"]),
    ],
)
async def form_category_insert(
    self, info: strawberry.types.Info, category: FormCategoryInsertGQLModel
) -> typing.Union[FormCategoryGQLModel, InsertError[FormCategoryGQLModel]]:
    return await Insert[FormCategoryGQLModel].DoItSafeWay(info=info, entity=category)

@strawberry.mutation(
    description="Update an existing form category",
    permission_classes=[
        OnlyForAuthentized,
        SimpleUpdatePermission[FormCategoryGQLModel](roles=["administrator"]),
    ],
)
async def form_category_update(
    self, info: strawberry.types.Info, category: FormCategoryUpdateGQLModel
) -> typing.Union[FormCategoryGQLModel, UpdateError[FormCategoryGQLModel]]:
    return await Update[FormCategoryGQLModel].DoItSafeWay(info=info, entity=category)

@strawberry.mutation(
    description="Delete an existing form category",
    permission_classes=[
        OnlyForAuthentized,
        SimpleDeletePermission[FormCategoryGQLModel](roles=["administrátor"]),
    ],
)
async def form_category_delete(
    self, info: strawberry.types.Info, category: FormCategoryDeleteGQLModel
) -> typing.Optional[DeleteError[FormCategoryGQLModel]]:
    return await Delete[FormCategoryGQLModel].DoItSafeWay(info=info, entity=category)
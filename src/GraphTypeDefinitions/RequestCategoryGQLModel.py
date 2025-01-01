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


RequestTypeGQLModel = typing.Annotated["RequestTypeGQLModel", strawberry.lazy(".RequestTypeGQLModel")]

@strawberry.federation.type(
    keys=["id"], description="""Entity representing a category of request types"""
)
class RequestCategoryGQLModel(BaseGQLModel):
    """
    """
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).formrequestcategories

    name: str = strawberry.field(
        description="Name of the request category",
        permission_classes=[OnlyForAuthentized]
    )

    name_en: str = strawberry.field(
        description="English name of the request category",
        permission_classes=[OnlyForAuthentized]
    )
    from .RequestTypeGQLModel import RequestTypeInputFilter
    request_types: typing.List[RequestTypeGQLModel] = strawberry.field(
        description="All types from this category",
        resolver=VectorResolver[RequestTypeGQLModel](fkey_field_name="category_id", whereType=RequestTypeInputFilter)
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
class RequestCategoryInputFilter:
    id: IDType
    name: str
    name_en: str

@strawberry.field(
    description=""
)
async def request_category_by_id(self, info: strawberry.types.Info, id: uuid.UUID) -> typing.Optional["RequestCategoryGQLModel"]:
    result = await RequestCategoryGQLModel.resolve_reference(info=info, id=id)
    return result

request_category_page = strawberry.field(
    description='Retrieves the request categories',
    graphql_type=typing.List[RequestCategoryGQLModel],
    resolver=PageResolver[RequestCategoryGQLModel](whereType=RequestCategoryInputFilter)
)

#############################################################
#
# Mutations
#
#############################################################

@strawberry.input(description="Attributes for creating a new request category")
class RequestCategoryInsertGQLModel:
    name: str = strawberry.field(description="Name of the request category")
    name_en: str = strawberry.field(description="English name of the request category")
    id: typing.Optional[IDType] = strawberry.field(description="Client-generated ID (optional)", default=None)
    createdby_id: strawberry.Private[uuid.UUID] = None

@strawberry.input(description="Attributes for updating an existing request category")
class RequestCategoryUpdateGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the request category to update")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification to ensure data consistency"
    )
    name: typing.Optional[str] = strawberry.field(description="Updated name of the request category", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="Updated English name of the request category", default=None)

    changedby_id: strawberry.Private[uuid.UUID] = None

@strawberry.input(description="Attributes for deleting an existing request category")
class RequestCategoryDeleteGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the request category to delete")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification to ensure data consistency"
    )

@strawberry.mutation(
    description="Create a new request category",
    permission_classes=[
        OnlyForAuthentized,
        SimpleInsertPermission[RequestCategoryGQLModel](roles=["administrátor"]),
    ],
)
async def request_category_insert(
    self, info: strawberry.types.Info, category: RequestCategoryInsertGQLModel
) -> typing.Union[RequestCategoryGQLModel, InsertError[RequestCategoryGQLModel]]:
    return await Insert[RequestCategoryGQLModel].DoItSafeWay(info=info, entity=category)

@strawberry.mutation(
    description="Update an existing request category",
    permission_classes=[
        OnlyForAuthentized,
        SimpleUpdatePermission[RequestCategoryGQLModel](roles=["administrátor"]),
    ],
)
async def request_category_update(
    self, info: strawberry.types.Info, category: RequestCategoryUpdateGQLModel
) -> typing.Union[RequestCategoryGQLModel, UpdateError[RequestCategoryGQLModel]]:
    return await Update[RequestCategoryGQLModel].DoItSafeWay(info=info, entity=category)

@strawberry.mutation(
    description="Delete an existing request category",
    permission_classes=[
        OnlyForAuthentized,
        SimpleDeletePermission[RequestCategoryGQLModel](roles=["administrátor"]),
    ],
)
async def request_category_delete(
    self, info: strawberry.types.Info, category: RequestCategoryDeleteGQLModel
) -> typing.Optional[DeleteError[RequestCategoryGQLModel]]:
    return await Delete[RequestCategoryGQLModel].DoItSafeWay(info=info, entity=category)
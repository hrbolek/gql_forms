import strawberry
import typing
import datetime
import uuid

from typing import Annotated

from uoishelpers.gqlpermissions import (
    OnlyForAuthentized, 
    SimpleInsertPermission,
    SimpleUpdatePermission,
    SimpleDeletePermission
)

from uoishelpers.resolvers import (
    getLoadersFromInfo,
    VectorResolver,
    ScalarResolver,
    PageResolver,
    Insert, InsertError,
    Update, UpdateError,
    Delete, DeleteError
)
from .BaseGQLModel import BaseGQLModel, IDType

ItemCategoryGQLModel = Annotated["ItemCategoryGQLModel", strawberry.lazy(".ItemCategoryGQLModel")]
ItemGQLModel = Annotated["ItemGQLModel", strawberry.lazy(".ItemGQLModel")]

@strawberry.federation.type(
    keys=["id"], 
    name="FormItemTypeGQLModel",
    description="""Type representing an item type"""
)
class ItemTypeGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).formitemtypes
    
    # @classmethod
    # async def resolve_reference(cls, info: strawberry.types.Info, id: uuid.UUID):
    # implementation is inherited

    name: typing.Optional[str] = strawberry.field(
        description="Name of the item type",
        permission_classes=[OnlyForAuthentized]
    )
    name_en: typing.Optional[str] = strawberry.field(
        description="English name of the item type",
        permission_classes=[OnlyForAuthentized]
    )
    query: typing.Optional[str] = strawberry.field(
        description="API query associated with the item type",
        permission_classes=[OnlyForAuthentized]
    )
    selector: typing.Optional[str] = strawberry.field(
        description="Selector for picking the right value from the query",
        permission_classes=[OnlyForAuthentized]
    )
    category_id: typing.Optional[IDType] = strawberry.field(
        description="Foreign key to item category",
        permission_classes=[OnlyForAuthentized]
    )
    
    category: typing.Optional[ItemCategoryGQLModel] = strawberry.field(
        description="The category this item type belongs to",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["ItemCategoryGQLModel"](fkey_field_name="category_id")
    )
    
    # @strawberry.field(
    #     description="",
    #     permission_classes=[OnlyForAuthentized])
    # async def items(self, info: strawberry.types.Info) -> typing.List["ItemGQLModel"]:
    #     loader = getLoadersFromInfo(info).items
    #     rows = await loader.filter_by(type_id=self.id)
    #     return rows       
#############################################################
#
# Queries
#
#############################################################
from src.DBResolvers import ItemTypeResolvers

from dataclasses import dataclass
from uoishelpers.resolvers import createInputs

@createInputs
@dataclass
class FormItemTypeWhereFilter:
    id: uuid.UUID
    name: str
    category_id: uuid.UUID

# @strawberry.field(
#     description="Retrieves the item types",
#     permission_classes=[OnlyForAuthentized])
# async def item_type_page(
#     self, info: strawberry.types.Info, skip: int = 0, limit: int = 10
# ) -> typing.List[ItemCategoryGQLModel]:
#     loader = getLoadersFromInfo(info).itemtypes
#     result = await loader.page(skip=skip, limit=limit)
#     return result

item_type_page = strawberry.field(
    description="Retrieves the item types",
    resolver=ItemTypeResolvers.Page(GQLModel=ItemTypeGQLModel, WhereFilterModel=FormItemTypeWhereFilter),
    permission_classes=[
        OnlyForAuthentized
    ]
)

@strawberry.field(
    description="Retrieves the item type",
    permission_classes=[OnlyForAuthentized])
async def item_type_by_id(
    self, info: strawberry.types.Info, id: uuid.UUID
) -> typing.Optional[ItemTypeGQLModel]:
    result = await ItemTypeGQLModel.resolve_reference(info=info, id=id)
    return result

#############################################################
#
# Mutations
#
#############################################################


@strawberry.input(description="Input structure - C operation")
class FormItemTypeInsertGQLModel:
    name: str = strawberry.field(description="Item type name")
    id: typing.Optional[uuid.UUID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    createdby: strawberry.Private[uuid.UUID] = None 

@strawberry.input(description="Input structure - U operation")
class FormItemTypeUpdateGQLModel:
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    name: typing.Optional[str] = strawberry.field(description="Item type name", default=None)
    order: typing.Optional[int] = None
    changedby: strawberry.Private[uuid.UUID] = None

@strawberry.input(description="Attributes for creating a new item type")
class ItemTypeInsertGQLModel:
    id: typing.Optional[IDType] = strawberry.field(
        description="Client-generated ID for the item type (optional)", default=None
    )
    name: typing.Optional[str] = strawberry.field(description="Name of the item type", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="English name of the item type", default=None)
    query: typing.Optional[str] = strawberry.field(description="API query for the item type", default=None)
    selector: typing.Optional[str] = strawberry.field(description="Selector for the query", default=None)
    category_id: typing.Optional[IDType] = strawberry.field(description="ID of the item category", default=None)
    createdby_id: strawberry.Private[uuid.UUID] = None 

@strawberry.input(description="Attributes for updating an existing item type")
class ItemTypeUpdateGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the item type to update")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )
    name: typing.Optional[str] = strawberry.field(description="Updated name of the item type", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="Updated English name of the item type", default=None)
    query: typing.Optional[str] = strawberry.field(description="Updated API query for the item type", default=None)
    selector: typing.Optional[str] = strawberry.field(description="Updated selector for the query", default=None)
    category_id: typing.Optional[IDType] = strawberry.field(description="Updated item category ID", default=None)
    changedby_id: strawberry.Private[uuid.UUID] = None

@strawberry.input(description="Attributes for deleting an existing item type")
class ItemTypeDeleteGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the item type to delete")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )

@strawberry.mutation(
    description="Create a new item type",
    permission_classes=[
        OnlyForAuthentized,
        SimpleInsertPermission[ItemTypeGQLModel](roles=["administrator"]),
    ],
)
async def item_type_insert(
    self, info: strawberry.types.Info, item_type: ItemTypeInsertGQLModel
) -> typing.Union[ItemTypeGQLModel, InsertError[ItemTypeGQLModel]]:
    return await Insert[ItemTypeGQLModel].DoItSafeWay(info=info, entity=item_type)

@strawberry.mutation(
    description="Update an existing item type",
    permission_classes=[
        OnlyForAuthentized,
        SimpleUpdatePermission[ItemTypeGQLModel](roles=["administrator"]),
    ],
)
async def item_type_update(
    self, info: strawberry.types.Info, item_type: ItemTypeUpdateGQLModel
) -> typing.Union[ItemTypeGQLModel, UpdateError[ItemTypeGQLModel]]:
    return await Update[ItemTypeGQLModel].DoItSafeWay(info=info, entity=item_type)

@strawberry.mutation(
    description="Delete an existing item type",
    permission_classes=[
        OnlyForAuthentized,
        SimpleDeletePermission[ItemTypeGQLModel](roles=["administrator"]),
    ],
)
async def item_type_delete(
    self, info: strawberry.types.Info, item_type: ItemTypeDeleteGQLModel
) -> typing.Optional[DeleteError[ItemTypeGQLModel]]:
    return await Delete[ItemTypeGQLModel].DoItSafeWay(info=info, entity=item_type)
import strawberry
import typing
import datetime
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


ItemTypeGQLModel = typing.Annotated["ItemTypeGQLModel", strawberry.lazy(".ItemTypeGQLModel")]

@strawberry.federation.type(
    keys=["id"], 
    name="FormItemCategoryGQLModel",
    description="""Type representing an item category"""
)
class ItemCategoryGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).itemcategories
    
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
    
    @strawberry.field(
        description="Returns all type for this category",
        permission_classes=[OnlyForAuthentized])
    async def types(self, info: strawberry.types.Info) -> typing.List["ItemTypeGQLModel"]:
        loader = getLoadersFromInfo(info).itemtypes
        rows = await loader.filter_by(category_id=self.id)
        return rows   

#############################################################
#
# Queries
#
#############################################################
from src.DBResolvers import ItemCategoryResolvers

from dataclasses import dataclass
from uoishelpers.resolvers import createInputs

@createInputs
@dataclass
class FormItemCategoryInputFilter:
    id: uuid.UUID
    name: str
    category_id: uuid.UUID

item_category_page = strawberry.field(
    description="Retrieves the item categories",
    permission_classes=[
        OnlyForAuthentized
    ],
    graphql_type=typing.List[ItemCategoryGQLModel],
    resolver=PageResolver[ItemCategoryGQLModel](whereType=FormItemCategoryInputFilter)
    )

@strawberry.field(
    description="Retrieves the item category",
    permission_classes=[OnlyForAuthentized])
async def item_category_by_id(
    self, info: strawberry.types.Info, id: uuid.UUID
) -> typing.Optional[ItemCategoryGQLModel]:
    result = await ItemCategoryGQLModel.resolve_reference(info=info, id=id)
    return result

#############################################################
#
# Mutations
#
#############################################################


@strawberry.input(description="Input structure - C operation")
class FormItemCategoryInsertGQLModel:
    name: str = strawberry.field(description="Item category name")
    id: typing.Optional[uuid.UUID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    createdby: strawberry.Private[uuid.UUID] = None 

@strawberry.input(description="Input structure - U operation")
class FormItemCategoryUpdateGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")

    name: typing.Optional[str] = strawberry.field(description="Item category name", default=None)
    changedby: strawberry.Private[uuid.UUID] = None


@strawberry.input(description="Attributes for creating a new item category")
class ItemCategoryInsertGQLModel:
    id: typing.Optional[IDType] = strawberry.field(
        description="Client-generated ID for the item category (optional)", default=None
    )
    name: typing.Optional[str] = strawberry.field(description="Name of the category", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="English name of the category", default=None)
    createdby_id: strawberry.Private[uuid.UUID] = None 

@strawberry.input(description="Attributes for updating an existing item category")
class ItemCategoryUpdateGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the item category to update")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )
    name: typing.Optional[str] = strawberry.field(description="Updated name of the category", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="Updated English name of the category", default=None)
    changedby_id: strawberry.Private[uuid.UUID] = None

@strawberry.input(description="Attributes for deleting an existing item category")
class ItemCategoryDeleteGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the item category to delete")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )


@strawberry.mutation(
    description="Create a new item category",
    permission_classes=[
        OnlyForAuthentized,
        SimpleInsertPermission[ItemCategoryGQLModel](roles=["administrator"]),
    ],
)
async def item_category_insert(
    self, info: strawberry.types.Info, category: ItemCategoryInsertGQLModel
) -> typing.Union[ItemCategoryGQLModel, InsertError[ItemCategoryGQLModel]]:
    return await Insert[ItemCategoryGQLModel].DoItSafeWay(info=info, entity=category)

@strawberry.mutation(
    description="Update an existing item category",
    permission_classes=[
        OnlyForAuthentized,
        SimpleUpdatePermission[ItemCategoryGQLModel](roles=["administrator"]),
    ],
)
async def item_category_update(
    self, info: strawberry.types.Info, category: ItemCategoryUpdateGQLModel
) -> typing.Union[ItemCategoryGQLModel, UpdateError[ItemCategoryGQLModel]]:
    return await Update[ItemCategoryGQLModel].DoItSafeWay(info=info, entity=category)

@strawberry.mutation(
    description="Delete an existing item category",
    permission_classes=[
        OnlyForAuthentized,
        SimpleDeletePermission[ItemCategoryGQLModel](roles=["administrator"]),
    ],
)
async def item_category_delete(
    self, info: strawberry.types.Info, category: ItemCategoryDeleteGQLModel
) -> typing.Optional[DeleteError[ItemCategoryGQLModel]]:
    return await Delete[ItemCategoryGQLModel].DoItSafeWay(info=info, entity=category)
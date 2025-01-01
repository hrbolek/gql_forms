import strawberry
import datetime
import typing
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

PartGQLModel = Annotated["PartGQLModel", strawberry.lazy(".PartGQLModel")]
ItemTypeGQLModel = Annotated["ItemTypeGQLModel", strawberry.lazy(".ItemTypeGQLModel")]

@strawberry.input
class ItemUpdateGQLModel:
    lastchange: datetime.datetime
    name: typing.Optional[str] = None
    order: typing.Optional[int] = None
    value: typing.Optional[str] = None
    type_id: typing.Optional[uuid.UUID] = None

@strawberry.federation.type(
    keys=["id"], 
    name="FormItemGQLModel",
    description="""Type representing an item in the form"""
)
class ItemGQLModel(BaseGQLModel):
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).formitems
    
    # @classmethod
    # async def resolve_reference(cls, info: strawberry.types.Info, id: uuid.UUID):
    # implementation is inherited
    name: typing.Optional[str] = strawberry.field(
        description="Name of the item",
        permission_classes=[OnlyForAuthentized]
    )
    name_en: typing.Optional[str] = strawberry.field(
        description="English name of the item",
        permission_classes=[OnlyForAuthentized]
    )
    order: typing.Optional[int] = strawberry.field(
        description="Order of the item in the parent entity",
        permission_classes=[OnlyForAuthentized]
    )
    value: typing.Optional[str] = strawberry.field(
        description="Value associated with the item",
        permission_classes=[OnlyForAuthentized]
    )
    part_id: typing.Optional[IDType] = strawberry.field(
        description="Foreign key to the form part",
        permission_classes=[OnlyForAuthentized]
    )
    type_id: typing.Optional[IDType] = strawberry.field(
        description="Foreign key to the item type",
        permission_classes=[OnlyForAuthentized]
    )
    state_id: typing.Optional[IDType] = strawberry.field(
        description="State of the item",
        permission_classes=[OnlyForAuthentized]
    )
    part: typing.Optional[PartGQLModel] = strawberry.field(
        description="The parent form part of this item",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["PartGQLModel"](fkey_field_name="part_id")
    )
    type: typing.Optional[ItemTypeGQLModel] = strawberry.field(
        description="The type of this item",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["ItemTypeGQLModel"](fkey_field_name="type_id")
    )

#############################################################
#
# Queries
#
#############################################################

@strawberry.field(
    description="Retrieves the item type",
    permission_classes=[OnlyForAuthentized])
async def item_by_id(
    self, info: strawberry.types.Info, id: uuid.UUID
) -> typing.Optional[ItemGQLModel]:
    result = await ItemGQLModel.resolve_reference(info=info, id=id)
    return result

from dataclasses import dataclass
from uoishelpers.resolvers import createInputs

@createInputs
@dataclass
class FormItemWhereFilter:
    name: str
    name_en: str
    type_id: uuid.UUID
    part_id: uuid.UUID
    # value: str # potencialni unik informaci pomoci where: { value: {_eq: ""}}

@strawberry.field(
    description="Retrieves the item type",
    permission_classes=[OnlyForAuthentized])
async def item_page(
    self, info: strawberry.types.Info, skip: int = 0, limit: int = 0,
    where: typing.Optional[FormItemWhereFilter] = None
) -> typing.List[ItemGQLModel]:
    loader = getLoadersFromInfo(info).items
    wf = None if where is None else strawberry.asdict(where)
    result = await loader.page(skip, limit, where = wf)
    return result
#############################################################
#
# Mutations
#
#############################################################

@strawberry.input(description="Input structure - C operation")
class FormItemInsertGQLModel:
    name: str = strawberry.field(description="Item name")
    part_id: uuid.UUID = strawberry.field(description="id of parent entity")

    name_en: typing.Optional[str] = strawberry.field(description="Item name", default=None)
    id: typing.Optional[uuid.UUID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    value: typing.Optional[str] = None
    order: typing.Optional[int] = strawberry.field(description="Position in parent entity", default=None)
    type_id: typing.Optional[uuid.UUID] = None
    createdby: strawberry.Private[uuid.UUID] = None 
    rbacobject: strawberry.Private[uuid.UUID] = None 
    

@strawberry.input(description="Input structure - U operation")
class FormItemUpdateGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")

    name: typing.Optional[str] = strawberry.field(description="Item name", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="Item name", default=None)
    value: typing.Optional[str] = None
    order: typing.Optional[int] = strawberry.field(description="Position in parent entity", default=None)
    type_id: typing.Optional[uuid.UUID] = None
    changedby: strawberry.Private[uuid.UUID] = None
    
@strawberry.input(description="Attributes for creating a new item")
class ItemInsertGQLModel:
    part_id: IDType = strawberry.field(description="ID of the form part")
    type_id: IDType = strawberry.field(description="ID of the item type")
    state_id: IDType = strawberry.field(description="ID of the item state")
    id: typing.Optional[IDType] = strawberry.field(
        description="Client-generated ID for the item (optional)", default=None
    )
    rbacobject_id: typing.Optional[IDType] = strawberry.field(
        description=":)", default=None
    )
    name: typing.Optional[str] = strawberry.field(description="Name of the item", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="English name of the item", default=None)
    order: typing.Optional[int] = strawberry.field(description="Order of the item", default=None)
    value: typing.Optional[str] = strawberry.field(description="Value of the item", default=None)
    createdby_id: strawberry.Private[uuid.UUID] = None 

@strawberry.input(description="Attributes for updating an existing item")
class ItemUpdateGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the item to update")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )
    name: typing.Optional[str] = strawberry.field(description="Updated name of the item", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="Updated English name of the item", default=None)
    order: typing.Optional[int] = strawberry.field(description="Updated order of the item", default=None)
    value: typing.Optional[str] = strawberry.field(description="Updated value of the item", default=None)
    changedby_id: strawberry.Private[uuid.UUID] = None

@strawberry.input(description="Attributes for deleting an existing item")
class ItemDeleteGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the item to delete")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )

async def item_insert_internal(
    self, info: strawberry.types.Info, item: ItemInsertGQLModel
) -> typing.Union[ItemGQLModel, InsertError[ItemGQLModel]]:
    return await Insert[ItemGQLModel].DoItSafeWay(info=info, entity=item)

@strawberry.mutation(
    description="Create a new item",
    permission_classes=[
        OnlyForAuthentized,
        SimpleInsertPermission[ItemGQLModel](roles=["administrátor"]),
    ],
)
async def item_insert(
    self, info: strawberry.types.Info, item: ItemInsertGQLModel
) -> typing.Union[ItemGQLModel, InsertError[ItemGQLModel]]:
    return await item_insert_internal(self=self, info=info, item=item)

@strawberry.mutation(
    description="Update an existing item",
    permission_classes=[
        OnlyForAuthentized,
        SimpleUpdatePermission[ItemGQLModel](roles=["administrátor"]),
    ],
)
async def item_update(
    self, info: strawberry.types.Info, item: ItemUpdateGQLModel
) -> typing.Union[ItemGQLModel, UpdateError[ItemGQLModel]]:
    return await Update[ItemGQLModel].DoItSafeWay(info=info, entity=item)

@strawberry.mutation(
    description="Delete an existing item",
    permission_classes=[
        OnlyForAuthentized,
        SimpleDeletePermission[ItemGQLModel](roles=["administrátor"]),
    ],
)
async def item_delete(
    self, info: strawberry.types.Info, item: ItemDeleteGQLModel
) -> typing.Optional[DeleteError[ItemGQLModel]]:
    return await Delete[ItemGQLModel].DoItSafeWay(info=info, entity=item)
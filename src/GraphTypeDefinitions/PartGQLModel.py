import dataclasses
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
    createInputs,
    VectorResolver,
    ScalarResolver,
    PageResolver,
    Insert, InsertError,
    Update, UpdateError,
    Delete, DeleteError
)
from .BaseGQLModel import BaseGQLModel, IDType

SectionGQLModel = Annotated["SectionGQLModel", strawberry.lazy(".SectionGQLModel")]
ItemGQLModel = Annotated["ItemGQLModel", strawberry.lazy(".ItemGQLModel")]

@strawberry.federation.type(
    keys=["id"], description="Entity representing a part of a form"
)
class PartGQLModel(BaseGQLModel):
    """
    GraphQL model for the Part entity.
    Represents a part of a form, including metadata and relationships.
    """
    @classmethod
    def getLoader(cls, info):
        return getLoadersFromInfo(info).formparts
    
    name: typing.Optional[str] = strawberry.field(
        description="Name of the part",
        permission_classes=[OnlyForAuthentized]
    )
    name_en: typing.Optional[str] = strawberry.field(
        description="English name of the part",
        permission_classes=[OnlyForAuthentized]
    )
    order: typing.Optional[int] = strawberry.field(
        description="Order of the part in the parent entity",
        permission_classes=[OnlyForAuthentized]
    )
    section_id: typing.Optional[IDType] = strawberry.field(
        description="Foreign key to the form section",
        permission_classes=[OnlyForAuthentized]
    )
    state_id: typing.Optional[IDType] = strawberry.field(
        description="State of the request",
        permission_classes=[OnlyForAuthentized]
    )
    section: typing.Optional[SectionGQLModel] = strawberry.field(
        description="The section this part belongs to",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["SectionGQLModel"](fkey_field_name="section_id")
    )

    @strawberry.field(
        description="Retrieves the items related to this part",
        permission_classes=[OnlyForAuthentized])
    async def items(self, info: strawberry.types.Info) -> typing.List["ItemGQLModel"]:
        from .ItemGQLModel import ItemGQLModel
        loader = ItemGQLModel.getLoader(info)
        results = await loader.filter_by(part_id=self.id)
        return (ItemGQLModel.from_dataclass(result) for result in results)

@createInputs
@dataclasses.dataclass
class PartInputFilter:
    """
    Input filter for querying form parts.
    Allows filtering by various fields of the form parts.
    """

    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        return getLoadersFromInfo(info=info).formparts    
    

    name: str = strawberry.field(
        description="Filter by the name of the form part"
    )
    name_en: str = strawberry.field(
        description="Filter by the English name of the form part"
    )
    section_id: IDType = strawberry.field(
        description="Filter by the form section ID"
    )
    state_id: IDType = strawberry.field(
        description="Filter by the state ID"
    )

#############################################################
#
# Queries
#
#############################################################
# @strawberry.field(description="")
# async def form_part_by_id(self, info: strawberry, id: strawberry.uuid) -> "PartGQLModel":
#     loader = getLoadersFromInfo(info).parts
#     result = await loader.load(id)
#     return result

@strawberry.field(
    description="returns part of section by its id",
    permission_classes=[OnlyForAuthentized])
async def form_part_by_id(self, info: strawberry.types.Info, id: uuid.UUID) -> typing.Optional[PartGQLModel]:
    return await PartGQLModel.resolve_reference(info=info, id=id)
#############################################################
#
# Mutations
#
#############################################################

@strawberry.input(description="Input structure - C operation")
class FormPartInsertGQLModel:
    name: str = strawberry.field(description="Part name")
    section_id: uuid.UUID
    name_en: typing.Optional[str] = strawberry.field(description="English part name", default=None)
    id: typing.Optional[uuid.UUID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    order: typing.Optional[int] = strawberry.field(description="Position in parent entity", default=None)
    createdby: strawberry.Private[uuid.UUID] = None 
    rbacobject: strawberry.Private[uuid.UUID] = None 

@strawberry.input(description="Input structure - U operation")
class FormPartUpdateGQLModel:
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    section_id: typing.Optional[uuid.UUID] = strawberry.field(description="id of parent entity", default=None)
    name: typing.Optional[str] = strawberry.field(description="Part name", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="English part name", default=None)
    order: typing.Optional[int] = strawberry.field(description="Position in parent entity", default=None)
    changedby: strawberry.Private[uuid.UUID] = None


@strawberry.input(description="Attributes for creating a new form part")
class PartInsertGQLModel:
    id: typing.Optional[IDType] = strawberry.field(
        description="Client-generated ID for the part (optional)", default=None
    )
    name: typing.Optional[str] = strawberry.field(description="Name of the part", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="English name of the part", default=None)
    order: typing.Optional[int] = strawberry.field(description="Order of the part", default=None)
    section_id: typing.Optional[IDType] = strawberry.field(description="ID of the form section", default=None)
    state_id: typing.Optional[IDType] = strawberry.field(description="ID of the state", default=None)
    createdby_id: strawberry.Private[uuid.UUID] = None 
    rbacobject: strawberry.Private[uuid.UUID] = None 

@strawberry.input(description="Attributes for updating an existing form part")
class PartUpdateGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the part to update")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )
    name: typing.Optional[str] = strawberry.field(description="Updated name of the part", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="Updated English name of the part", default=None)
    order: typing.Optional[int] = strawberry.field(description="Updated order of the part", default=None)
    section_id: typing.Optional[IDType] = strawberry.field(description="Updated form section ID", default=None)
    state_id: typing.Optional[IDType] = strawberry.field(description="Updated state ID", default=None)
    changedby_id: strawberry.Private[uuid.UUID] = None

@strawberry.input(description="Attributes for deleting an existing form part")
class PartDeleteGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the part to delete")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )

@strawberry.mutation(
    description="Create a new form part",
    permission_classes=[
        OnlyForAuthentized,
        SimpleInsertPermission[PartGQLModel](roles=["administrator"]),
    ],
)
async def part_insert(
    self, info: strawberry.types.Info, part: PartInsertGQLModel
) -> typing.Union[PartGQLModel, InsertError[PartGQLModel]]:
    return await Insert[PartGQLModel].DoItSafeWay(info=info, entity=part)

@strawberry.mutation(
    description="Update an existing form part",
    permission_classes=[
        OnlyForAuthentized,
        SimpleUpdatePermission[PartGQLModel](roles=["administrator"]),
    ],
)
async def part_update(
    self, info: strawberry.types.Info, part: PartUpdateGQLModel
) -> typing.Union[PartGQLModel, UpdateError[PartGQLModel]]:
    return await Update[PartGQLModel].DoItSafeWay(info=info, entity=part)

@strawberry.mutation(
    description="Delete an existing form part",
    permission_classes=[
        OnlyForAuthentized,
        SimpleDeletePermission[PartGQLModel](roles=["administrator"]),
    ],
)
async def part_delete(
    self, info: strawberry.types.Info, part: PartDeleteGQLModel
) -> typing.Optional[DeleteError[PartGQLModel]]:
    return await Delete[PartGQLModel].DoItSafeWay(info=info, entity=part)

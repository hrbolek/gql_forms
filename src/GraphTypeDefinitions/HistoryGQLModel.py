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
    PageResolver,
    ScalarResolver,
    Insert, InsertError,
    Update, UpdateError,
    Delete, DeleteError
)
from .BaseGQLModel import BaseGQLModel, IDType

FormGQLModel = Annotated["FormGQLModel", strawberry.lazy(".FormGQLModel")]
RequestGQLModel = Annotated["RequestGQLModel", strawberry.lazy(".RequestGQLModel")]
StateGQLModel = Annotated["StateGQLModel", strawberry.lazy(".externals")]

@strawberry.federation.type(
    keys=["id"], description="Entity representing a history record for forms"
)
class HistoryGQLModel(BaseGQLModel):
    """
    GraphQL model for the History entity.
    Tracks changes and historical states for forms and requests.
    """

    name: typing.Optional[str] = strawberry.field(
        description="A notice describing the reason",
        permission_classes=[OnlyForAuthentized]
    )
    name_en: typing.Optional[str] = strawberry.field(
        description="English description of the reason",
        permission_classes=[OnlyForAuthentized]
    )
    request_id: typing.Optional[IDType] = strawberry.field(
        description="Foreign key to form requests",
        permission_classes=[OnlyForAuthentized]
    )
    form_id: typing.Optional[IDType] = strawberry.field(
        description="Foreign key to forms",
        permission_classes=[OnlyForAuthentized]
    )
    state_id: typing.Optional[IDType] = strawberry.field(
        description="State of the request",
        permission_classes=[OnlyForAuthentized]
    )
    request: typing.Optional[FormRequestGQLModel] = strawberry.field(
        description="The associated form request",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["FormRequestGQLModel"](fkey_field_name="request_id")
    )
    form: typing.Optional[FormGQLModel] = strawberry.field(
        description="The associated form",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["FormGQLModel"](fkey_field_name="form_id")
    )
    
    @strawberry.field(
        description="State od the form",
        permission_classes=[OnlyForAuthentized])
    async def state(self, info: strawberry.types.Info) -> typing.Optional["StateGQLModel"]:
        #user = UserGQLModel(id=self.createdby)
        from .externals import StateGQLModel
        return await StateGQLModel.resolve_reference(info=info, id=self.state_id)

#############################################################
#
# Queries
#
#############################################################
@strawberry.field(
    description="returns the history result by its id",
    permission_classes=[OnlyForAuthentized])
async def form_history_by_id(self, info: strawberry.types.Info, id: uuid.UUID) -> typing.Optional[HistoryGQLModel]:
    return await HistoryGQLModel.resolve_reference(info=info, id=id)

@createInputs
@dataclasses.dataclass
class HistoryInputFilter:
    """
    Input filter for querying history records.
    Allows filtering by various fields of the history records.
    """
    name: typing.Optional[str] = strawberry.field(
        description="Filter by the name of the history record"
    )
    name_en: typing.Optional[str] = strawberry.field(
        description="Filter by the English name of the history record"
    )
    request_id: typing.Optional[IDType] = strawberry.field(
        description="Filter by the ID of the associated form request"
    )
    form_id: typing.Optional[IDType] = strawberry.field(
        description="Filter by the ID of the associated form"
    )
    state_id: typing.Optional[IDType] = strawberry.field(
        description="Filter by the state ID"
    )
    valid: typing.Optional[bool] = strawberry.field(
        description="Filter by the validity status of the history record"
    )


history_page = strawberry.field(
    description="Retrieve a paginated list of history records",
    permission_classes=[OnlyForAuthentized],
    graphql_type=typing.List[HistoryGQLModel],
    resolver=PageResolver[HistoryGQLModel](whereType=HistoryInputFilter)
)

#############################################################
#
# Mutations
#
#############################################################


@strawberry.input(description="Input structure - C operation")
class HistoryInsertGQLModel:
    name: str = strawberry.field(description="history name")
    request_id: uuid.UUID = strawberry.field(description="id of request")
    form_id: uuid.UUID = strawberry.field(description="id of form")

    id: typing.Optional[uuid.UUID] = strawberry.field(description="primary key (UUID), could be client generated", default=None)
    createdby: strawberry.Private[uuid.UUID] = None    

@strawberry.input(description="Input structure - U operation")
class HistoryUpdateGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")

    name: typing.Optional[str] = strawberry.field(description="history name", default=None)
    changedby: strawberry.Private[uuid.UUID] = None


@strawberry.input(description="Attributes for creating a new history record")
class HistoryInsertGQLModel:
    request_id: IDType = strawberry.field(description="ID of the associated form request")
    form_id: IDType = strawberry.field(description="ID of the associated form")
    state_id: IDType = strawberry.field(description="ID of the state")

    id: typing.Optional[IDType] = strawberry.field(
        description="Client-generated ID for the history record (optional)", default=None
    )
    name: typing.Optional[str] = strawberry.field(description="A notice describing the reason", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="English description of the reason", default=None)
    createdby_id: strawberry.Private[uuid.UUID] = None    

@strawberry.input(description="Attributes for updating an existing history record")
class HistoryUpdateGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the history record to update")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )
    name: typing.Optional[str] = strawberry.field(description="Updated notice describing the reason", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="Updated English description of the reason", default=None)
    changedby_id: strawberry.Private[uuid.UUID] = None

@strawberry.input(description="Attributes for deleting an existing history record")
class HistoryDeleteGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the history record to delete")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )

@strawberry.mutation(
    description="Create a new history record",
    permission_classes=[
        OnlyForAuthentized,
        SimpleInsertPermission[HistoryGQLModel](roles=["administrátor"]),
    ],
)
async def history_insert(
    self, info: strawberry.types.Info, history: HistoryInsertGQLModel
) -> typing.Union[HistoryGQLModel, InsertError[HistoryGQLModel]]:
    return await Insert[HistoryGQLModel].DoItSafeWay(info=info, entity=history)

@strawberry.mutation(
    description="Update an existing history record",
    permission_classes=[
        OnlyForAuthentized,
        SimpleUpdatePermission[HistoryGQLModel](roles=["administrátor"]),
    ],
)
async def history_update(
    self, info: strawberry.types.Info, history: HistoryUpdateGQLModel
) -> typing.Union[HistoryGQLModel, UpdateError[HistoryGQLModel]]:
    return await Update[HistoryGQLModel].DoItSafeWay(info=info, entity=history)

@strawberry.mutation(
    description="Delete an existing history record",
    permission_classes=[
        OnlyForAuthentized,
        SimpleDeletePermission[HistoryGQLModel](roles=["administrátor"]),
    ],
)
async def history_delete(
    self, info: strawberry.types.Info, history: HistoryDeleteGQLModel
) -> typing.Optional[DeleteError[HistoryGQLModel]]:
    return await Delete[HistoryGQLModel].DoItSafeWay(info=info, entity=history)
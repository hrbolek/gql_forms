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

RequestCategoryGQLModel = Annotated["RequestCategoryGQLModel", strawberry.lazy(".RequestCategoryGQLModel")]
RequestGQLModel = Annotated["RequestGQLModel", strawberry.lazy(".RequestGQLModel")]
FormGQLModel = Annotated["FormGQLModel", strawberry.lazy(".FormGQLModel")]
GroupGQLModel = Annotated["GroupGQLModel", strawberry.lazy(".GroupGQLModel")]
StateGQLModel = Annotated["StateGQLModel", strawberry.lazy(".StateGQLModel")]
StateMachineGQLModel = Annotated["StateMachineGQLModel", strawberry.lazy(".StateMachineGQLModel")]
@strawberry.federation.type(
    keys=["id"], description="Entity representing a request type"
)
class RequestTypeGQLModel(BaseGQLModel):
    """
    GraphQL model for the RequestType entity.
    Represents different types of requests with metadata such as name and category.
    """
    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        return getLoadersFromInfo(info=info).formrequesttypes

    name: typing.Optional[str] = strawberry.field(
        description="Name of the request type",
        permission_classes=[OnlyForAuthentized]
    )
    name_en: typing.Optional[str] = strawberry.field(
        description="English name of the request type",
        permission_classes=[OnlyForAuthentized]
    )
    category_id: typing.Optional[IDType] = strawberry.field(
        description="Foreign key to the request category",
        permission_classes=[OnlyForAuthentized]
    )
    template_form_id: typing.Optional[IDType] = strawberry.field(
        description="Foreign key to the form which is a template",
        permission_classes=[OnlyForAuthentized]
    )
    group_id: typing.Optional[IDType] = strawberry.field(
        description="Group members can create new request",
        permission_classes=[OnlyForAuthentized]
    )
    state_id: typing.Optional[IDType] = strawberry.field(
        description="First state of the request",
        permission_classes=[OnlyForAuthentized]
    )
    statemachine_id: typing.Optional[IDType] = strawberry.field(
        description="Set of states related to the request",
        permission_classes=[OnlyForAuthentized]
    )

    category: typing.Optional[RequestCategoryGQLModel] = strawberry.field(
        description="The category this request type belongs to",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["RequestCategoryGQLModel"](fkey_field_name="category_id")
    )
    template_form: typing.Optional[FormGQLModel] = strawberry.field(
        description="The form which will be copied as initial form for the request",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["FormGQLModel"](fkey_field_name="template_form_id")
    )
    
    @strawberry.field(
        description="",
        permission_classes=[OnlyForAuthentized])
    async def requests(self, info: strawberry.types.Info) -> typing.List["RequestGQLModel"]:
        loader = getLoadersFromInfo(info).requests
        rows = await loader.filter_by(type_id=self.id)
        return rows
    
    @strawberry.field(
        description="Who can create a request",
        permission_classes=[OnlyForAuthentized]
    )
    async def group(self, info: strawberry.types.Info) -> typing.Optional["GroupGQLModel"]:
        from .GroupGQLModel import GroupGQLModel
        result = await GroupGQLModel.resolve_reference(info=info, id=self.group_id)
        return result
    
    @strawberry.field(
        description="First state where new request will begin",
        permission_classes=[OnlyForAuthentized]
    )
    async def state(self, info: strawberry.types.Info) -> typing.Optional["StateGQLModel"]:
        from .StateGQLModel import StateGQLModel
        result = await StateGQLModel.resolve_reference(info=info, id=self.group_id)
        return result    
    
    @strawberry.field(
        description="First state where new request will begin",
        permission_classes=[OnlyForAuthentized]
    )
    async def statemachine(self, info: strawberry.types.Info) -> typing.Optional["StateMachineGQLModel"]:
        from .StateMachineGQLModel import StateMachineGQLModel
        result = await StateMachineGQLModel.resolve_reference(info=info, id=self.statemachine_id)
        return result        
#############################################################
#
# Queries
#
#############################################################

@strawberry.field(
    description="Retrieves the request type",
    permission_classes=[OnlyForAuthentized])
async def request_type_by_id(
    self, info: strawberry.types.Info, id: uuid.UUID
) -> typing.Optional[RequestTypeGQLModel]:
    result = await RequestTypeGQLModel.resolve_reference(info=info, id=id)
    return result

from dataclasses import dataclass
from uoishelpers.resolvers import createInputs

# RequestWhereFilter = Annotated["RequestWhereFilter", strawberry.lazy(".RequestGQLModel")]
@createInputs
@dataclass
class RequestTypeInputFilter:
    name: str
    name_en: str
    id: IDType
    category_id: IDType
    # from .RequestGQLModel import RequestWhereFilter
    # requests: RequestWhereFilter

request_type_page = strawberry.field(
    description="Retrieves the request type",
    permission_classes=[OnlyForAuthentized],
    graphql_type=typing.List[RequestTypeGQLModel],
    resolver=PageResolver[RequestTypeGQLModel](whereType=RequestTypeInputFilter)
    )
#############################################################
#
# Mutations
#
#############################################################

@strawberry.input(description="Attributes for creating a new request type")
class RequestTypeInsertGQLModel:
    category_id: IDType = strawberry.field(description="ID of the request category")    
    id: typing.Optional[IDType] = strawberry.field(
        description="Client-generated ID for the request type (optional)", default=None
    )
    group_id: typing.Optional[IDType] = strawberry.field(
        description="members of this group will be able to create new request", default=None
    )
    statemachine_id: typing.Optional[IDType] = strawberry.field(
        description="set of states related to the request", default=None
    )
    state_id: typing.Optional[IDType] = strawberry.field(
        description="first state of new request", default=None
    )
    # template_form_id: typing.Optional[IDType] = strawberry.field(
    #     description="id of form", default=None
    # )
    from .FormGQLModel import FormInsertGQLModel
    template_form: typing.Optional[FormInsertGQLModel] = strawberry.field(description="template form for the request type", default=None)
    name: typing.Optional[str] = strawberry.field(description="Name of the request type", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="English name of the request type", default=None)
    createdby_id: strawberry.Private[uuid.UUID] = None 

@strawberry.input(description="Attributes for updating an existing request type")
class RequestTypeUpdateGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the request type to update")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )
    name: typing.Optional[str] = strawberry.field(description="Updated name of the request type", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="Updated English name of the request type", default=None)
    group_id: typing.Optional[IDType] = strawberry.field(
        description="members of this group will be able to create new request", default=None
    )
    statemachine_id: typing.Optional[IDType] = strawberry.field(
        description="set of states related to the request", default=None
    )
    template_form_id: typing.Optional[IDType] = strawberry.field(
        description="template form for the request type", default=None)
    changedby_id: strawberry.Private[uuid.UUID] = None

@strawberry.input(description="Attributes for deleting an existing request type")
class RequestTypeDeleteGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the request type to delete")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )

@strawberry.mutation(
    description="Create a new request type",
    permission_classes=[
        OnlyForAuthentized,
        SimpleInsertPermission[RequestTypeGQLModel](roles=["administrátor"]),
    ],
)
async def request_type_insert(
    self, info: strawberry.types.Info, request_type: RequestTypeInsertGQLModel
) -> typing.Union[RequestTypeGQLModel, InsertError[RequestTypeGQLModel]]:
    from .FormGQLModel import form_insert_internal
    if request_type.template_form:
        result = form_insert_internal(self=self, info=info, form=request_type.template_form)
        if getattr(result, "failed", False):
            # print(f"failed request_type_insert {result}")
            msg = result.msg
            return InsertError[RequestTypeGQLModel](msg=msg, _input=request_type)
    return await Insert[RequestTypeGQLModel].DoItSafeWay(info=info, entity=request_type)

@strawberry.mutation(
    description="Update an existing request type",
    permission_classes=[
        OnlyForAuthentized,
        SimpleUpdatePermission[RequestTypeGQLModel](roles=["administrátor"]),
    ],
)
async def request_type_update(
    self, info: strawberry.types.Info, request_type: RequestTypeUpdateGQLModel
) -> typing.Union[RequestTypeGQLModel, UpdateError[RequestTypeGQLModel]]:
    return await Update[RequestTypeGQLModel].DoItSafeWay(info=info, entity=request_type)

@strawberry.mutation(
    description="Delete an existing request type",
    permission_classes=[
        OnlyForAuthentized,
        SimpleDeletePermission[RequestTypeGQLModel](roles=["administrátor"]),
    ],
)
async def request_type_delete(
    self, info: strawberry.types.Info, request_type: RequestTypeDeleteGQLModel
) -> typing.Optional[DeleteError[RequestTypeGQLModel]]:
    return await Delete[RequestTypeGQLModel].DoItSafeWay(info=info, entity=request_type)
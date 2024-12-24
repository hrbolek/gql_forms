import strawberry
import datetime
import typing
import uuid
import asyncio
import logging

from typing import Annotated

from uoishelpers.gqlpermissions import (
    OnlyForAuthentized, 
    SimpleInsertPermission,
    SimpleUpdatePermission,
    SimpleDeletePermission
)

from uoishelpers.resolvers import (
    getLoadersFromInfo,
    getUserFromInfo,
    createInputs,
    VectorResolver,
    ScalarResolver,
    PageResolver,
    Insert, InsertError,
    Update, UpdateError,
    Delete, DeleteError
)
from .BaseGQLModel import BaseGQLModel, IDType

UserGQLModel = Annotated["UserGQLModel", strawberry.lazy(".userGQLModel")]
HistoryGQLModel = Annotated["HistoryGQLModel", strawberry.lazy(".HistoryGQLModel")]
StateGQLModel = Annotated["StateGQLModel", strawberry.lazy(".StateGQLModel")]
FormGQLModel = Annotated["FormGQLModel", strawberry.lazy(".FormGQLModel")]

# define the type help to get attribute name and name
@strawberry.federation.type(
    keys=["id"], description="Entity representing a form request"
)
class RequestGQLModel(BaseGQLModel):
    """
    GraphQL model for the Request entity.
    Represents form requests, including their associated form and histories.
    """
    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        return getLoadersFromInfo(info=info).formrequests

    name: typing.Optional[str] = strawberry.field(
        description="Name of the request",
        permission_classes=[OnlyForAuthentized]
    )
    name_en: typing.Optional[str] = strawberry.field(
        description="English name of the request",
        permission_classes=[OnlyForAuthentized]
    )
    form_id: typing.Optional[IDType] = strawberry.field(
        description="Foreign key to the associated form",
        permission_classes=[OnlyForAuthentized]
    )
    state_id: typing.Optional[IDType] = strawberry.field(
        description="State of the request",
        permission_classes=[OnlyForAuthentized]
    )
    form: typing.Optional[FormGQLModel] = strawberry.field(
        description="The associated form for this request",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["FormGQLModel"](fkey_field_name="form_id")
    )
    state: typing.Optional[StateGQLModel] = strawberry.field(
        description="The state of the request",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["StateGQLModel"](fkey_field_name="state_id")
    )

    from .HistoryGQLModel import HistoryInputFilter
    histories: typing.List[HistoryGQLModel] = strawberry.field(
        description="Histories linked to this request",
        permission_classes=[OnlyForAuthentized],
        resolver=VectorResolver["HistoryGQLModel"](whereType=HistoryInputFilter, fkey_field_name="request_id")
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
class RequestWhereFilter:
    name: str
    name_en: str
    createdby: uuid.UUID
    state_id: uuid.UUID

@strawberry.field(
    description="""Finds an request by their id""",
    permission_classes=[OnlyForAuthentized])
async def request_by_id(
    self, info: strawberry.types.Info, id: uuid.UUID
) -> typing.Optional[RequestGQLModel]:
    result = await RequestGQLModel.resolve_reference(info, id)
    return result

# requests_page = createRootResolver_by_page(
#     scalarType=RequestGQLModel,
#     whereFilterType=RequestWhereFilter,
#     description="Retrieves all requests",
#     loaderLambda=lambda info: getLoadersFromInfo(info).requests,
#     skip=0,
#     limit=10
#     )
from src.DBResolvers import RequestResolvers
# from ._GraphResolvers import asPage

# @strawberry.field(
#     description="Retrieves all requests",
#     permission_classes=[OnlyForAuthentized])
# @asPage
# #async def request_page(self, info: strawberry.types.Info, where: typing.Optional[RequestWhereFilter] = None) -> typing.List[RequestGQLModel]:
# async def request_page(self, info: strawberry.types.Info, where: typing.Optional[RequestWhereFilter]) -> typing.List[RequestGQLModel]:
#     logging.info("returning just loader")
#     return getLoadersFromInfo(info).requests

request_page = strawberry.field(
    description="Retrieves all requests",
    permission_classes=[OnlyForAuthentized],
    resolver=RequestResolvers.Page(GQLModel=RequestGQLModel, WhereFilterModel=RequestWhereFilter)
)
#############################################################
#
# Mutations
#
#############################################################

@strawberry.input(description="Attributes for creating a new form request")
class RequestInsertGQLModel:
    id: typing.Optional[IDType] = strawberry.field(
        description="Client-generated ID for the request (optional)", default=None
    )
    name: typing.Optional[str] = strawberry.field(description="Name of the request", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="English name of the request", default=None)
    form_id: typing.Optional[IDType] = strawberry.field(description="ID of the associated form", default=None)
    state_id: typing.Optional[IDType] = strawberry.field(description="ID of the state", default=None)
    createdby_id: strawberry.Private[IDType] = None 
    rbacobject_id: strawberry.Private[IDType] = None

@strawberry.input(description="Attributes for updating an existing form request")
class RequestUpdateGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the request to update")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )
    name: typing.Optional[str] = strawberry.field(description="Updated name of the request", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="Updated English name of the request", default=None)
    form_id: typing.Optional[IDType] = strawberry.field(description="Updated form ID", default=None)
    state_id: typing.Optional[IDType] = strawberry.field(description="Updated state ID", default=None)
    changedby: strawberry.Private[IDType] = None


@strawberry.input(description="Attributes for deleting an existing form request")
class RequestDeleteGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the request to delete")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )

@strawberry.mutation(
    description="Create a new form request",
    permission_classes=[
        OnlyForAuthentized,
        SimpleInsertPermission[RequestGQLModel](roles=["administrator"]),
    ],
)
async def request_insert(
    self, info: strawberry.types.Info, request: RequestInsertGQLModel
) -> typing.Union[RequestGQLModel, InsertError[RequestGQLModel]]:
    return await Insert[RequestGQLModel].DoItSafeWay(info=info, entity=request)

@strawberry.mutation(
    description="Update an existing form request",
    permission_classes=[
        OnlyForAuthentized,
        SimpleUpdatePermission[RequestGQLModel](roles=["administrator"]),
    ],
)
async def request_update(
    self, info: strawberry.types.Info, request: RequestUpdateGQLModel
) -> typing.Union[RequestGQLModel, UpdateError[RequestGQLModel]]:
    return await Update[RequestGQLModel].DoItSafeWay(info=info, entity=request)

@strawberry.mutation(
    description="Delete an existing form request",
    permission_classes=[
        OnlyForAuthentized,
        SimpleDeletePermission[RequestGQLModel](roles=["administrator"]),
    ],
)
async def request_delete(
    self, info: strawberry.types.Info, request: RequestDeleteGQLModel
) -> typing.Optional[DeleteError[RequestGQLModel]]:
    return await Delete[RequestGQLModel].DoItSafeWay(info=info, entity=request)

@strawberry.input(description="Input structure")
class FormRequestUseTransitionGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")
    transition_id: uuid.UUID = strawberry.field(description="transition used for this operation")
    history_message: str = strawberry.field(description="this will appear in history records")
    changedby: strawberry.Private[uuid.UUID] = None

async def CopyForm(info: strawberry.types.Info, request_id: uuid.UUID, source_form_id: uuid.UUID, copy_form_id: uuid.UUID, copy_state_id: uuid.UUID, copy_item_values=False):
    from .FormGQLModel import FormGQLModel
    formloader = FormGQLModel.getLoader(info=info)
    form_row = await formloader.load(source_form_id)
    assert form_row is not None, f"Form {source_form_id} has not been found"

    # copy_form = await formloader.insert(entity=form_row, extraAttributes={"id": copy_form_id, "state_id": target_id})
    copy_form = await formloader.insert(
        entity=None, 
        extraAttributes={
            "id": copy_form_id, 
            "state_id": copy_state_id,
            "request_id": request_id,
            "name": form_row.name,
            "rbacobject": form_row.rbacobject,
            "type_id": form_row.type_id
        })
    print(f"copy_form {copy_form.state_id} {copy_form}({copy_form.id} / {copy_form_id})")
    from .SectionGQLModel import SectionGQLModel
    section_loader = SectionGQLModel.getLoader(info=info)
    sections = await section_loader.filter_by(form_id=source_form_id)
    sections = list(sections)
    # print("sections", sections, flush=True)
    section_ids = list(map(lambda section: section.id, sections))
    # print("section_ids", section_ids, flush=True)
    # assert len(section_ids) !=0, f"form has no sections :("
    copy_sections = (section_loader.insert(
        # entity=section, 
        entity=None, 
        extraAttributes={
            "id": uuid.uuid1(), 
            "form_id": copy_form_id, 
            "state_id": copy_state_id,
            "rbacobject": section.rbacobject,
            "name": section.name,
            }) for section in sections)
    copy_sections = await asyncio.gather(*copy_sections)
    # print("copy_sections", copy_sections, flush=True)
    sections_map = {oldid: copy_section.id for copy_section, oldid in zip(copy_sections, section_ids)}
    # print("sections_map", sections_map, flush=True)

    from .PartGQLModel import PartGQLModel
    part_loader = PartGQLModel.getLoader(info=info)
    part_db_model = part_loader.getModel()
    
    parts_select_statement = part_loader.getSelectStatement()
    parts_select_statement = parts_select_statement.filter(part_db_model.section_id.in_(section_ids))
    parts = await part_loader.execute_select(parts_select_statement)
    parts = list(parts)
    part_ids = list(map(lambda part: part.id, parts))
    # print("part_ids", part_ids, flush=True)
    copy_parts = (part_loader.insert(
        # entity=part, 
        entity=None, 
        extraAttributes={
            "id": uuid.uuid1(), 
            "section_id": sections_map[part.section_id], 
            "state_id": copy_state_id,
            "rbacobject": part.rbacobject,
            "name": part.name,
            }) for part in parts)
    copy_parts = await asyncio.gather(*copy_parts)
    # print("copy_parts", copy_parts, flush=True)
    parts_map = {oldid: copy_part.id for copy_part, oldid in zip(copy_parts, part_ids)}
    # print("parts_map", parts_map, flush=True)
    # copy_part_ids = {id: uuid.uuid1() for id in part_ids}

    from .ItemGQLModel import ItemGQLModel
    item_loader = ItemGQLModel.getLoader(info=info)
    item_db_model = item_loader.getModel()
    items_select_statement = item_loader.getSelectStatement()
    items_select_statement = items_select_statement.filter(item_db_model.part_id.in_(part_ids))
    items = await item_loader.execute_select(items_select_statement)
    items = list(items)
    # item_ids = list(map(lambda item: item.id, items))
    copy_items = (item_loader.insert(
        # entity=item, 
        entity=None, 
        extraAttributes={
            "id": uuid.uuid1(), 
            "part_id": parts_map[item.part_id], 
            "state_id": copy_state_id,
            "rbacobject": item.rbacobject,
            "name": item.name,
            "value": item.value if copy_item_values else None,
            "type_id": item.type_id
            }) for item in items )
    copy_items = await asyncio.gather(*copy_items)    
    return copy_form


@strawberry.mutation(
    description="C operation",
    permission_classes=[OnlyForAuthentized])
async def form_request_insert(self, info: strawberry.types.Info, request: RequestInsertGQLModel) -> typing.Union[RequestGQLModel, InsertError[RequestGQLModel]]:
    user = getUserFromInfo(info)
    request.createdby = uuid.UUID(user["id"])
    request.rbacobject = uuid.UUID(user["id"])

    copy_form_id = uuid.uuid1()
    copy_form = await CopyForm(
        info=info,
        request_id=request.id,
        source_form_id=request.form_id,
        copy_form_id=copy_form_id,
        copy_state_id=request.state_id, # TODO change this better is to use StateMachine (first/input state)
        copy_item_values=False
        )
    request.form_id=copy_form_id
    loader = getLoadersFromInfo(info).requests
    row = await loader.insert(request)
    result = FormRequestResultGQLModel(id=row.id, msg="ok")
    result.msg = "ok"
    result.id = row.id
    return result

# from ._GraphPermissions import StateBasedPermissionForUDOps
# from strawberry.extensions import FieldExtension

# class TestExtension(FieldExtension):
#     async def resolve_async(
#         self, next: typing.Callable[..., typing.Any], source: typing.Any, info: strawberry.Info, **kwargs
#     ):
#         print("TestExtension", source, type(source), info, kwargs, flush=True)
#         result = await next(source, info, **kwargs)
#         print("TestExtension.result", result, flush=True)
#         return result

# @strawberry.field(
#     description="U operation",
#     extensions=[TestExtension()]
#     )
# async def form_test_extension(self, info: strawberry.types.Info, param: typing.Optional[str] = "default") -> typing.Optional[FormRequestResultGQLModel]:
#     print("form_test_extension", param, flush=True)
#     return None


@strawberry.mutation(
    description="U operation",
    permission_classes=[
        OnlyForAuthentized,
        # StateBasedPermissionForUDOps(GQLModel=RequestGQLModel, parameterName="request", readPermission=False, writePermission=True)
        ],
    )
async def form_request_use_transition(self, info: strawberry.types.Info, request: FormRequestUseTransitionGQLModel) -> typing.Union[RequestGQLModel, UpdateError[RequestGQLModel]]:
    # create copy of current form
    # make row in histories
    # change state of request
    from uoishelpers.gqlpermissions import RBACObjectGQLModel
    client = RBACObjectGQLModel.get_async_client(info=info)
    query = """query statetransitionById($id: UUID!) {
  result: statetransitionById(id: $id) {
    source { id }
    target { id }
  }
}"""

    variables = {
        "id": f"{request.transition_id}"
    }
    jsonResponse = await client(query=query, variables=variables)
    assert "errors" not in jsonResponse, f"got error {jsonResponse}"
    print(f"got jsonResponse from UG {jsonResponse}", flush=True)
    jsonResult = jsonResponse["data"]["result"]
    source_id = uuid.UUID(jsonResult["source"]["id"])
    target_id = uuid.UUID(jsonResult["target"]["id"])
    print(f"transition {jsonResult}", flush=True)
    user = getUserFromInfo(info)
    request.changedby = uuid.UUID(user["id"])

    # create copy of current form
    request_loader = RequestGQLModel.getLoader(info=info)
    request_row = await request_loader.load(request.id)
    assert request_row is not None, f"request.id {request.id} refers to unknown request"

    assert request_row.state_id == source_id, f"transition {request.transition_id} cannot be applied to state {request.state_id} see {request}"
    form_id = request_row.form_id

    # make row in histories
    from .HistoryGQLModel import HistoryGQLModel
    history_loader = HistoryGQLModel.getLoader(info=info)
    history_row = await history_loader.insert(
        None, 
        extraAttributes={
            "id": uuid.uuid1(), 
            "form_id": form_id, 
            "request_id": request.id,
            "state_id": target_id,
            "name": request.history_message
        }
    )
    # print("history name", request.history_message, flush=True)
    # create copy of current form
    from .FormGQLModel import FormGQLModel
    formloader = FormGQLModel.getLoader(info=info)
    form_row = await formloader.load(form_id)
    assert form_row is not None, f"Unexpected situation, form has not been found on request {request.id}"
    copy_form_id = uuid.uuid1()
    # form_row.history = history_row
    form_row.history = None
    form_row.history_id = history_row.id

    copy_form = await CopyForm(
        info=info, 
        request_id=request.id, 
        source_form_id=form_id, 
        copy_form_id=copy_form_id, 
        copy_state_id=target_id,
        copy_item_values=True
    )
    # copy_form = await formloader.insert(entity=form_row, extraAttributes={"id": copy_form_id, "state_id": target_id})
    # copy_form = await formloader.insert(
    #     entity=None, 
    #     extraAttributes={
    #         "id": copy_form_id, 
    #         "state_id": target_id,
    #         "request_id": request.id,
    #         "name": form_row.name,
    #         "rbacobject": form_row.rbacobject,
    #         "type_id": form_row.type_id
    #     })
    # print(f"copy_form {copy_form.state_id} {copy_form}({copy_form.id} / {copy_form_id})")
    # from .SectionGQLModel import SectionGQLModel
    # section_loader = SectionGQLModel.getLoader(info=info)
    # sections = await section_loader.filter_by(form_id=form_id)
    # sections = list(sections)
    # # print("sections", sections, flush=True)
    # section_ids = list(map(lambda section: section.id, sections))
    # # print("section_ids", section_ids, flush=True)
    # assert len(section_ids) !=0, f"request's {request.id} form has no sections :("
    # copy_sections = (section_loader.insert(
    #     # entity=section, 
    #     entity=None, 
    #     extraAttributes={
    #         "id": uuid.uuid1(), 
    #         "form_id": copy_form_id, 
    #         "state_id": target_id,
    #         "rbacobject": section.rbacobject,
    #         "name": section.name,
    #         }) for section in sections)
    # copy_sections = await asyncio.gather(*copy_sections)
    # # print("copy_sections", copy_sections, flush=True)
    # sections_map = {oldid: copy_section.id for copy_section, oldid in zip(copy_sections, section_ids)}
    # # print("sections_map", sections_map, flush=True)

    # from .PartGQLModel import PartGQLModel
    # part_loader = PartGQLModel.getLoader(info=info)
    # part_db_model = part_loader.getModel()
    
    # parts_select_statement = part_loader.getSelectStatement()
    # parts_select_statement = parts_select_statement.filter(part_db_model.section_id.in_(section_ids))
    # parts = await part_loader.execute_select(parts_select_statement)
    # parts = list(parts)
    # part_ids = list(map(lambda part: part.id, parts))
    # # print("part_ids", part_ids, flush=True)
    # copy_parts = (part_loader.insert(
    #     # entity=part, 
    #     entity=None, 
    #     extraAttributes={
    #         "id": uuid.uuid1(), 
    #         "section_id": sections_map[part.section_id], 
    #         "state_id": target_id,
    #         "rbacobject": part.rbacobject,
    #         "name": part.name,
    #         }) for part in parts)
    # copy_parts = await asyncio.gather(*copy_parts)
    # # print("copy_parts", copy_parts, flush=True)
    # parts_map = {oldid: copy_part.id for copy_part, oldid in zip(copy_parts, part_ids)}
    # # print("parts_map", parts_map, flush=True)
    # # copy_part_ids = {id: uuid.uuid1() for id in part_ids}

    # from .ItemGQLModel import ItemGQLModel
    # item_loader = ItemGQLModel.getLoader(info=info)
    # item_db_model = item_loader.getModel()
    # items_select_statement = item_loader.getSelectStatement()
    # items_select_statement = items_select_statement.filter(item_db_model.part_id.in_(part_ids))
    # items = await item_loader.execute_select(items_select_statement)
    # items = list(items)
    # # item_ids = list(map(lambda item: item.id, items))
    # copy_items = (item_loader.insert(
    #     # entity=item, 
    #     entity=None, 
    #     extraAttributes={
    #         "id": uuid.uuid1(), 
    #         "part_id": parts_map[item.part_id], 
    #         "state_id": target_id,
    #         "rbacobject": item.rbacobject,
    #         "name": item.name,
    #         "value": item.value,
    #         "type_id": item.type_id
    #         }) for item in items )
    # copy_items = await asyncio.gather(*copy_items)
    # # copy_item_ids = {id: uuid.uuid1() for id in item_ids}


    # change state of request
    requestAttributeValues={
        "id": request_row.id,
        "name": request_row.name,
        "rbacobject": request_row.rbacobject,
        "form_id": copy_form_id,
        "state_id": target_id,
        "lastchange": request_row.lastchange
    }
    dbmodel = request_loader.getModel()
    updated_request_row = await request_loader.update(
        # entity=request_row, 
        entity=dbmodel(**requestAttributeValues), 
    )

    result = FormRequestResultGQLModel(id=request.id, msg="ok")
    result.msg = "fail" if updated_request_row is None else "ok"
    result.id = request.id
    return result   



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
    PageResolver,
    ScalarResolver,
    Insert, InsertError,
    Update, UpdateError,
    Delete, DeleteError
)
from .BaseGQLModel import BaseGQLModel, IDType


SectionGQLModel = Annotated["SectionGQLModel", strawberry.lazy(".SectionGQLModel")]
FormTypeGQLModel = Annotated["FormTypeGQLModel", strawberry.lazy(".FormTypeGQLModel")]
UserGQLModel = Annotated["UserGQLModel", strawberry.lazy(".externals")]
StateGQLModel = Annotated["StateGQLModel", strawberry.lazy(".externals")]
RequestGQLModel = Annotated["RequestGQLModel", strawberry.lazy(".RequestGQLModel")]

FormGQLModelDescription = """
# Reason

Entity representing a form, form is digitalized A4 sheet

## Structure

form -> sections -> parts -> items
"""

@strawberry.federation.type(
    keys=["id"], description=FormGQLModelDescription
)
class FormGQLModel(BaseGQLModel):
    """
    Type representing a request in the system.
    This class extends the base `RequestModel` from the database and adds additional fields and methods needed for use in GraphQL.
    """
    @classmethod
    def getLoader(cls, info):
        loader = getLoadersFromInfo(info).forms
        # logging.info(f"FormGQLModel.getLoader => {loader}")
        return loader
    
    # @classmethod
    # async def resolve_reference(cls, info: strawberry.types.Info, id: uuid.UUID):
    # implementation is inherited
    name: typing.Optional[str] = strawberry.field(
        description="Name of the form",
        permission_classes=[OnlyForAuthentized]
    )
    name_en: typing.Optional[str] = strawberry.field(
        description="English name of the form",
        permission_classes=[OnlyForAuthentized]
    )
    status: typing.Optional[str] = strawberry.field(
        description="Status of the form",
        permission_classes=[OnlyForAuthentized]
    )
    valid: typing.Optional[bool] = strawberry.field(
        description="Indicates if the form is valid",
        permission_classes=[OnlyForAuthentized]
    )
    type_id: typing.Optional[IDType] = strawberry.field(
        description="Foreign key to the form type",
        permission_classes=[OnlyForAuthentized]
    )
    state_id: typing.Optional[IDType] = strawberry.field(
        description="Foreign key to the form state",
        permission_classes=[OnlyForAuthentized]
    )
    type: typing.Optional[FormTypeGQLModel] = strawberry.field(
        description="Type of the form",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["FormTypeGQLModel"](fkey_field_name="type_id")
    )

    # state: typing.Optional[FormStateGQLModel] = strawberry.field(
    #     description="State of the form",
    #     permission_classes=[OnlyForAuthentized],
    #     resolver=ScalarResolver["FormStateGQLModel"](fkey_field_name="state_id")
    # )

    @strawberry.field(
        description="Retrieves the sections related to this form (form has several sections), form->section->part->item",
        permission_classes=[OnlyForAuthentized],
        )
    async def sections(
        self, info: strawberry.types.Info,
    ) -> typing.List["SectionGQLModel"]:
        loader = getLoadersFromInfo(info).sections
        results = await loader.filter_by(form_id=self.id)
        return results

    @strawberry.field(
        description="Retrieves the type of form",
        permission_classes=[OnlyForAuthentized])
    async def request(self, info: strawberry.types.Info) -> typing.Optional["RequestGQLModel"]:
        from .HistoryGQLModel import HistoryGQLModel
        loader = HistoryGQLModel.getLoader(info)
        rows = await loader.filter_by(form_id=self.id)
        row = next(rows, None)

        from .RequestGQLModel import RequestGQLModel
        result =  await RequestGQLModel.resolve_reference(info, row.request_id)
        return None if row is None else result
    
#############################################################
#
# Queries
#
#############################################################
from ._GraphPermissions import OnlyForAuthentized
@strawberry.field(
    description="Retrieves the form type",
    permission_classes=[OnlyForAuthentized])
async def form_by_id(
    self, info: strawberry.types.Info, id: uuid.UUID
) -> typing.Optional[FormGQLModel]:
    # logging.info(f"form_by_id ({id})")
    result = await FormGQLModel.resolve_reference(info=info, id=id)
    # logging.info(f"form_by_id ({result})")
    return result

from dataclasses import dataclass
from uoishelpers.resolvers import createInputs

# FormTypeWhereFilter_ = typing.Annotated["FormTypeWhereFilter", strawberry.lazy(".FormTypeGQLModel")]
@createInputs
@dataclass
class FormInputFilter:
    name: str
    name_en: str
    valid: bool
    type_id: uuid.UUID
    createdby: uuid.UUID

    from .FormTypeGQLModel import FormTypeInputFilter
    type: FormTypeInputFilter

form_page = strawberry.field(
    description="Retrieves the form type",
    permission_classes=[OnlyForAuthentized],
    graphql_type=typing.List[FormGQLModel],
    resolver=PageResolver[FormGQLModel](whereType=FormInputFilter)
)

#############################################################
#
# Mutations
#
#############################################################


@strawberry.input(description="Attributes for creating a new form")
class FormInsertGQLModel:
    type_id: IDType = strawberry.field(description="ID of the form type")
    id: typing.Optional[IDType] = strawberry.field(
        description="Client-generated ID for the form (optional)", default=None
    )
    
    rbacobject_id: typing.Optional[uuid.UUID] = strawberry.field(
        description="user_id or group_id, allows resolution of authorized users, if not present, logged user will be assigned", default=None)
    name: typing.Optional[str] = strawberry.field(description="Name of the form", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="English name of the form", default=None)
    status: typing.Optional[str] = strawberry.field(description="Status of the form", default=None)
    valid: typing.Optional[bool] = strawberry.field(description="Indicates if the form is valid", default=True)
    type_id: typing.Optional[IDType] = strawberry.field(description="ID of the form type", default=None)
    state_id: typing.Optional[IDType] = strawberry.field(description="ID of the form state", default=None)
    createdby_id: strawberry.Private[uuid.UUID] = None 


@strawberry.input(description="Input structure - U operation")
class FormUpdateGQLModel:
    lastchange: datetime.datetime = strawberry.field(description="timestamp of last change = TOKEN")
    id: uuid.UUID = strawberry.field(description="primary key (UUID), identifies object of operation")

    name: typing.Optional[str] = strawberry.field(description="form name", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="form name", default=None)
    type_id: typing.Optional[uuid.UUID] = strawberry.field(description="form type", default=None)
    valid: typing.Optional[bool] = None
    changedby: strawberry.Private[uuid.UUID] = None

@strawberry.input(description="Attributes for updating an existing form")
class FormUpdateGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the form to update")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )
    name: typing.Optional[str] = strawberry.field(description="Updated name of the form", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="Updated English name of the form", default=None)
    status: typing.Optional[str] = strawberry.field(description="Updated status of the form", default=None)
    valid: typing.Optional[bool] = strawberry.field(description="Updated validity of the form", default=None)
    type_id: typing.Optional[IDType] = strawberry.field(description="Updated form type ID", default=None)
    state_id: typing.Optional[IDType] = strawberry.field(description="Updated form state ID", default=None)
    changedby_id: strawberry.Private[uuid.UUID] = None


@strawberry.input(description="Attributes for deleting an existing form")
class FormDeleteGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the form to delete")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )    

@strawberry.mutation(
        description="Create a new form",
        permission_classes=[
            OnlyForAuthentized,
            SimpleInsertPermission[FormGQLModel](roles=["administrátor"]),
        ],
    )
async def form_insert(
    self, info: strawberry.types.Info, form: FormInsertGQLModel
) -> typing.Union[FormGQLModel, InsertError[FormGQLModel]]:
    return await Insert[FormGQLModel].DoItSafeWay(info=info, entity=form)

@strawberry.mutation(
    description="Update an existing form",
    permission_classes=[
        OnlyForAuthentized,
        SimpleUpdatePermission[FormGQLModel](roles=["administrátor"]),
    ],
)
async def form_update(
    self, info: strawberry.types.Info, form: FormUpdateGQLModel
) -> typing.Union[FormGQLModel, UpdateError[FormGQLModel]]:
    return await Update[FormGQLModel].DoItSafeWay(info=info, entity=form)

@strawberry.mutation(
    description="Delete an existing form",
    permission_classes=[
        OnlyForAuthentized,
        SimpleDeletePermission[FormGQLModel](roles=["administrátor"]),
    ],
)
async def form_delete(
    self, info: strawberry.types.Info, form: FormDeleteGQLModel
) -> typing.Optional[DeleteError[FormGQLModel]]:
    return await Delete[FormGQLModel].DoItSafeWay(info=info, entity=form)
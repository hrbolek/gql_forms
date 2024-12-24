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

FormGQLModel = Annotated["FormGQLModel", strawberry.lazy(".FormGQLModel")]
PartGQLModel = Annotated["PartGQLModel", strawberry.lazy(".PartGQLModel")]
StateGQLModel = Annotated["StateGQLModel", strawberry.lazy(".StateGQLModel")]

@strawberry.federation.type(
    keys=["id"], description="Entity representing a section within a form"
)
class SectionGQLModel(BaseGQLModel):
    """
    GraphQL model for the Section entity.
    Represents sections in forms, including their associated parts and form.
    """
    @classmethod
    def getLoader(cls, info: strawberry.types.Info):
        return getLoadersFromInfo(info=info).formsections    
    

    name: typing.Optional[str] = strawberry.field(
        description="Name of the section",
        permission_classes=[OnlyForAuthentized]
    )
    name_en: typing.Optional[str] = strawberry.field(
        description="English name of the section",
        permission_classes=[OnlyForAuthentized]
    )
    form_id: typing.Optional[IDType] = strawberry.field(
        description="Foreign key to the associated form",
        permission_classes=[OnlyForAuthentized]
    )
    order: typing.Optional[int] = strawberry.field(
        description="Order of the section in the parent entity",
        permission_classes=[OnlyForAuthentized]
    )
    status: typing.Optional[str] = strawberry.field(
        description="Status of the section",
        permission_classes=[OnlyForAuthentized]
    )
    state_id: typing.Optional[IDType] = strawberry.field(
        description="State of the request",
        permission_classes=[OnlyForAuthentized]
    )
    form: typing.Optional[FormGQLModel] = strawberry.field(
        description="The associated form for this section",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["FormGQLModel"](fkey_field_name="form_id")
    )
    state: typing.Optional[StateGQLModel] = strawberry.field(
        description="The state of the section",
        permission_classes=[OnlyForAuthentized],
        resolver=ScalarResolver["StateGQLModel"](fkey_field_name="state_id")
    )
    from .PartGQLModel import PartInputFilter
    parts: typing.List[PartGQLModel] = strawberry.field(
        description="Parts linked to this section",
        permission_classes=[OnlyForAuthentized],
        resolver=VectorResolver["PartGQLModel"](fkey_field_name="section_id", whereType=PartInputFilter)
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
class SectionWhereFilter:
    name: str
    name_en: str
    state_id: uuid.UUID
    form_id: IDType
    createdby_id: IDType

    from .FormGQLModel import FormInputFilter
    form: FormInputFilter

# resolve_sectionsForForm = createAttributeVectorResolver(
#     scalarType=SectionGQLModel, 
#     whereFilterType=SectionWhereFilter, 
#     foreignKeyName="from_id", description="Gets sections associated with form",
#     loaderLambda=lambda info: getLoadersFromInfo(info=info).sections
#     )
    
@strawberry.field(
    description="returns section from form by its id",
    permission_classes=[OnlyForAuthentized])
async def form_section_by_id(self, info: strawberry.types.Info, id: uuid.UUID) -> typing.Optional[SectionGQLModel]:
    return await SectionGQLModel.resolve_reference(info=info, id=id)
#############################################################
#
# Mutations
#
#############################################################

@strawberry.input(description="Attributes for creating a new form section")
class SectionInsertGQLModel:
    id: typing.Optional[IDType] = strawberry.field(
        description="Client-generated ID for the section (optional)", default=None
    )
    name: typing.Optional[str] = strawberry.field(description="Name of the section", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="English name of the section", default=None)
    form_id: typing.Optional[IDType] = strawberry.field(description="ID of the associated form", default=None)
    order: typing.Optional[int] = strawberry.field(description="Order of the section", default=None)
    status: typing.Optional[str] = strawberry.field(description="Status of the section", default=None)
    state_id: typing.Optional[IDType] = strawberry.field(description="ID of the state", default=None)
    createdby_id: strawberry.Private[IDType] = None 
    rbacobject_id: strawberry.Private[IDType] = None 

@strawberry.input(description="Attributes for updating an existing form section")
class SectionUpdateGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the section to update")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )
    name: typing.Optional[str] = strawberry.field(description="Updated name of the section", default=None)
    name_en: typing.Optional[str] = strawberry.field(description="Updated English name of the section", default=None)
    form_id: typing.Optional[IDType] = strawberry.field(description="Updated form ID", default=None)
    order: typing.Optional[int] = strawberry.field(description="Updated order of the section", default=None)
    status: typing.Optional[str] = strawberry.field(description="Updated status of the section", default=None)
    state_id: typing.Optional[IDType] = strawberry.field(description="Updated state ID", default=None)
    changedby_id: strawberry.Private[IDType] = None

@strawberry.input(description="Attributes for deleting an existing form section")
class SectionDeleteGQLModel:
    id: IDType = strawberry.field(description="Unique ID of the section to delete")
    lastchange: datetime.datetime = strawberry.field(
        description="Timestamp of the last modification"
    )

@strawberry.mutation(
    description="Create a new form section",
    permission_classes=[
        OnlyForAuthentized,
        SimpleInsertPermission[SectionGQLModel](roles=["administrator"]),
    ],
)
async def section_insert(
    self, info: strawberry.types.Info, section: SectionInsertGQLModel
) -> typing.Union[SectionGQLModel, InsertError[SectionGQLModel]]:
    section.createdby_id = info.context["user"].id  # Set the private field for the creator
    return await Insert[SectionGQLModel].DoItSafeWay(info=info, entity=section)

@strawberry.mutation(
    description="Update an existing form section",
    permission_classes=[
        OnlyForAuthentized,
        SimpleUpdatePermission[SectionGQLModel](roles=["administrator"]),
    ],
)
async def section_update(
    self, info: strawberry.types.Info, section: SectionUpdateGQLModel
) -> typing.Union[SectionGQLModel, UpdateError[SectionGQLModel]]:
    section.updatedby_id = info.context["user"].id  # Set the private field for the updater
    return await Update[SectionGQLModel].DoItSafeWay(info=info, entity=section)

@strawberry.mutation(
    description="Delete an existing form section",
    permission_classes=[
        OnlyForAuthentized,
        SimpleDeletePermission[SectionGQLModel](roles=["administrator"]),
    ],
)
async def section_delete(
    self, info: strawberry.types.Info, section: SectionDeleteGQLModel
) -> typing.Optional[DeleteError[SectionGQLModel]]:
    return await Delete[SectionGQLModel].DoItSafeWay(info=info, entity=section)
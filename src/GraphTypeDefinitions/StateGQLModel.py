import strawberry
from .BaseGQLModel import IDType

@strawberry.federation.type(extend=True, keys=["id"])
class StateGQLModel:
    id: IDType = strawberry.federation.field(external=True)

    from .BaseGQLModel import resolve_reference

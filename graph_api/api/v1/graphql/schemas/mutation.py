import strawberry
import json
from graph_api.api.v1.graphql.resolvers import (
    add_unit,
    update_unit,
    delete_unit,
    add_document,
    update_document,
    delete_document,
)
from graph_api.api.v1.graphql.types import Unit, Document, JSON
from graph_api.api.v1.graphql.models import (
    AddDocumentInput,
    UpdateDocumentInput,
    AddUnitInput,
    UpdateUnitInput,
)
from strawberry.field_extensions import InputMutationExtension


@strawberry.type
class UnitMutations:
    @strawberry.mutation(extensions=[InputMutationExtension()])
    async def addUnit(
        self, name: str | None = None, description: str | None = None
    ) -> Unit:
        return await add_unit(AddUnitInput(name=name, description=description))

    @strawberry.mutation(extensions=[InputMutationExtension()])
    async def updateUnit(
        self, id: int, name: str | None = None, description: str | None = None
    ) -> Unit:
        return await update_unit(
            UpdateUnitInput(id=id, name=name, description=description)
        )

    @strawberry.mutation(extensions=[InputMutationExtension()])
    async def deleteUnit(self, id: int) -> Unit:
        return await delete_unit(id)


def transform_json_to_dict(value: JSON | None) -> dict | None:
    if isinstance(value, str):
        value = json.loads(value)
    # TODO: understand if should use 'strawberry.asdict(value)'
    return value if isinstance(value, dict) else None


@strawberry.type
class DocumentMutations:
    @strawberry.mutation(extensions=[InputMutationExtension()])
    async def addDocument(
        self,
        unit_id: int,
        name: str,
        description: str | None = None,
        content: JSON | None = None,
    ) -> Document:
        return await add_document(
            AddDocumentInput(
                unit_id=unit_id,
                name=name,
                description=description,
                content=transform_json_to_dict(content),
            )
        )

    @strawberry.mutation(extensions=[InputMutationExtension()])
    async def updateDocument(
        self,
        id: int,
        name: str | None = None,
        description: str | None = None,
        content: JSON | None = None,
    ) -> Document:
        return await update_document(
            UpdateDocumentInput(
                id=id,
                name=name,
                description=description,
                content=transform_json_to_dict(content),
            )
        )

    @strawberry.mutation(extensions=[InputMutationExtension()])
    async def deleteDocument(self, id: int) -> Document:
        return await delete_document(id)


@strawberry.type
class Mutation:
    @strawberry.field
    def unit(self) -> UnitMutations:
        return UnitMutations()

    @strawberry.field
    def document(self) -> DocumentMutations:
        return DocumentMutations()

import strawberry
from graph_api.api.v1.graphql.resolvers import add_unit, update_unit, delete_unit
from graph_api.api.v1.graphql.types import Unit
from strawberry.field_extensions import InputMutationExtension


@strawberry.type
class UnitMutations:
    @strawberry.mutation(extensions=[InputMutationExtension()])
    async def add(self, info, name: str, description: str) -> Unit:
        return await add_unit(name, description)

    @strawberry.mutation(extensions=[InputMutationExtension()])
    async def update(self, info, id: int, name: str, description: str) -> Unit:
        return await update_unit(id, name, description)

    @strawberry.mutation(extensions=[InputMutationExtension()])
    async def delete(self, info, id: int) -> Unit:
        return await delete_unit(id)


@strawberry.type
class Mutation:
    @strawberry.field
    def unit(self) -> UnitMutations:
        return UnitMutations()

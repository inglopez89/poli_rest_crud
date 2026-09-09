import graphene
from graphene_django import DjangoObjectType
from api.models import Producto


# 1. Tipo GraphQL basado en el modelo Producto
class ProductoType(DjangoObjectType):
    class Meta:
        model = Producto
        fields = "__all__"  # expone id, nombre, descripcion, precio


# 2. Queries: qué se puede consultar
class Query(graphene.ObjectType):
    todos_productos = graphene.List(ProductoType)
    producto = graphene.Field(ProductoType, id=graphene.Int(required=True))

    def resolve_todos_productos(root, info):
        return Producto.objects.all()

    def resolve_producto(root, info, id):
        return Producto.objects.filter(id=id).first()


# 3. Mutations: crear, actualizar, eliminar
class CrearProducto(graphene.Mutation):
    class Arguments:
        nombre = graphene.String(required=True)
        descripcion = graphene.String(required=True)
        precio = graphene.Decimal(required=True)

    producto = graphene.Field(ProductoType)

    def mutate(root, info, nombre, descripcion, precio):
        producto = Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio
        )
        return CrearProducto(producto=producto)


class ActualizarProducto(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        nombre = graphene.String()
        descripcion = graphene.String()
        precio = graphene.Decimal()

    producto = graphene.Field(ProductoType)

    def mutate(root, info, id, nombre=None, descripcion=None, precio=None):
        producto = Producto.objects.filter(id=id).first()
        if producto is None:
            return None
        if nombre is not None:
            producto.nombre = nombre
        if descripcion is not None:
            producto.descripcion = descripcion
        if precio is not None:
            producto.precio = precio
        producto.save()
        return ActualizarProducto(producto=producto)


class EliminarProducto(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(root, info, id):
        producto = Producto.objects.filter(id=id).first()
        if producto is None:
            return EliminarProducto(ok=False)
        producto.delete()
        return EliminarProducto(ok=True)


class Mutation(graphene.ObjectType):
    crear_producto = CrearProducto.Field()
    actualizar_producto = ActualizarProducto.Field()
    eliminar_producto = EliminarProducto.Field()


# 4. Esquema final (coincide con GRAPHENE.SCHEMA en settings.py)
schema = graphene.Schema(query=Query, mutation=Mutation)

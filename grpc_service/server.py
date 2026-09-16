import os
import sys
import django
from concurrent import futures
import grpc

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest_crud.settings')
django.setup()

from api.models import Producto
import producto_pb2
import producto_pb2_grpc

class ProductoService(producto_pb2_grpc.ProductoServiceServicer):
    def CrearProducto(self, request, context):
        producto = Producto.objects.create(nombre=request.nombre, descripcion=request.descripcion,
                                            precio=request.precio)
        return producto_pb2.ProductoResponse(id=producto.id, nombre=producto.nombre, descripcion=producto.descripcion,
                                         precio=producto.precio)
    
    def ObtenerProducto(self, request, context):
        producto = Producto.objects.filter(id=request.id).first()
        if producto is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Producto con id {request.id} no encontrado")
            return producto_pb2.ProductoResponse()
        return producto_pb2.ProductoResponse(
            id=producto.id,
            nombre=producto.nombre,
            descripcion=producto.descripcion,
            precio=float(producto.precio)
        )

    def ListarProductos(self, request, context):
        productos = Producto.objects.all()
        return producto_pb2.ListaProductos(
            productos=[
                producto_pb2.ProductoResponse(
                    id=p.id, nombre=p.nombre,
                    descripcion=p.descripcion, precio=float(p.precio)
                ) for p in productos
            ]
        )

    def ActualizarProducto(self, request, context):
        producto = Producto.objects.filter(id=request.id).first()
        if producto is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Producto con id {request.id} no encontrado")
            return producto_pb2.ProductoResponse()
        producto.nombre = request.nombre
        producto.descripcion = request.descripcion
        producto.precio = request.precio
        producto.save()
        return producto_pb2.ProductoResponse(
            id=producto.id, nombre=producto.nombre,
            descripcion=producto.descripcion, precio=float(producto.precio)
        )

    def EliminarProducto(self, request, context):
        producto = Producto.objects.filter(id=request.id).first()
        if producto is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Producto con id {request.id} no encontrado")
            return producto_pb2.EliminarResponse(ok=False)
        producto.delete()
        return producto_pb2.EliminarResponse(ok=True)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    producto_pb2_grpc.add_ProductoServiceServicer_to_server(ProductoService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Servidor gRPC corriendo en puerto 50051...")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
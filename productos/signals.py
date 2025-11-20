from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UnidadProducto
from usuarios.models import PedidoItem
from datetime import date

@receiver(post_save, sender=PedidoItem)
def crear_unidades_pedido(sender, instance, created, **kwargs):
    """
    Cada vez que se cree un PedidoItem, se generan las unidades de producto correspondientes.
    """
    if created:
        cantidad = max(instance.cantidad, 0)  # Por si acaso la cantidad es negativa o cero
        for i in range(cantidad):
            # Crear un lote único por unidad
            lote = f'LOTE-{instance.id}-{i+1}'
            UnidadProducto.objects.create(
                producto=instance.producto,
                pedido_item=instance,
                lote=lote,
                fecha_caducidad=instance.producto.fecha_caducidad,
                estado='disponible'
            )

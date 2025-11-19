# pagos/views.py ESTO ES PARA CQUE SALGA EL COSTO DELL ENVIO DEL DOMICILIO 
import hashlib
import time
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from .models import Transaccion
from usuarios.models import Pedido, Direccion, PedidoItem
from productos.models import Producto

import hashlib
import time
from django.shortcuts import render, redirect
from django.conf import settings
from usuarios.models import Pedido, PedidoItem
from django.db import transaction
from .models import Transaccion
from productos.models import Producto


def checkout(request):
    carrito = request.session.get("carrito", {})
    
    if not carrito:
        return redirect("productos:producto")
    
    productos = []
    subtotal = 0

    for item in carrito.values():
        imagen = item.get('imgProduc', '')
        nombre = item.get('nombProduc', 'Sin nombre')
        cantidad = int(item.get('cantidad', 0))
        precio = float(item.get('precio', 0))
        precio_producto = precio * cantidad
        subtotal += precio_producto

        productos.append({
            'imagen': imagen,
            'nombre': nombre,
            'cantidad': cantidad,
            'precio': precio,
            'subtotal': precio_producto
        })

    # Dirección + envío
    direccion_guardada = None
    costo_envio = 0

    if request.user.is_authenticated:
        try:
            direccion_guardada = Direccion.objects.get(usuario=request.user, es_principal=True)

            ciudad = direccion_guardada.ciudad.lower().strip()

            if 'ibague' in ciudad or 'ibagué' in ciudad:
                costo_envio = 8000
            elif any(c in ciudad for c in [
                'espinal', 'melgar', 'honda', 'mariquita', 'chaparral',
                'líbano', 'libano', 'flandes', 'guamo', 'saldaña', 'saldana',
                'purificacion', 'purificación', 'cajamarca', 'armero', 'venadillo'
            ]):
                costo_envio = 12000

        except Direccion.DoesNotExist:
            pass

    # Calcular totales
    iva = subtotal * 0.19
    total_sin_envio = subtotal + iva
    total_final = total_sin_envio + costo_envio

    # Generar order_id SOLO para Bold
    timestamp = int(time.time())
    order_id = f"ORD-{timestamp}"

    amount = int(total_final)
    currency = "COP"
    cadena = f"{order_id}{amount}{currency}{settings.BOLD_SECRET_KEY}"
    integrity_hash = hashlib.sha256(cadena.encode()).hexdigest()

    redirection_url = request.build_absolute_uri('/pagos/respuesta/')

    context = {
        'productos': productos,
        'subtotal': round(subtotal, 2),
        'iva': round(iva, 2),
        'costo_envio': round(costo_envio, 2),
        'total_sin_envio': round(total_sin_envio, 2),
        'total_final': round(total_final, 2),
        'order_id': order_id,
        'amount': amount,
        'currency': currency,
        'integrity_hash': integrity_hash,
        'redirection_url': redirection_url,
        'bold_api_key': settings.BOLD_API_KEY,
        'direccion_guardada': direccion_guardada,
    }

    return render(request, 'pagos/checkout.html', context)

def payment_response(request):
    order_id = request.GET.get('bold-order-id')
    tx_status = request.GET.get('bold-tx-status')

    if not order_id:
        return redirect('productos:producto')

    carrito = request.session.get("carrito", {})
    productos_ids = []

    if tx_status == 'approved':
        # Calcular total igual que en checkout
        subtotal = sum(float(item['precio']) * int(item['cantidad']) for item in carrito.values())
        iva = subtotal * 0.19
        costo_envio = 0

        try:
            direccion = Direccion.objects.get(usuario=request.user, es_principal=True)
            ciudad = direccion.ciudad.lower().strip()

            if 'ibague' in ciudad or 'ibagué' in ciudad:
                costo_envio = 8000
            elif any(c in ciudad for c in [
                'espinal', 'melgar', 'honda', 'mariquita', 'chaparral',
                'líbano', 'libano', 'flandes', 'guamo', 'saldaña', 'saldana',
                'purificacion', 'purificación', 'cajamarca', 'armero', 'venadillo'
            ]):
                costo_envio = 12000
        except Direccion.DoesNotExist:
            pass

        total_final = subtotal + iva + costo_envio

        # Crear pedido
        pedido = Pedido.objects.create(
            usuario=request.user,
            order_id=order_id,
            total=total_final,
            estado='pagado',
            pago=True
        )

        # Crear items
        for producto_id, item in carrito.items():
            producto = Producto.objects.get(id=int(producto_id))
            cantidad = int(item['cantidad'])
            precio_unitario = float(item['precio'])

            PedidoItem.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario
            )

            productos_ids.append(producto.id)

            # Restar stock
            producto.stock -= cantidad
            if producto.stock < 0:
                producto.stock = 0
            producto.save()

        # Registrar transacción
        Transaccion.objects.create(
            order_id=order_id,
            usuario=request.user,
            pedido=pedido,
            monto=total_final,
            estado='approved'
        )

        # Vaciar carrito
        request.session['carrito'] = {}
        request.session.modified = True

    context = {
        'order_id': order_id,
        'tx_status': tx_status,
        'producto_id': productos_ids[0] if productos_ids else None,
        'productos_ids': productos_ids,
    }

    return render(request, 'pagos/payment_response.html',context)
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date
from cloudinary.models import CloudinaryField

# ====================== CATEGORÍA ======================
class Category(models.Model):
    nombCategory = models.CharField(max_length=140)

    def __str__(self):
        return self.nombCategory

    class Meta:
        verbose_name_plural = 'Categoria'

# ====================== PRODUCTO ======================
class Producto(models.Model):
    nombProduc = models.CharField(max_length=130)
    descripcion = models.CharField(max_length=300)
    Categoria = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imgProduc = CloudinaryField('image')
    stock = models.IntegerField(default=0)
    estado = models.BooleanField(default=True)  # True = Activo, False = Inactivo
    fecha_caducidad = models.DateField(null=True, blank=True)
    vendidos = models.IntegerField(default=0)

    def esta_vencido(self):
        if self.fecha_caducidad:
            return date.today() > self.fecha_caducidad
        return False

    def __str__(self):
        return self.nombProduc

# ====================== UNIDAD DE PRODUCTO ======================
class UnidadProducto(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='unidades')
    pedido_item = models.ForeignKey('usuarios.PedidoItem', on_delete=models.CASCADE, null=True, blank=True, related_name='unidades')
    lote = models.CharField(max_length=50)
    fecha_caducidad = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=[('disponible', 'Disponible'), ('devuelto', 'Devuelto')], default='disponible')

    def __str__(self):
        return f"{self.producto.nombProduc} - Lote {self.lote} ({self.estado})"

# ====================== SERVICIO ======================
class Servicio(models.Model):
    TIPO_CHOICES = [
        ('compra', 'Compra')
    ]
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return self.nombre

# ====================== CALIFICACIÓN ======================
class Calificacion(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='calificaciones', null=True, blank=True)
    servicio = models.ForeignKey('Servicio', on_delete=models.CASCADE, related_name='calificaciones', null=True, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puntuacion_servicio = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    puntuacion_productos = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    aprobado = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.servicio.nombre} - {self.puntuacion_servicio} / {self.puntuacion_productos}'

# ====================== CARRITO ======================
class CarritoItem(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('usuario', 'producto')

    def __str__(self):
        return f"{self.producto.nombProduc} x {self.cantidad}"

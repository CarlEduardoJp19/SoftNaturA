from django.conf import settings
from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# ====================== USUARIO ======================
class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Debes ingresar un correo electrónico')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('admin', 'Administrador'),
        ('cliente', 'Cliente'),
    )

    email = models.EmailField(unique=True, max_length=60)
    nombre = models.CharField(max_length=150, unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return self.nombre

# ====================== PEDIDO ======================
class Pedido(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=30, choices=[
        ('pendiente','Pendiente'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
    ], default='pendiente')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pago = models.BooleanField(default=True)

    def __str__(self):
        return f"Pedido #{self.id} de {self.usuario.email}"

class PedidoItem(models.Model):
    pedido = models.ForeignKey('Pedido', related_name="items", on_delete=models.CASCADE)
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Items de Pedido'

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombProduc}"

    def subtotal(self):
        return self.cantidad * self.precio_unitario

# ====================== MENSAJES ======================
class Mensaje(models.Model):
    nombre = models.CharField(max_length=150)
    correo = models.EmailField()
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.asunto}"

# ====================== DEVOLUCIONES ======================
class Devolucion(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada'),
    ]
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devoluciones')
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE)
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, related_name='devoluciones')
    unidad_producto = models.ForeignKey('productos.UnidadProducto', on_delete=models.SET_NULL, null=True, blank=True)
    item = models.ForeignKey('PedidoItem', on_delete=models.CASCADE, null=True, blank=True, related_name='devoluciones')
    motivo = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    foto1 = CloudinaryField('foto1', blank=True, null=True)
    foto2 = CloudinaryField('foto2', blank=True, null=True)
    foto3 = CloudinaryField('foto3', blank=True, null=True)
    unidad = models.PositiveIntegerField(default=1)
    seleccionada = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Devolución'
        verbose_name_plural = 'Devoluciones'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"Devolución #{self.id} - {self.usuario.nombre} - {self.estado}"

    def get_fotos(self):
        fotos = []
        if self.foto1:
            fotos.append(self.foto1.url)
        if self.foto2:
            fotos.append(self.foto2.url)
        if self.foto3:
            fotos.append(self.foto3.url)
        return fotos

class HistorialDevolucion(models.Model):
    devolucion = models.ForeignKey('Devolucion', on_delete=models.CASCADE, related_name='historial')
    estado = models.CharField(max_length=20, choices=Devolucion.ESTADOS)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario_admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    comentario = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha_cambio']
        verbose_name = 'Historial de Devolución'
        verbose_name_plural = 'Historial de Devoluciones'

    def __str__(self):
        return f"Devolución #{self.devolucion.id} - {self.estado} - {self.fecha_cambio}"

# ====================== DIRECCIÓN ======================
class Direccion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='direcciones')
    nombre_completo = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    direccion_completa = models.TextField()
    ciudad = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20, blank=True)
    notas_entrega = models.TextField(blank=True)
    es_principal = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'
        ordering = ['-es_principal', '-fecha_creacion']

    def __str__(self):
        return f"{self.nombre_completo} - {self.ciudad}"

    def save(self, *args, **kwargs):
        if self.es_principal:
            Direccion.objects.filter(usuario=self.usuario, es_principal=True).exclude(pk=self.pk).update(es_principal=False)
        super().save(*args, **kwargs)

# ====================== REEMPLAZOS ======================
class Reemplazo(models.Model):
    devolucion = models.OneToOneField('Devolucion', on_delete=models.CASCADE, related_name='reemplazo')
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reemplazo'
        verbose_name_plural = 'Reemplazos'

    def __str__(self):
        return f"Reemplazo Devolución #{self.devolucion.id} - {self.producto.nombProduc}"

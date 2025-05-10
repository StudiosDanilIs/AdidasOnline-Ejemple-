from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, password=None, **extra_fields):
        """
        Crea y guarda un usuario con el email y contraseña dados.
        """
        if not email:
            raise ValueError('El email es obligatorio')
        
        email = self.normalize_email(email).lower()
        user = self.model(email=email, nombre=nombre, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombre, password=None, **extra_fields):
        """
        Crea y guarda un superusuario con el email y contraseña dados.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(email, nombre, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _('Ya existe un usuario con este email.')
        }
    )
    nombre = models.CharField(
        _('nombre completo'),
        max_length=150
    )
    is_active = models.BooleanField(
        _('activo'),
        default=True,
        help_text=_('Designa si el usuario debe ser tratado como activo. Desmarque esta opción en lugar de borrar la cuenta.')
    )
    is_staff = models.BooleanField(
        _('equipo staff'),
        default=False,
        help_text=_('Designa si el usuario puede acceder al sitio de administración.')
    )
    date_joined = models.DateTimeField(
        _('fecha de registro'),
        default=timezone.now
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    objects = UsuarioManager()

    class Meta:
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Devuelve el nombre completo del usuario."""
        return self.nombre.strip()

    def get_short_name(self):
        """Devuelve el nombre corto del usuario (primer nombre)."""
        return self.nombre.split()[0] if self.nombre else self.email

    def save(self, *args, **kwargs):
        """Normaliza el email y guarda el usuario."""
        self.email = self.email.lower().strip()
        super().save(*args, **kwargs)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Envía un email al usuario."""
        from django.core.mail import send_mail
        send_mail(subject, message, from_email, [self.email], **kwargs)
          

class Producto(models.Model):
    nombre = models.CharField(max_length=80)
    descripcion = models.TextField(max_length=150)
    precio_actual = models.DecimalField(max_digits=10, decimal_places=2)
    precio_anterior = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    talla_min = models.IntegerField(default=36)
    talla_max = models.IntegerField(default=45)
    imagen = models.ImageField(upload_to='productos/')
    imagen1 = models.ImageField(upload_to='productos/', blank=True, null=True)
    imagen2 = models.ImageField(upload_to='productos/', blank=True, null=True)
    imagen3 = models.ImageField(upload_to='productos/', blank=True, null=True)
    imagen4 = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return self.nombre

    def tallas_disponibles(self):
        return [talla for talla in range(self.talla_min, self.talla_max + 1)]

class Carrito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    talla = models.IntegerField()

    def __str__(self):
        return f"{self.usuario.email} - {self.producto.nombre}"

    def subtotal(self):
        return self.producto.precio_actual * self.cantidad

class Compra(models.Model):
    METODO_PAGO_OPCIONES = [
        ('tarjeta', 'Tarjeta de Crédito'),
        ('paypal', 'PayPal'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    direccion_entrega = models.CharField(max_length=255)
    metodo_pago = models.CharField(max_length=50, choices=METODO_PAGO_OPCIONES)
    transaccion_id = models.CharField(max_length=100)

    def __str__(self):
        return f"Compra #{self.id} - {self.usuario.email}"

    def get_metodo_pago_display(self):
        return dict(self.METODO_PAGO_OPCIONES).get(self.metodo_pago, self.metodo_pago)

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} unidades"
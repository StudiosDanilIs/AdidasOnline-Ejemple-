from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.conf import settings
import os
from .models import Producto, Carrito, Compra, DetalleCompra, Usuario
from .forms import ProductoForm

# ===================== SEÑALES PARA MANEJO DE IMÁGENES =====================
@receiver(pre_delete, sender=Producto)
def eliminar_imagenes_producto(sender, instance, **kwargs):
    """
    Elimina las imágenes asociadas a un producto cuando se borra el producto
    """
    campos_imagen = ['imagen', 'imagen1', 'imagen2', 'imagen3', 'imagen4']
    for campo in campos_imagen:
        imagen = getattr(instance, campo)
        if imagen:
            ruta_completa = os.path.join(settings.MEDIA_ROOT, str(imagen))
            if os.path.exists(ruta_completa):
                os.remove(ruta_completa)

@receiver(pre_save, sender=Producto)
def eliminar_imagen_vieja(sender, instance, **kwargs):
    """
    Elimina la imagen anterior cuando se actualiza por una nueva
    """
    if not instance.pk:
        return False
    
    try:
        producto_original = Producto.objects.get(pk=instance.pk)
    except Producto.DoesNotExist:
        return False
    
    campos_imagen = ['imagen', 'imagen1', 'imagen2', 'imagen3', 'imagen4']
    for campo in campos_imagen:
        imagen_original = getattr(producto_original, campo)
        imagen_nueva = getattr(instance, campo)
        
        if imagen_original and imagen_original != imagen_nueva:
            ruta_completa = os.path.join(settings.MEDIA_ROOT, str(imagen_original))
            if os.path.exists(ruta_completa):
                os.remove(ruta_completa)

# ===================== MODELO PRODUCTO (MEJORADO) =====================
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    form = ProductoForm
    list_display = ('nombre', 'precio_actual', 'precio_anterior', 'talla_min', 'talla_max')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('talla_min', 'talla_max')
    readonly_fields = ('precio_anterior',)
    
    def delete_queryset(self, request, queryset):
        """
        Sobrescribe para eliminar imágenes al borrar múltiples productos
        """
        for producto in queryset:
            eliminar_imagenes_producto(Producto, producto)
        super().delete_queryset(request, queryset)

# ===================== MODELO USUARIO (MANTENIDO) =====================
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('email', 'nombre', 'is_staff', 'date_joined')
    search_fields = ('email', 'nombre')
    list_filter = ('is_staff', 'is_active')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('nombre',)}),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )
    
    readonly_fields = ('date_joined',)
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

# ===================== MODELO CARRITO (MANTENIDO) =====================
@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'producto', 'talla', 'cantidad', 'subtotal')
    list_select_related = ('usuario', 'producto')
    search_fields = ('usuario__email', 'producto__nombre')
    list_filter = ('producto', 'talla')
    autocomplete_fields = ['usuario', 'producto']

# ===================== DETALLE COMPRA (INLINE) =====================
class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    autocomplete_fields = ['producto']

# ===================== MODELO COMPRA (MANTENIDO) =====================
@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    inlines = [DetalleCompraInline]
    list_display = ('id', 'usuario', 'fecha', 'total_formateado', 'metodo_pago', 'estado')
    list_filter = ('metodo_pago', 'fecha')
    search_fields = ('usuario__email', 'transaccion_id')
    readonly_fields = ('fecha', 'transaccion_id')
    autocomplete_fields = ['usuario']

    def total_formateado(self, obj):
        return f"${obj.total:,.2f}"
    total_formateado.short_description = 'Total'

    def estado(self, obj):
        return "Completada" if obj.detalles.exists() else "Pendiente"

# ===================== MODELO DETALLE COMPRA (MANTENIDO) =====================
@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = ('compra', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_select_related = ('compra', 'producto')
    search_fields = ('compra__transaccion_id', 'producto__nombre')
    readonly_fields = ('compra', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    autocomplete_fields = ['compra', 'producto']
# context_processors.py
from django.contrib.auth import get_user_model

def usuario_actual(request):
    """
    Añade el usuario autenticado al contexto de todas las plantillas.
    Elimina la necesidad de manejar sesiones manualmente.
    """
    User = get_user_model()
    
    # Obtener usuario autenticado
    usuario = request.user if request.user.is_authenticated else None
    
    # Si se necesita información adicional del modelo User:
    if usuario:
        try:
            # Cargar el objeto completo desde la base de datos
            # (opcional, solo si se necesitan campos adicionales)
            usuario_completo = User.objects.get(pk=usuario.pk)
            return {'usuario': usuario_completo}
        except User.DoesNotExist:
            pass
    
    return {'usuario': usuario}
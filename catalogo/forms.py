from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from .models import Producto, Usuario

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre", "descripcion", "precio_actual", "talla_min", "talla_max",
            "imagen", "imagen1", "imagen2", "imagen3", "imagen4"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configuración de etiquetas
        self.fields["nombre"].label = "Nombre del Producto"
        self.fields["descripcion"].label = "Descripción del Producto"
        self.fields["precio_actual"].label = "Precio Actual"
        self.fields["talla_min"].label = "Talla Mínima (Ej: 36)"
        self.fields["talla_max"].label = "Talla Máxima (Ej: 45)"
        
    def save(self, commit=True):
        producto = super().save(commit=False)
        if producto.pk:  # Actualización de precio anterior
            producto.precio_anterior = Producto.objects.get(pk=producto.pk).precio_actual
        if commit:
            producto.save()
        return producto

class RegistroForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar Contraseña'})
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'email']  # Campos actualizados
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre de usuario'}),  # Nuevo campo
            'email': forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}),
        }
        labels = {
            'nombre': 'Nombre de usuario',  # Etiqueta personalizada
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'autofocus': True,
            'placeholder': 'Correo electrónico',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'form-control'
        })
    )

    def clean_username(self):
        email = self.cleaned_data['username'].lower().strip()
        if not Usuario.objects.filter(email=email).exists():
            raise ValidationError("No existe una cuenta con este email")
        return email

class RecuperarCuentaForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico'})
    )

class CompraForm(forms.Form):
    TALLAS = [(i, str(i)) for i in range(36, 46)]  # Tallas del 36 al 45
    
    talla = forms.ChoiceField(
        choices=TALLAS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cantidad = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
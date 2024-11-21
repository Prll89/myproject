from django import template
from accounts.models import Contact

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_item_by_email(email):
    """Busca un contacto por su correo electrónico."""
    try:
        return Contact.objects.get(email=email)
    except Contact.DoesNotExist:
        return None

# Filtro personalizado para dividir una cadena
@register.filter
def split(value, key):
    """Dividir la cadena 'value' usando el delimitador 'key'."""
    return value.split(key)
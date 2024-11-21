# accounts/templatetags/custom_tags.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)  # Retorna 0 si la clave no existe
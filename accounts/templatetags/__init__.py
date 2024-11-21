from django import template

register = template.Library()

@register.filter
def split(value, delimiter=', '):
    """Divide una cadena en una lista usando el delimitador proporcionado."""
    return value.split(delimiter)

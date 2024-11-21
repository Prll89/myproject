# accounts/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def split(value, separator):
    return value.split(separator)

@register.filter(name='add_class')
def add_class(value, css_class):
    return value.as_widget(attrs={"class": css_class})

@register.filter
def pluck(objects_list, key_name):
    return [getattr(obj, key_name) for obj in objects_list if hasattr(obj, key_name)]
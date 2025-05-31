
from django import template

register = template.Library()

@register.filter
def class_name(value):
    return value.__class__.__name__

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')
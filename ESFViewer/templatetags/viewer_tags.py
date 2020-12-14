from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def thousands(value):
    """Formats number values with blank space thousand separator"""
    try:
        value = float(value)
    except ValueError:
        return value
    return f"{value:,}".replace(',',' ')
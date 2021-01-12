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

@register.filter
def to_bool(value):
    """Converts XML boolean values(true, false) to Python bool"""
    return value == 'true ' or value == 'true'

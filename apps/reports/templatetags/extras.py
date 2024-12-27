from django import template

register = template.Library()


@register.filter
def to_range(value):
    """Converts an integer to a range from 1 to value"""
    return range(1, value + 1)

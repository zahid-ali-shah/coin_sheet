from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def is_today(date):
    return timezone.localtime(timezone.now()).day == date.day

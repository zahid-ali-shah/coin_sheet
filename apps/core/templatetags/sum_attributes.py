from django import template
from django.utils.html import format_html
register = template.Library()


@register.simple_tag
def sum_attribute(daily_expenses):
    p_sum = sum(exp.transaction.amount for exp in daily_expenses if exp.transaction.is_deposited)
    n_sum = sum(exp.transaction.amount for exp in daily_expenses if not exp.transaction.is_deposited)
    sum_total = p_sum - n_sum
    return format_html(
            '<span style="color: #{};">{}</span>',
            ('008000' if sum_total > 0 else 'FF0000'), '{:,.2f}'.format(abs(sum_total))
        )

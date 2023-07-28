from django import template

register = template.Library()

@register.filter
def get_star_range(value):
    try:
        rating = int(value)
    except ValueError:
        rating = 0

    return range(rating)

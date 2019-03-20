from django import template
register = template.Library()

@register.filter(name='keyValue')
def keyValue(dict, key):
    print(dict[key])
    return dict[key]
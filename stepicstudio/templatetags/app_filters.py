import math
from django import template

register = template.Library()

@register.filter(name='sec_to_time')
def sec_to_time(value):
    hour = value // 3600
    min = int(math.fmod(value, 3600)) // 60
    sec = int(math.fmod(value, 60))
    return ''.join(map(lambda x: str(x[0]) + x[1],
                       (filter(lambda x: x[0] != 0, [(hour, 'H '), (min, 'min '), (sec, 'sec')]))))

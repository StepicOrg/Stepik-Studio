import math
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='sec_to_time')
def sec_to_time(value):
    hour = value // 3600
    min = int(math.fmod(value, 3600)) // 60
    sec = int(math.fmod(value, 60))
    return ''.join(map(lambda x: str(x[0]) + x[1],
                       (filter(lambda x: x[0] != 0, [(hour, 'H '), (min, 'min '), (sec, 'sec')]))))


@register.filter(name="formatting_text")
def formatting_text(value):
    return mark_safe(value.replace('\n', '<br/>'))

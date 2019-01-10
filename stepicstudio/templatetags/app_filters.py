import math
import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='sec_to_time')
def sec_to_time(value):
    if value < 0.1:
        return '<0.1'

    hour = value // 3600
    mins = int(math.fmod(value, 3600)) // 60

    if mins > 0:
        sec = int(math.fmod(value, 60))
    else:
        sec = '%.1f' % math.fmod(value, 60.0)

    return ''.join(map(lambda x: str(x[0]) + x[1],
                       (filter(lambda x: x[0] != 0, [(hour, 'H '), (mins, 'min '), (sec, 'sec')]))))


@register.filter(name="formatting_text")
def formatting_text(value):
    return mark_safe(value.replace('\n', '<br/>'))


@register.filter(name='to_custom_name')
def to_custom_name(substep_name, user_name_template=None):
    m = re.search(r'(\d+)_(\d+)', substep_name)

    if not m:  # to support legacy naming
        m = re.search(r'Step(\d+)from(\d+)', substep_name)

    ss_id, s_id = (m.group(1), m.group(2))
    tmp = re.sub(r'(\$id)', re.escape(ss_id), user_name_template)
    fin = re.sub(r'(\$stepid)', re.escape(s_id), tmp)
    return fin

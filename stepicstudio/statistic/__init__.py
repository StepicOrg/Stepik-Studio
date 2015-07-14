from stepicstudio.models import StatInfo, SubStep
import time


def add_stat_info(substep_id):
    substep = SubStep.objects.all().get(id=substep_id)
    substep_stat = StatInfo()
    substep_stat.substep = substep_id
    substep_stat.substep_uuid = substep.start_time
    substep_stat.duration = int(((round(time.time() * 1000)) - substep.start_time))
    substep_stat.save()

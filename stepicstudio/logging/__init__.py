from django.conf import settings
from raven.contrib.django.client import DjangoClient


class SentryLocatedClient(DjangoClient):
    def build_msg(self, *args, **kwargs):
        data = super(DjangoClient, self).build_msg(*args, **kwargs)
        data['tags']['location'] = settings.LOGGER_TAG
        return data

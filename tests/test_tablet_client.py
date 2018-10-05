from django.test import TestCase

from stepicstudio.operations_statuses.statuses import ExecutionStatus
from stepicstudio.ssh_connections.tablet_client import TabletClient


class TestTabletClient(TestCase):
    def should_successfully_download_dir(self):
        local_dir = 'C:\\Development\\Tests'
        remote_dir = 'home/user/VIDEO/STEPICSTUDIO/tests'
        client = TabletClient()
        status = client.download_dir(remote_dir, local_dir)

        self.assertEqual(status.status, ExecutionStatus.SUCCESS)
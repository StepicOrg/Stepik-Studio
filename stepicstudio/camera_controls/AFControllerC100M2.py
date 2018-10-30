import logging

import requests
from django.conf import settings
from singleton_decorator import singleton

from stepicstudio.operations_statuses.operation_result import InternalOperationResult
from stepicstudio.operations_statuses.statuses import ExecutionStatus

URI_LOGIN = '/api/acnt/login'
URI_AF = '/api/cam/drivelens?af=oneshot'

TIMEOUT = 3  # seconds

logging.getLogger('requests').setLevel(logging.WARNING)


@singleton
class AFControllerC100M2(object):
    def __init__(self):
        self.absolute_path = 'http://' + settings.CAMERA_IP
        self.session = requests.Session()
        self.init_connection()

    def focus_camera(self, attempts=2):
        if self.session.cookies.__len__() == 0:
            self.init_connection()

        for _ in range(0, attempts):
            response = self.session.get(self.absolute_path + URI_AF, timeout=TIMEOUT)
            if response.status_code == requests.codes.get('ok') and response.json()['res'] == 'ok':
                return InternalOperationResult(ExecutionStatus.SUCCESS)
            else:
                self.reconnect()

        return InternalOperationResult(ExecutionStatus.FATAL_ERROR, 'Cannot connection to camera failed.')

    def init_connection(self) -> InternalOperationResult:
        try:
            login_response = self.session.get(self.absolute_path + URI_LOGIN, timeout=TIMEOUT)
        except Exception as e:
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR, e)

        if login_response.status_code != requests.codes.get('ok'):
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR,
                                           'Response code: {}' % login_response.status_code)

        if login_response.json()['res'] != 'ok':
            return InternalOperationResult(ExecutionStatus.FATAL_ERROR, 'Camera login failed')

        return InternalOperationResult(ExecutionStatus.SUCCESS)

    def reconnect(self, attempts=1):
        for _ in range(0, attempts):
            self.session.cookies.clear()
            res = self.init_connection()
            if res.status is ExecutionStatus.SUCCESS:
                return

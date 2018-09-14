class InternalOperationResult(object):

    def __init__(self, status, message=""):
        self.message = message
        self.status = status

    def __str__(self):
        return self.message

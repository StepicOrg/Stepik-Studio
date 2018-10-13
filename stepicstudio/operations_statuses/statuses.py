from enum import Enum


class ExecutionStatus(Enum):
    SUCCESS = 1
    FIXABLE_ERROR = 2
    FATAL_ERROR = 3

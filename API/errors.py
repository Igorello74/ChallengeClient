from typing import Any


class TasksOverError(RuntimeError):
    def __init__(self, task_type: str | None, *args):
        self.task_type = task_type
        super().__init__(
            f"No more tasks of the '{task_type}' type left on this round",
            *args)


class NoRoundCurrentlyRunningError(RuntimeError):
    def __init__(self, *args):
        super().__init__("No round is currently running", *args)


class DeserializationError(ValueError):
    def __init__(self, obj: Any, cls: type, *args):
        super().__init__(
            f"Can't deserialize the following object into {cls.__name__}:\n{obj}",
            *args)

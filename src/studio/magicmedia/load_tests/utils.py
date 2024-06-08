from typing import Callable

import gevent


def schedule_task(task_function: Callable[[], None], interval: int) -> None:
    def run_task() -> None:
        while True:
            gevent.sleep(interval)
            task_function()

    gevent.spawn(run_task)

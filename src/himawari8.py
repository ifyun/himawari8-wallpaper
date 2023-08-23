import sched
import time

from src.env import ENV, LOG
from src.earth_api import earth

task = sched.scheduler(time.time, time.sleep)


def _execute(inc):
    task.enter(inc, 0, _execute, (inc,))
    try:
        earth.get(ENV.IMAGE_SIZE)
    except Exception as e:
        LOG.error(e)


def run():
    task.enter(0, 0, _execute, (300,))
    task.run()

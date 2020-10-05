import sched
import time

from env import IMAGE_SIZE
from get_earth import get_earth
from logger import log

task = sched.scheduler(time.time, time.sleep)


def execute(inc):
    task.enter(inc, 0, execute, (inc,))
    try:
        get_earth(IMAGE_SIZE)
    except Exception as e:
        log.error(e)


def run():
    task.enter(0, 0, execute, (300,))
    task.run()


if __name__ == "__main__":
    run()

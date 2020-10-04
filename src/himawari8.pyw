import sched, time
import getopt, sys

from get_earth import get_earth

# resolution = (550 * size) ^ 2
size = 4
task = sched.scheduler(time.time, time.sleep)

def execute(inc):
   task.enter(inc, 0, execute, (inc,))
   get_earth(size)

if __name__ == "__main__":
    task.enter(0, 0, execute, (300,))
    task.run()

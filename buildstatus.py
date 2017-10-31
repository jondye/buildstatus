#!python3

import os
import time

from requests.exceptions import ConnectionError
from jenkins import Jenkins
from gpiozero import StatusBoard


def main():
    delay = os.environ.get('POLL_PERIOD', 60)
    server = os.environ['JENKINS_URI']
    status = StatusBoard(pwm=True)
    job_names = [os.environ.get('JENKINS_JOB_%d' % (i+1)) for i in range(5)]
    job_color = [None for _ in job_names]

    while True:
        try:

            j = Jenkins(server)
            for i, name in enumerate(job_names):
                lights = status[i].lights
                if not name:
                    lights.off()
                    continue

                job = j.job(name)
                if not job.enabled:
                    lights.off()
                    continue

                color = job.info['color']
                if color == job_color[i]:
                    continue

                set_status(color, lights)

                job_color = color

            time.sleep(delay)

        except ConnectionError:

            print("Unable to connect")
            display_warning(delay, status)


def set_status(color, lights):
    if color.startswith('blue'):
        lights.red.off()
        if color.endswith('_anime'):
            lights.green.pulse()
        else:
            lights.green.on()
    elif color.startswith('red'):
        lights.green.off()
        if color.endswith('_anime'):
            lights.red.pulse()
        else:
            lights.red.on()
    else:
        lights.on()


def display_warning(delay, status):
    start = time.time()
    while time.time() - start >= delay:
        for s in status:
            status.off()
            s.lights.red.on()
            time.sleep(1)


if __name__ == '__main__':
    main()

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

        except ConnectionError:
            print("Unable to connect")

        time.sleep(delay)


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


if __name__ == '__main__':
    main()

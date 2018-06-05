#!python3

import logging
import os
import time

from requests.exceptions import ConnectionError
from jenkins import Jenkins
from gpiozero import StatusBoard


def main():
    debug = os.environ.get('DEBUG')
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    delay = os.environ.get('POLL_PERIOD', 60)
    default_server = os.environ['JENKINS_URI']
    status = StatusBoard(pwm=True)
    job_names = [os.environ.get('JENKINS_JOB_%d' % (i+1)) for i in range(5)]
    jobs = [
        (default_server, j) for j in job_names
    ]

    job_color = [None for _ in job_names]

    while True:
        for i, (server, name) in enumerate(jobs):
            try:
                logging.info("Polling %s", server)
                j = Jenkins(server)

                lights = status[i].lights
                if not name:
                    lights.off()
                    continue

                color = get_job_color(j, name)
                logging.debug(
                    "Job %s was %s and is now %s",
                    name, job_color[i], color)
                if color == job_color[i]:
                    continue

                set_status(color, lights)
                job_color[i] = color

            except ConnectionError:
                logging.exception("Unable to connect to %s", server)
                job_color[i] = None

        if any(job_color):
            time.sleep(delay)
        else:  # all failed
            display_warning(delay, status)



def get_job_color(j, name):
    try:
        job = j.job(name)
        color = job.info['color']
        logging.debug("Job %s is %s", name, color)
        return color
    except ConnectionError:
        logging.error("Can\'t retrieve info on job %s", name)
        return None


def set_status(color, lights):
    if not color:
        lights.off()
    elif color.startswith('blue'):
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
    while time.time() - start <= delay:
        for s in status:
            status.off()
            s.lights.red.on()
            time.sleep(1)


if __name__ == '__main__':
    main()

#!python3

import logging
import os
import time
from urllib.parse import urlparse

from requests.exceptions import ConnectionError
from jenkins import Jenkins
from gpiozero import StatusBoard
import sshtunnel


def main():
    debug = os.environ.get('DEBUG')
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    delay = int(os.environ.get('POLL_PERIOD', '60'))
    server = os.environ['JENKINS_URI']
    status = StatusBoard(pwm=True)
    job_names = [os.environ.get('JENKINS_JOB_%d' % (i+1)) for i in range(5)]
    job_color = [None for _ in job_names]
    ssh_relay = os.environ.get('SSH_RELAY')
    ssh_user = os.environ.get('SSH_USER')
    ssh_key = os.environ.get('SSH_KEY')

    while True:
        try:
            logging.info("Setting up ssh tunnel via %s@%s", ssh_user, ssh_relay)
            url = urlparse(server)
            host = url.netloc.split(':')[0]
            port = url.port if url.port else 80
            with sshtunnel.open_tunnel(
                    ssh_relay,
                    ssh_username=ssh_user,
                    ssh_pkey=ssh_key,
                    remote_bind_address=(host, port),
                    local_bind_address=('localhost', 12345)):

                poll_server(
                        url._replace(netloc='localhost:12345').geturl(),
                        status,
                        job_names,
                        job_color)
                time.sleep(delay)

        except ConnectionError:
            logging.exception("Unable to connect")
            display_warning(delay, status)
            job_color = [None for _ in job_names]


def poll_server(server, status, job_names, job_color):
    j = Jenkins(server)
    for i, name in enumerate(job_names):
        lights = status[i].lights
        if not name:
            lights.off()
            continue

        color = get_job_color(j, name)
        logging.info(
            "Job %s was %s and is now %s",
            name, job_color[i], color)
        if color == job_color[i]:
            continue

        set_status(color, lights)
        job_color[i] = color


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

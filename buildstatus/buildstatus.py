#!python3

import logging
import os
import time

from requests.exceptions import ConnectionError
from jenkins import Jenkins
from gpiozero import StatusBoard


class JenkinsJobStatus(object):
    def __init__(self, server_uri, job_name):
        self.server_uri = server_uri
        self.job_name = job_name
        self.color = None

    def update(self):
        logging.info("Polling %s", self.server_uri)
        try:
            color = get_job_color(
                Jenkins(self.server_uri),
                self.job_name)
            logging.debug(
                "JenkinsJob %s was %s and is now %s",
                self.job_name, self.color, color)
            self.color = color
        except ConnectionError:
            logging.exception("Unable to connect")
            self.color = None

    def set_light(self, light):
        set_status(self.color, light)


class BlankStatus(object):
    def update(self):
        pass

    def set_light(self, light):
        light.off()


def main():
    debug = os.environ.get('DEBUG')
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    delay = os.environ.get('POLL_PERIOD', 60)
    server = os.environ['JENKINS_URI']
    status = StatusBoard(pwm=True)
    job_names = [os.environ.get('JENKINS_JOB_%d' % (i+1)) for i in range(5)]
    pollers = [
            JenkinsJob(server, job_name) if name else BlankStatus()
            for name in job_names]

    while True:
        for i, poller in enumerate(pollers):
            poller.update()
            poller.set_light(status[i].lights)
        time.sleep(delay)


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


if __name__ == '__main__':
    main()

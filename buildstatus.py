#!python3

import logging
import os
import time

from requests.exceptions import ConnectionError
import jenkins
import gpiozero


def main():
    debug = os.environ.get('DEBUG')
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    delay = os.environ.get('POLL_PERIOD', 60)
    server = os.environ['JENKINS_URI']
    job_names = [os.environ.get('JENKINS_JOB_%d' % (i+1)) for i in range(5)]

    board = StatusBoard(server, job_names)
    while True:
        board.update()
        time.sleep(delay)


class StatusBoard(object):
    def __init__(self, server, job_names):
        self.server = server
        self.job_names = job_names
        self.status = gpiozero.StatusBoard(pwm=True)
        self.job_color = [None for _ in job_names]

    def update(self):
        try:
            logging.info("Polling %s", self.server)
            j = jenkins.Jenkins(self.server)
            for i, name in enumerate(self.job_names):
                lights = self.status[i].lights
                if not name:
                    lights.off()
                    continue

                color = get_job_color(j, name)
                logging.debug(
                    "Job %s was %s and is now %s",
                    name, self.job_color[i], color)
                if color == self.job_color[i]:
                    continue

                set_status(color, lights)
                self.job_color[i] = color

        except ConnectionError:
            logging.exception("Unable to connect")
            self.display_warning()
            self.job_color = [None for _ in self.job_names]

    def display_warning(self):
        start = time.time()
        while time.time() - start <= 10:
            for s in self.status:
                self.status.off()
                s.lights.red.on()
                time.sleep(1)


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

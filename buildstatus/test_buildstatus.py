import sys
from unittest.mock import MagicMock, patch
import unittest

sys.modules['gpiozero'] = MagicMock()

import buildstatus

@patch('buildstatus.Jenkins')
class TestJenkinsJobStatus(unittest.TestCase):
    def test_update_polls_uri(self, Jenkins):
            jenkins = Jenkins.return_value
            status = buildstatus.JenkinsJobStatus("http://jenkins.com/", "my_job")

            status.update()

            Jenkins.assert_called_with('http://jenkins.com/')
            jenkins.job.assert_called_with("my_job")

    def test_color_is_retrieved_from_job_info(self, Jenkins):
        self.assertTrue(False)

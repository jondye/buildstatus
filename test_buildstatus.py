import unittest
from unittest.mock import Mock, patch
import sys

sys.modules['gpiozero'] = Mock()
import buildstatus

class MyFirstTest(unittest.TestCase):
    @patch("jenkins.Jenkins")
    def test_something(self, jenkins):
        board = buildstatus.StatusBoard("", [])

        board.update()

        jenkins.assert_not_called()
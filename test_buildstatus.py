import unittest
from unittest.mock import Mock
import sys

sys.modules['gpiozero'] = Mock()
import buildstatus

class MyFirstTest(unittest.TestCase):
    def test_failure(self):
        pass


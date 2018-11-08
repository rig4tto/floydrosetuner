import unittest
import coverage
import sys
import os

sys.path.insert(0, os.path.abspath("tst"))
sys.path.insert(0, os.path.abspath("src"))

cov = coverage.Coverage()
cov.start()

loader = unittest.TestLoader()
suite = loader.discover("tst")
runner = unittest.TextTestRunner()
runner.run(suite)

cov.stop()
cov.save()
cov.html_report()

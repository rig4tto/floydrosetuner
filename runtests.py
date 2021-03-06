# Floyd Rose Tuner
# Copyright (C) 2018  Daniele Rigato
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import coverage
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)

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

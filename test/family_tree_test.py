#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import unittest

# Add the repo root to the beginning of the Python module path.
# Even if the user has installed family_tree locally, the version
# next to the test file will be used.
sys.path = [os.path.join(os.path.dirname(__file__), '..')] + sys.path

from source import family_tree as ft

class FamilyTreeTest(unittest.TestCase):
  def testSample(self):
    family = ft.Family()

if __name__ == '__main__':
  unittest.main()
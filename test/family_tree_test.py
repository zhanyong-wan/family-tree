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

  def setUp(self):
    self.family = ft.Family()

  def testMakeEmptyFamily(self):
    self.assertEqual(0, self.family.Size())

  def testAddOnePerson(self):
    self.family.Person('John Smith')
    self.assertEqual(1, self.family.Size())

  def testAddOnePersonWithGender(self):
    p = self.family.Person('John Smith', gender='M')
    self.assertEqual('M', p.Gender())

  def testAddOnePersonWithAttributes(self):
    p = self.family.Person('John Smith', birth='1942', death='?')
    self.assertIsNone(p.Gender())  # Gender is unknown yet.
    self.assertEqual('1942', p.Birth())
    self.assertIsNone(p.Death())
    self.assertTrue(p.Deceased())  # We know he's deceased as the death is '?'.
    self.assertEqual(1, self.family.Size())

  def testAddPersonWithWife(self):
    p = self.family.Person('John Smith', wife='Ada Smith')
    self.assertEqual('M', p.Gender())  # Inferred.
    q = self.family.Person('Ada Smith')
    self.assertEqual('F', q.Gender())  # Inferred.

    wives = p.Wives()
    self.assertEqual(1, len(wives))
    self.assertEqual(q, wives[0])
    self.assertEqual(0, len(p.Husbands()))

    husbands = q.Husbands()
    self.assertEqual(1, len(husbands))
    self.assertEqual(p, husbands[0])
    self.assertEqual(0, len(q.Wives()))

    self.assertEqual(2, self.family.Size())

  def testAddPersonWithTwoWives(self):
    p = self.family.Person('John Smith', wife=('Ada Smith', 'Katty Lam'))
    self.assertEqual('M', p.Gender())  # Inferred.
    q = self.family.Person('Ada Smith')
    self.assertEqual('F', q.Gender())  # Inferred.
    r = self.family.Person('Katty Lam')
    self.assertEqual('F', q.Gender())  # Inferred.

    wives = p.Wives()
    self.assertEqual(2, len(wives))
    self.assertEqual(q, wives[0])
    self.assertEqual(r, wives[1])
    self.assertEqual(0, len(p.Husbands()))

    husbands = q.Husbands()
    self.assertEqual(1, len(husbands))
    self.assertEqual(p, husbands[0])
    self.assertEqual(0, len(q.Wives()))

    husbands = r.Husbands()
    self.assertEqual(1, len(husbands))
    self.assertEqual(p, husbands[0])
    self.assertEqual(0, len(r.Wives()))

    self.assertEqual(3, self.family.Size())

  def testAddPersonWithHusband(self):
    q = self.family.Person('Ada Smith', husband='John Smith')
    self.assertEqual('F', q.Gender())  # Inferred.
    p = self.family.Person('John Smith')
    self.assertEqual('M', p.Gender())  # Inferred.

    wives = p.Wives()
    self.assertEqual(1, len(wives))
    self.assertEqual(q, wives[0])
    self.assertEqual(0, len(p.Husbands()))

    husbands = q.Husbands()
    self.assertEqual(1, len(husbands))
    self.assertEqual(p, husbands[0])
    self.assertEqual(0, len(q.Wives()))

    self.assertEqual(2, self.family.Size())

  def testAddPersonWithTwoHusbands(self):
    p = self.family.Person('Ada Smith', husband=('John Smith', 'Mike Jin'))
    self.assertEqual('F', p.Gender())  # Inferred.
    q = self.family.Person('John Smith')
    self.assertEqual('M', q.Gender())  # Inferred.
    r = self.family.Person('Mike Jin')
    self.assertEqual('M', q.Gender())  # Inferred.

    husbands = p.Husbands()
    self.assertEqual(2, len(husbands))
    self.assertEqual(q, husbands[0])
    self.assertEqual(r, husbands[1])
    self.assertEqual(0, len(p.Wives()))

    wives = q.Wives()
    self.assertEqual(1, len(wives))
    self.assertEqual(p, wives[0])
    self.assertEqual(0, len(q.Husbands()))

    wives = r.Wives()
    self.assertEqual(1, len(wives))
    self.assertEqual(p, wives[0])
    self.assertEqual(0, len(r.Husbands()))

    self.assertEqual(3, self.family.Size())

  def testAddPersonWithFather(self):
    p = self.family.Person('John Smith', father='Adam Smith')
    q = self.family.Person('Adam Smith')

    self.assertEqual(q, p.Father())
    self.assertIsNone(p.Mother())
    self.assertEqual(0, len(p.Children()))

    self.assertEqual('M', q.Gender())
    self.assertIsNone(q.Father())
    self.assertIsNone(q.Mother())
    children = q.Children()
    self.assertEqual(1, len(children))
    self.assertEqual(p, children[0])

    self.assertEqual(2, self.family.Size())

  def testAddPersonWithMother(self):
    p = self.family.Person('John Smith', mother='Alice Smith')
    q = self.family.Person('Alice Smith')

    self.assertEqual(q, p.Mother())
    self.assertIsNone(p.Father())
    self.assertEqual(0, len(p.Children()))

    self.assertEqual('F', q.Gender())
    self.assertIsNone(q.Father())
    self.assertIsNone(q.Mother())
    children = q.Children()
    self.assertEqual(1, len(children))
    self.assertEqual(p, children[0])

    self.assertEqual(2, self.family.Size())

if __name__ == '__main__':
  unittest.main()
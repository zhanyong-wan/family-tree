# -*- coding: utf-8 -*-

"""Libraries for generating nice-looking family tree illustration via
graphviz (dot).
"""

__author__ = 'Zhanyong Wan'

from typing import Optional, Text

def _GetDefaultIdFromName(name: Text) -> Text:
  """Gets a person's default ID from their name."""

  return name.replace(' ', '')

class Person:
  """Represents a person."""

  def __init__(self, name: Text, id: Optional[Text]=None):
    self.name = name
    self.id = id if id else _GetDefaultIdFromName(name)


class Family:
  """Represents a family of people."""

  def __init__(self):
    self.people = {}  # Maps ID to person.

  def Add(self, person) -> 'Family':
    self.people[person.ID()] = person
    return self
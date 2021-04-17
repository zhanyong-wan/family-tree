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

  def __init__(self, name: Text,
               id: Optional[Text]=None,
               gender: Optional[Text]=None,
               birth: Optional[Text]=None,
               death: Optional[Text]=None):
    self.name = name
    self.id = id if id else _GetDefaultIdFromName(name)
    self.gender = 'M' if (gender and gender=='M') else 'F'
    self.birth = birth
    self.death = death

  def ID(self) -> Text:
    return self.id

  def Male(self) -> bool:
    return self.gender == 'M'

  def Deceased(self) -> bool:
    return self.death

  def ToDot(self) -> Text:
    attribs = []
    label = self.name
    if self.birth or self.death:
      label += r'\n'
      if self.birth:
        label += self.birth
      label += '-'
      if self.death:
        label += self.death
    attribs.append(f'label="{label}"')
    if self.Deceased():
      if self.Male():
        attribs.append('style="bold"')
      else:
        attribs.append('style="bold,rounded"')
    elif self.Male():
      attribs.append('style="filled"')
      attribs.append('fillcolor="lightblue"')
    else:  # Female
      attribs.append('style="filled,rounded"')
      attribs.append('fillcolor="pink"')
    
    dot = f'{self.id} [{" ".join(attribs)}];'
    return dot

class Family:
  """Represents a family of people."""

  def __init__(self):
    self.people = {}  # Maps ID to person.
    self.ids = []  # Person IDs, in the order they are first added.

  def Add(self, name: Text,
          id: Optional[Text]=None,
          gender: Optional[Text]=None,
          birth: Optional[Text]=None,
          death: Optional[Text]=None) -> 'Family':
    person = Person(name=name, id=id, gender=gender, birth=birth, death=death)
    self.people[person.ID()] = person
    if person.ID() not in self.ids:
      self.ids.append(person.ID())
    return self

  def ToDot(self) -> Text:
    dot = []
    dot.append("""digraph G {
    rankdir=LR;
    node [shape=box fontname="Kai"];
    edge [dir=none];
""")
    for id in self.ids:
      p = self.people[id]
      dot.append('\t' + p.ToDot())
    dot.append('}')
    return '\n'.join(dot)
# -*- coding: utf-8 -*-

"""Libraries for generating nice-looking family tree illustration via
graphviz (dot).
"""

__author__ = 'Zhanyong Wan'

from typing import Optional, Sequence, Text

def _GetDefaultIdFromName(name: Text) -> Text:
  """Gets a person's default ID from their name."""

  return name.replace(' ', '')

class Person:
  """Represents a person."""

  def __init__(self, family: 'Family', name: Text):
    self.family = family
    self.name = name
    self.id = _GetDefaultIdFromName(name)
    self.gender = None
    self.wife_ids = []  # IDs of wives.
    self.husband_ids = []  # IDs of husbands.
    self.father = None
    self.mother = None
    self.children = []
    self.birth = None
    self.death = None

  def Family(self) -> 'Family':
    return self.family

  def AddWife(self, wife: 'Person') -> 'Person':
    self.SetGender('M')
    wife_id = wife.ID()
    if wife_id not in self.wife_ids:
      self.wife_ids.append(wife_id)
      wife.AddHusband(self)
    return self

  def AddHusband(self, husband: 'Person') -> 'Person':
    self.SetGender('F')
    husband_id = husband.ID()
    if husband_id not in self.husband_ids:
      self.husband_ids.append(husband_id)
      husband.AddWife(self)
    return self

  def SetFather(self, father: 'Person') -> 'Person':
    if self.father != father:
      father.SetGender('M')
      self.father = father
      father.AddChild(self)
    return self

  def Father(self) -> 'Person':
    return self.father

  def Mother(self) -> 'Person':
    return self.mother

  def AddChild(self, child: 'Person') -> 'Person':
    id = child.ID()
    for c in self.children:
      if c.ID() == id:
        return self
    self.children.append(child)
    if self.Gender() == 'M':
      child.SetFather(self)
    elif self.Gender() == 'F':
      child.SetMonther(self)
    return self

  def Children(self) -> Sequence['Person']:
    return self.children

  def Update(self, **args) -> 'Person':
    for name, value in args.items():
      if name == 'name':
        self.name = value
      elif name == 'gender':
        self.gender = value
      elif name == 'birth':
        self.birth = value
      elif name == 'death':
        self.death = value
      elif name == 'wife':
        # The 'wife' attribute can be either a string or a tuple of strings.
        if not isinstance(value, tuple):
          value = (value,)

        for wife_name in value:
          wife_id = _GetDefaultIdFromName(wife_name)
          wife = self.Family().PersonById(wife_id)
          self.AddWife(wife)
      elif name == 'husband':
        # The 'husband' attribute can be either a string or a tuple of strings.
        if not isinstance(value, tuple):
          value = (value,)

        for husband_name in value:
          husband_id = _GetDefaultIdFromName(husband_name)
          husband = self.Family().PersonById(husband_id)
          self.AddHusband(husband)
      elif name == 'father':
        father = self.Family().Person(name=value)
        self.SetFather(father)
      else:
        raise ValueError(f'Invalid person attribute "{name}".')
    return self

  def ID(self) -> Text:
    return self.id

  def Wives(self) -> Sequence['Person']:
    if not self.wife_ids:
      return []
    return [self.Family().PersonById(wife_id) for wife_id in self.wife_ids]

  def Husbands(self) -> Sequence['Person']:
    if not self.husband_ids:
      return []
    return [self.Family().PersonById(husband_id) for husband_id in self.husband_ids]

  def SetGender(self, gender : Text) -> 'Person':
    self.gender = gender
    return self

  def Gender(self) -> Text:
    return self.gender

  def Birth(self) -> Text:
    if self.birth and self.birth != '?':
      return self.birth
    return None

  def Death(self) -> Text:
    if self.death and self.death != '?':
      return self.death
    return None

  def Deceased(self) -> bool:
    return self.death

  def ToDot(self) -> Text:
    attribs = []
    label = self.name
    birth = self.Birth()
    death = self.Death()
    if birth or death:
      label += r'\n'
      if birth:
        label += birth
      label += '-'
      if death:
        label += death
    attribs.append(f'label="{label}"')
    if self.Deceased():
      if self.Gender() == 'M':
        attribs.append('style="bold"')
      else:
        attribs.append('style="bold,rounded"')
    elif self.Gender() == 'M':
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

  def Size(self) -> int:
    return len(self.ids)

  def Person(self, name: Text, **attribs) -> Person:
    global Person  # Allow referencing the outer name.
    id = _GetDefaultIdFromName(name)
    if id not in self.people:
      person = Person(self, name)
      self.people[id] = person
      self.ids.append(id)
    else:
      person = self.people[id]
    person.Update(name=name).Update(**attribs)
    return person

  def PersonById(self, id: Text) -> Person:
    return self.Person(name=id)

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
# -*- coding: utf-8 -*-

"""Libraries for generating nice-looking family tree illustration via
graphviz (dot).
"""

__author__ = 'Zhanyong Wan'

from typing import List, Optional, Sequence, Text, Tuple

def _GetDefaultIdFromName(name: Text) -> Text:
  """Gets a person's default ID from their name."""

  return name.replace(' ', '')

class Person:
  """Represents a person."""

  def __init__(self, family: 'Family', name: Text):
    self.family = family
    self.generation = None
    self.order_added = None
    self.name = name
    self.id = _GetDefaultIdFromName(name)
    self.annotation = None
    self.gender = None
    self.wives = []
    self.husbands = []
    self.father = None
    self.mother = None
    self.children = []
    self.birth = None
    self.death = None

  def Family(self) -> 'Family':
    return self.family

  def Generation(self) -> int:
    return self.generation

  def AddWife(self, wife: 'Person') -> 'Person':
    for w in self.wives:
      if w == wife:
        return self
    self.SetGender('M')
    self.wives.append(wife)
    wife.AddHusband(self)
    return self

  def AddHusband(self, husband: 'Person') -> 'Person':
    for h in self.husbands:
      if h == husband:
        return self
    self.SetGender('F')
    self.husbands.append(husband)
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

  def SetMother(self, mother: 'Person') -> 'Person':
    if self.mother != mother:
      mother.SetGender('F')
      self.mother = mother
      mother.AddChild(self)
    return self

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
      child.SetMother(self)
    return self

  def Children(self) -> Sequence['Person']:
    return self.children

  def Update(self, **args) -> 'Person':
    for name, value in args.items():
      if name == 'name':
        self.name = value
      elif name == 'annotation':
        self.annotation = value
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
          wife = self.Family().PersonByName(name=wife_name)
          self.AddWife(wife)
      elif name == 'husband':
        # The 'husband' attribute can be either a string or a tuple of strings.
        if not isinstance(value, tuple):
          value = (value,)

        for husband_name in value:
          husband = self.Family().PersonByName(name=husband_name)
          self.AddHusband(husband)
      elif name == 'father':
        father = self.Family().PersonByName(name=value)
        self.SetFather(father)
      elif name == 'mother':
        mother = self.Family().PersonByName(name=value)
        self.SetMother(mother)
      else:
        raise ValueError(f'Invalid person attribute "{name}".')
    return self

  def ID(self) -> Text:
    return self.id

  def Name(self) -> Text:
    return self.name

  def Wives(self) -> Sequence['Person']:
    return self.wives

  def Husbands(self) -> Sequence['Person']:
    return self.husbands

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

  def PropagateGeneration(self, my_generation: int) -> 'Person':
    if self.generation is not None:
      assert self.generation == my_generation
      return self

    self.generation = my_generation
    if self.Father():
      self.Father().PropagateGeneration(my_generation - 1)
    if self.Mother():
      self.Mother().PropagateGeneration(my_generation - 1)
    for husband in self.Husbands():
      husband.PropagateGeneration(my_generation)
    for wife in self.Wives():
      wife.PropagateGeneration(my_generation)
    for child in self.Children():
      child.PropagateGeneration(my_generation + 1)
    return self

  def ToDot(self) -> Text:
    attribs = []
    label = self.name
    if self.annotation:
      label += f' ({self.annotation})'
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
    self.id_to_person = {}  # Maps ID to person.
    self.people = []  # People in the order they are first added.

  def Size(self) -> int:
    return len(self.people)

  def Person(self, name: Text, **attribs) -> 'Person':
    """Returns the person with the given name.
    
    Also sets the person's display name to `name`.
    """

    global Person  # Allow referencing the outer name.
    id = _GetDefaultIdFromName(name)
    if id not in self.id_to_person:
      person = Person(self, name)
      self.id_to_person[id] = person
      self.people.append(person)
    else:
      person = self.id_to_person[id]
    person.Update(name=name).Update(**attribs)
    return person

  def PersonByName(self, name: Text) -> Person:
    """Returns the person with the given name, which may or may not contain spaces.

    Unlike Person(name), this will not affect the person's display name.    
    """

    id = _GetDefaultIdFromName(name)
    if id in self.id_to_person:
      return self.id_to_person[id]
    return self.Person(name=name)

  def Sort(self) -> List[List[Person]]:
    """Sorts the people by generation; within the same generation,
    sort by the order they are added.

    Each element in the return value is a list of people in the same generation.
    """

    if not self.people:
      return [[]]

    for i, p in enumerate(self.people):
      p.generation = None
      p.order_added = i

    for p in self.people:
      if p.generation is None:
        p.PropagateGeneration(1)

    max_generation = max(p.generation for p in self.people)
    min_generation = min(p.generation for p in self.people)
    num_generations = max_generation - min_generation + 1
    for p in self.people:
      p.generation -= min_generation

    generations = [[] for i in range(num_generations)]
    for p in self.people:
      generations[p.Generation()].append(p)
    
    def GetRankInGeneration(p: Person) -> Tuple[int, int]:
      """Returns the rank of the person within the same generation."""

      # A male is ranked by the order he was added.
      if p.Gender() == 'M':
        return (p.order_added, 0)

      # Now we know p is a female.

      # If p has not had a husband, she's ranked by the order she was added.
      husbands = p.Husbands()
      if not husbands:
        return (p.order_added, 0)

      # p has had at least one husband.  She should be after her highest-ranked
      # husband.
      max_husband_rank = max(h.order_added for h in husbands)
      for h in husbands:
        if h.order_added == max_husband_rank:
          # In case this husband has N wives, the wives should be ranked by the
          # order they were married.
          for i, w in enumerate(h.Wives()):
            if w == p:
              return (max_husband_rank, i + 1)

    for gen in generations:
      gen.sort(key=GetRankInGeneration)

    return generations

  def ToDot(self) -> Text:
    dot = []
    dot.append("""digraph G {
    rankdir=LR;
    node [shape=box fontname="Kai"];
    edge [dir=none];
    graph [splines="line"];
""")

    for i, gen in enumerate(self.Sort()):
      gen_num = i + 1
      dot.append('\t################')
      dot.append(f'\t# Generation {gen_num}.')

      dot.append('')
      dot.append(f'\t# People in generation {gen_num}.')
      for p in gen:
        dot.append('\t' + p.ToDot())

      # Each item is a (marriage ID, child ID list).
      marriage_to_children = []
      def GetChildren(marrage_id: Text) -> List[Text]:
        for id, children in marriage_to_children:
          if id == marriage_id:
            return children
        children = []
        marriage_to_children.append((marriage_id, children))
        return children

      for p in gen:
        if p.Father() and p.Mother():
          marriage_id = f'm_{p.Father().ID()}_{p.Mother().ID()}'
          GetChildren(marriage_id).append(p.ID())

      dot.append('')
      dot.append(f'\t# Parents of generation {gen_num}.')
      for marriage_id, children in marriage_to_children:
        if len(children) == 1:
          dot.append(f'\t{marriage_id} -> {children[0]} [weight=10];')
        else:
          for child in children:
            # Define the elbow point.
            dot.append(f'\tp_{child} [shape=circle label="" height=0.01 width=0.01];')
          middle_child = children[(len(children) -1) // 2]
          dot.append(f'\t{marriage_id} -> p_{middle_child} [weight=10];')
          for child in children:
            dot.append(f'\tp_{child} -> {child} [weight=10];')

      dot.append('')
      dot.append(f'\t# Order the parent elbow points for generation {gen_num}.')
      dot.append('\t{')
      dot.append('\t\trank=same;')
      last_p_node = None
      for marriage_id, children in marriage_to_children:
        if len(children) == 1:
          continue
        if last_p_node:
          dot.append(f'\t\t{last_p_node} -> p_{children[0]} [style="invis"];')
        chain = ' -> '.join(f'p_{child}' for child in children)
        dot.append(f'\t\t{chain};')
        last_p_node = f'p_{children[-1]}'
      dot.append('\t}')

      dot.append('')
      dot.append(f'\t# Order the people in generation {gen_num}.')
      for p in gen:
        if len(p.Wives()) > 1:
          # Add extra elbow points to account for multiple wives of the same person.
          elbows = []
          dot.append(f'\tu_{p.ID()} [shape=circle label="" height=0.01 width=0.01];')
          dot.append(f'\tu_{p.ID()} -> {p.ID()} [weight=10];')
          elbows = [f'u_{p.ID()}']
          for w in p.Wives()[1:]:
            dot.append(f'\tu_{w.ID()} [shape=circle label="" height=0.01 width=0.01];')
            dot.append(f'\tu_{w.ID()} -> m_{p.ID()}_{w.ID()} [weight=10];')
            elbows.append(f'u_{w.ID()}')
          dot.append('\t{')
          dot.append('\t\trank=same;')
          dot.append('\t\t' + ' -> '.join(elbows) + ';')
          dot.append('\t}')

      dot.append('\t{')
      dot.append('\t\trank=same;')
      last_person = None
      last_male = None
      for p in gen:
        marriage_id = None
        if last_male:
          wives = last_male.Wives()
          if p in wives:
            k = wives.index(p)
            marriage_id = f'm_{last_male.ID()}_{p.ID()}'
            dot.append(f'\t\t{marriage_id} [shape="diamond" label="" height=0.25 width=0.25];')
            if k == 0:
              dot.append(f'\t\t{last_male.ID()} -> {marriage_id} -> {p.ID()} [weight=10];')
            else:
              dot.append(f'\t\t{marriage_id} -> {p.ID()} [weight=10];')
        if last_person:
          if p not in last_person.Wives():
            id = marriage_id if marriage_id else p.ID()
            dot.append(f'\t\t{last_person.ID()} -> {id} [style="invis"];')
        last_person = p
        if p.Gender() == 'M':
          last_male = p
      dot.append('\t}')
      dot.append('')

    dot.append('}')
    return '\n'.join(dot)
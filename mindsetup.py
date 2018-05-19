import parsimonious

grammar = parsimonious.grammar.Grammar('''
    expression = binary / unary / parens / setx / set / label
    
    program = expression _
    input = set _
    
    intermediate = unary / parens / setx / set / label
    clean = parens / setx / set / label
    set = number / fullset
    fullset = _ "{" set? ( _ "," set )* _ "}"
    setx = _ "{" expression? ( _ "," expression )* _ "}"
    number = _ ~"[0-9]+"
    parens = _ "(" expression ")"
    op = ~"[+*$^<\\[=#?-]"
    label = _ ~"[A-Za-z]+"
    
    unary = clean (complex / simple)+
    simple = _ &~"[+*$^-]" op !expression
    complex = _ &~"[#?]" op label ":" parens
    
    binary = intermediate tail+
    tail = _ &~"[+*<\\[=-]" op intermediate
    
    _ = ~"[ \\t\\n\\r]*"
  ''')

class coolset(frozenset):
  expressive = True
  numeral = None
  nums = []
  
  def __init__(self, iterable=()):
    super().__init__()
    self.expressive = not all(
      map(lambda e: type(e) is coolset and not e.expressive, self))
    try:
      n = len(self)
      if n < len(coolset.nums):
        #self.numeral = n
        if self == coolset.nums[n]:
          self.numeral = n
      elif sorted([val.numeral for val in self]) == list(range(n)):
        self.numeral = n
    except NameError:
      pass

  def __repr__(self):
    '''
    Hacky way to make sets display nicely
    Rewrites __repr__ instead of __str__ because __repr__ is
    still used for inner frozensets when __str__ is called
    '''
    if len(self) == 0:
      return '0'
    if self.numeral is not None:
      return str(self.numeral)
    else:
      return repr(set(self))  #.replace("'","")

  def __eq__(self, value):
    if self.numeral is not None and type(value) is coolset and value.numeral is not None:
      return self.numeral == value.numeral
    else:
      return frozenset.__eq__(self, value)

  __hash__ = frozenset.__hash__

  def difference(self, iterable):
    if type(self) is tuple or type(iterable) is tuple:
      return coolset()
    return coolset(super().difference(iterable))

  def intersection(self, iterable):
    if type(self) is tuple or type(iterable) is tuple:
      return coolset()
    return coolset(super().intersection(iterable))

  def symmetric_difference(self, iterable):
    if type(self) is tuple or type(iterable) is tuple:
      return coolset()
    return coolset(super().symmetric_difference(iterable))

  def union(self, iterable):
    if type(self) is tuple or type(iterable) is tuple:
      return coolset()
    return coolset(super().union(iterable))
  
for n in range(256):
  coolset.nums.append(coolset(coolset.nums))
  coolset.nums[-1].numeral = n

class MindSet:
  program = None
  universe = None
  result = None
  unary = {}
  binary = {}

  def __init__(self, program, universe=None):
    
    if type(program) is str:
      program = parser.visit(grammar['program'].parse(program))
    self.program = program
    
    if universe is None:
      self.universe = coolset({coolset({coolset()})})
    else:
      if type(universe) is str:
        universe = parser.visit(grammar['input'].parse(universe))
      self.universe = coolset({coolset({coolset()}), coolset({coolset(), self.value(universe)})})
    
    self.binary = {
      "+": lambda a, b: a.union(b),
      "*": lambda a, b: a.intersection(b),
      "-": lambda a, b: a.difference(b),
      "<": lambda a, b: self.universe if a.issubset(b) else coolset(),
      "[": lambda a, b: self.universe if a in b else coolset(),
      "=": lambda a, b: self.universe if a == b else coolset(),
    }
    
    self.unary = {
      "+": lambda a: MindSet.reduce(coolset.union, a),
      "*": lambda a: MindSet.reduce(coolset.intersection, a),
      "-": self.symmetricmultidifference,
      "$": lambda a: self.value(len(a)),
      "^": self.powerset,
      "#": self.mapset,
      "?": self.filterset
    }

  def value(self, val, labels=None, expressive=True):
    if labels is None: labels = {"U": self.universe}
    value = lambda v: self.value(v, labels, expressive)
    t = type(val)
    if t is coolset and not val.expressive:
      return val
    elif t is coolset or t is frozenset or t is set:
      return coolset(map(value, val))
    elif t is tuple:

      op = val[0]
      args = val[1:]

      if not expressive and op[0] != '!':
        return tuple(map(value, val))

      if op[0] == '!': op = op[1]

      if len(args) == 1:
        return self.unary[op](value(*args))
      elif len(args) == 2:
        return self.binary[op](*map(value, args))
      elif len(args) == 3:
        return self.unary[op](*args, labels, expressive)
      else:
        raise Exception("ERROR: Malformed operator: {}; expected tuple of length 2, 3, or 4".format(val))
    elif t is str:
      if not expressive and val not in labels:
        return val
      else: return labels[val]
    else:
      raise Exception("ERROR: Unknown construct: {} of type {}; expected set, int, tuple (operator expression) or string (label)".format(val, t))

  @classmethod
  def reduce(cls, f, aset):
    if aset == coolset():
      return aset
    aset = set(aset)
    val = aset.pop()
    while aset:
      val = f(val, aset.pop())
    return coolset(val)

  def symmetricmultidifference(self, aset):
    inset  = set()
    outset = set()
    for anelem in aset:
      outset.update(inset.intersection(anelem))
      inset.update(anelem)
      inset.difference_update(outset)
    return coolset(inset)
      
  def powerset(self, aset):
    if len(aset) > 32:
      print("You played yourself")
    workset = set(frozenset())
    for anelem in aset:
      newset = set()
      for workelem in workset:
        newset.add(workelem.union({anelem}))
      workset.update(newset)
    return coolset(workset)
  
  def mapset(self, aset, label, expr, labels, expressive):
    return coolset(map(lambda val: self.value(expr, {**labels, label:val}, expressive), aset))
  
  def filterset(self, aset, label, expr, labels, expressive):
    return coolset(filter(lambda val: self.value(expr, dict(labels, **{label:val}), expressive), aset))
  
  def step(self, log = False):
    # What we're supposed to do is set the univese to `<program>?line:(line**=U**)--`
    # in other words,
    # self.universe = self.value(('-', ('-', ('?', self.program, 'line', ('=', ('*', ('*', 'line')), ('*', ('*', 'U')))))))
    # but that would take FOREVER since we'd have to evaluate every line every time
    # so we cheat

    # unless...WE DON'T

    # lookingindex = None
    # lookingline = None
    # doingindex = self.value(('*', 'U'))
    # if log:
    #   print('Running line {}'.format(*doingindex))
    # doingline = None
    # for line in self.program:
    #   if len(line) == 2:
    #     for anelem in line:
    #       if len(anelem) == 2:
    #         wrappedlookingline = anelem
    #       if len(anelem) == 1:
    #         lookingindex = anelem
    #     for maybeline in wrappedlookingline:
    #       if maybeline not in lookingindex:
    #         lookingline = maybeline
    #   else:
    #     for doubleduty in line:
    #       lookingindex = doubleduty
    #       for anelem in doubleduty:
    #         lookingline = anelem
    #   if self.value(lookingindex) == doingindex:
    #     doingline = lookingline
    #     self.universe = self.value(doingline)
    #     if log:
    #       print('Result: {}'.format(self.universe))
    #     break
    # if doingline is None:
    #   print("No such line found.")
    # return doingline

    lineindex = self.value(('*', ('*', 'U')))
    if log: 
      print('\nRunning line {}'.format(lineindex))
    newniverse = self.value(('!-',('!-',('!-',('!?',self.program,'line',('!=',('!*',('!*','line')), lineindex))))), expressive=False) 
    if newniverse != coolset():
      self.universe = self.value(newniverse)
      if log:
        print('EXPR: {}'.format(newniverse))
        print('RSLT: {}'.format(self.universe))
    elif log:
      print("No such line found.\n\nFINAL RESULT:")
    return newniverse
    
  def run(self, log=False, step=False):
    haltwhennone = True
    while haltwhennone != coolset():
      haltwhennone = self.step(log)
      if step: input()
    self.result = self.value(("-", ("-", self.universe)))

class MindParser(parsimonious.nodes.NodeVisitor):

  grammar = grammar
  log = True

  def generic_visit(self, node, children):
    children = list(filter(lambda e: e != None, children))
    if len(children) == 0:
      return None
    if len(children) == 1:
      return children[0]
    else:
      return children

  def visit_fullset(self, node, children):
    children = list(filter(lambda e: e != None, children))
    if len(children) < 2 or (type(children[1]) is not list):
      return coolset(children)
    else:
      return coolset(children[:1] + children[1])

  def visit_setx(self, node, children):
    children = list(filter(lambda e: e != None, children))
    if len(children) < 2 or (type(children[1]) is not list):
      return coolset(children)
    else:
      return coolset(children[:1] + children[1])

  def visit_number(self, node, children):
    val = int(node.text)
    if val < len(coolset.nums):
      return coolset.nums[val]
    result = coolset(coolset.nums)
    for i in range(val - len(coolset.nums)):
      result = result.union({result})
    return result

  def visit_unary(self, node, children):
    arg = children[0]
    if type(children[1]) is list:
      for opifier in children[1]:
        arg = opifier(arg)
      return arg
    else:
      return children[1](arg)

  def visit_simple(self, node, children):
    return lambda arg: (children[2], arg)

  def visit_complex(self, node, children):
    _, _, op, label, _, expr = children
    return lambda arg: (op, arg, label, expr)

  def visit_binary(self, node, children):
    arg = children[0]
    if type(children[1]) is list:
      for opifier in children[1]:
        arg = opifier(arg)
      return arg
    else:
      return children[1](arg)

  def visit_tail(self, node, children):
    _, _, op, expr = children
    return lambda arg: (op, arg, expr)

  def visit_label(self, node, children):
    return node.children[1].text

  def visit_op(self, node, children):
    return node.text

  def visit_parens(self, node, children):
    return children[2]

parser = MindParser()
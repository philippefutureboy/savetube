def noop (*x, **y):
  pass

def validate_callable(fn, error_message):
  if not callable(fn):
      raise TypeError(error_message)

def ifElse(condition, ifAction, elseAction = noop):
  validate_callable(condition, "TypeError: condition argument should be callable")
  validate_callable(ifAction, "TypeError: ifAction argument should be callable")
  validate_callable(elseAction, "TypeError: elseAction argument should be callable")

  return lambda *x, **y: ifAction(*x, **y) if condition(*x, **y) else elseAction(*x, **y)

def both(predicate1, predicate2):
  validate_callable(predicate1, "TypeError: first predicate argument should be callable")
  validate_callable(predicate2, "TypeError: second predicate argument should be callable")
  return lambda x: predicate1(x) and predicate2(x)
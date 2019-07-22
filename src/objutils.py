import collections.abc

def has_path(path, obj):
  try: 
    get_path(path, obj)
    return True
  except:
    return False

def get_path(path, obj):
  if not isinstance(path, collections.abc.Sequence) or isinstance(path, str):
    raise Exception(f"Path should implement the Sequence interface and not be a string")
  elif len(path) != 0:
    return get_path(path[1:], obj[path[0]])
  else:
    return obj

def set_path(path, obj, value):
  if not isinstance(path, collections.abc.Sequence) or isinstance(path, str):
    raise Exception(f"path should implement the Sequence interface and not be a string")
  elif len(path) != 1:
    return set_path(path[1:], obj[path[0]], value)
  else:
    obj[path[0]] = value
    # do not return anything because this is a mutative operation
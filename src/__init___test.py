from . import add

def test_add():
  assert add(1, 2) == 3

def test_add_multiple():
  assert add(1, 2, 3) == 6
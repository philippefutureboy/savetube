import sys

def log(*args, **kwargs):
  print(*args, file=sys.stdout, **kwargs)

def error(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)
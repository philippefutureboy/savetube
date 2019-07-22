import re
from watchdog.observers import Observer
from watchdog.events import FileDeletedEvent, FileMovedEvent
from functional import noop, ifElse

Watcher = Observer

class ConditionalFileEventHandler:
  def __init__(self, condition, ifAction, elseAction = noop):
    self.handler = ifElse(condition, ifAction, elseAction)
  
  def dispatch(self, event):
    print(event)
    self.handler(event)

def is_moved_event(event):
  return type(event) in [FileMovedEvent]

def filename_matches(pattern, event):
  filename = event.dest_path
  print(pattern, filename)
  match = re.match(pattern, filename)
  if match is not None:
    return True
  return False
import re
import os
from pprint import pprint
import json
import jsonschema
import jsonmerge
import copy
import console
import objutils

CONFIG_REGEXP_PATHS = {
  # title
  "title.songname": ["parsers", "title", "songname"],
  "title.artist": ["parsers", "title", "artist"],
  "title.album": ["parsers", "title", "album"],
  "title.album_artist": ["parsers", "title", "album_artist"],
  "title.compilation": ["parsers", "title", "compilation"],
  "title.composer": ["parsers", "title", "composer"],
  "title.release_year": ["parsers", "title", "release_year"],
  "title.comment": ["parsers", "title", "comment"],
  # description
  "description.songname": ["parsers", "description", "songname"],
  "description.artist": ["parsers", "description", "artist"],
  "description.album": ["parsers", "description", "album"],
  "description.album_artist": ["parsers", "description", "album_artist"],
  "description.compilation": ["parsers", "description", "compilation"],
  "description.composer": ["parsers", "description", "composer"],
  "description.release_year": ["parsers", "description", "release_year"],
  "description.comment": ["parsers", "description", "comment"],
  "description.tracklist": ["parsers", "description", "tracklist"],
}
  

def get_configuration_from_file(filename):
  try:
    defaultrc_json = get_defaultrc_json()
    user_rc_json = open_json(filename)

    rc_json = jsonmerge.merge(
      defaultrc_json,
      user_rc_json
    )

    validate_configuration(rc_json)
    return compile_configuration(rc_json)
  except FileNotFoundError as e:
    console.error(e.__doc__)
    return None

#############################################

def get_defaultrc_json():
  current_dirname = os.path.dirname(os.path.realpath(__file__))
  filename = os.path.join(current_dirname, 'defaultrc.json')
  return open_json(filename)

def open_json(filename):
  value = None
  with open(filename) as json_file: 
    value = json.load(json_file)
  
  return value

def validate_configuration(rc_json):
  validate_schema(rc_json)
  validate_schema_regexps(rc_json)

def fake_config():
  fake = fake_schema(generate_schema())
  fake['title'] = fake['parsers']['title']
  del(fake['parsers']['title'])
  fake['description'] = fake['parsers']['description']
  del(fake['parsers']['description'])
  # info from youtube-dl
  fake['info'] = {
    'fulltitle': 'fulltitle',
    'title': 'title',
    'upload_date': '22220222',
    'upload_year': 2222,
    'upload_month': 2,
    'upload_day': 22,
    'uploader': 'uploader',
    'album': 'album',
    'artist': 'artist',
    'creator': 'creator',
    'description': 'description',
    'episode_number': 1,
    'release_year': 2222,
    'season_number': 1,
    'series': 'series',
    'tags': ['tag 1', 'tag 2'],
  }
  return fake

def fake_schema(schema, key=""):
  if 'type' in schema and schema['type'] == 'object':
    if 'properties' in schema and isinstance(schema['properties'], dict):
      res = {k: fake_schema(v, k) for k, v in schema['properties'].items()}
    else:
      res = {}
  elif 'type' in schema and schema['type'] == 'array':
    if 'items' in schema and isinstance(schema['items'], list):
      res = [fake_schema(e) for e in schema['items']]
    else:
      res = []
  elif 'type' in schema and schema['type'] == 'number':
    res = 1
  elif 'type' in schema and schema['type'] == 'string':
    res = key
  elif 'type' in schema and schema['type'] == 'boolean':
    res = True

  return res
    

  

  

def generate_schema():
  available_props_schema = {
    "songname": { "type": "string" },
    "artist": { "type": "string" },
    "album": { "type": "string" },
    "album_artist": { "type": "string" },
    "compilation": { "type": "string" },
    "composer": { "type": "string" },
    "release_year": { "type": "string" },
    "comment": { "type": "string" },
    "tracklist": { "type": "string" },
    "disk_1": { "type": "string" },
    "disk_2": { "type": "string" },
    "trkn_1": { "type": "string" },
    "trkn_2": { "type": "string" },
  }
  return {
    "type": "object",
    "properties": {
      "parsers": {
        "type": "object",
        "properties": {
          "title": {
            "type": "object",
            "properties": {
              **available_props_schema
            },
          },
          "description": {
            "type": "object",
            "properties": {
              **available_props_schema
            },
          },
        },
      },
      "tags": {
        "type": "object",
        "properties": {
          **available_props_schema
        },
      },
      "save_tracklist_in_lyrics": { "type": "boolean", "default": True },
      "append_all_data_in_lyrics": { "type": "boolean", "default": True },
      "save_all_data_on_file": { "type": "boolean", "default": True },
      "config": { "type": "object" },
    },
    "additionalProperties": False,
    "required": ["parsers", "tags"]
  }


def validate_schema(rc_json):
  return jsonschema.validate(instance=rc_json, schema=generate_schema())


# TODO: TEST: should raise an exception with the errors as the 'errors' property if one or many 
# regexp fail validation
def validate_schema_regexps(rc_json):
  errors = []
  for path in CONFIG_REGEXP_PATHS.values():
    if not objutils.has_path(path, rc_json):
      pass
    elif not validate_regexp(objutils.get_path(path, rc_json)):
      errors.append({
        "keyword": "regexpCompiles",
        "path": '.'.join(path),
        "message": f"regexp does not compile"
      })
    elif not has_substr(objutils.get_path(path, rc_json), path[-1]):
      errors.append({
        "keyword": "invalidParser",
        "path": '.'.join(path),
        "message": f"regexp for the {'.'.join(path)} parser does not contain a group named '{path[-1]}'"
      })

  if len(errors):
    error = Exception("Invalid configuration: some regexps are invalid")
    error.errors = errors
    console.error(str(error))
    console.error(errors)

    raise error

def validate_regexp(regexp):
  try:
    re.compile(regexp)
    return True
  except re.error:
    return False

def has_substr(superstr, substr):
  try:
    superstr.index(substr)
    return True
  except ValueError:
    return False

def compile_configuration(rc_json):
  rccopy = copy.deepcopy(rc_json)
  for path in CONFIG_REGEXP_PATHS.values():
    if objutils.has_path(path, rccopy):
      objutils.set_path(path, rccopy, re.compile(objutils.get_path(path, rccopy)))
  return rccopy

  
if __name__ == "__main__":
  fake_config()
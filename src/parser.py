import re
from configure import CONFIG_REGEXP_PATHS
import objutils

def parse_info(parser_key, rc_json, video_info, info_key):
  result = {}
  for key in CONFIG_REGEXP_PATHS.keys():
    try:
      # TODO: support multiline for tracklist
      if (key.index(parser_key) == 0):
        # print(parser_key, key, CONFIG_REGEXP_PATHS[key])
        parser = objutils.get_path(CONFIG_REGEXP_PATHS[key], rc_json)
        # print(parser_key, key, parser)
        targets = video_info[info_key].split('\n')
        matches = [parser.match(target) for target in targets]
        # print(parser_key, key, matches, CONFIG_REGEXP_PATHS[key][-1])
        parsed = ''
        for match in matches:
          if match is None:
            continue
          parsed += match.group(CONFIG_REGEXP_PATHS[key][-1])

        # print(parser_key, key, parsed, CONFIG_REGEXP_PATHS[key][-1])
        result[CONFIG_REGEXP_PATHS[key][-1]] = parsed
        # print(f"{CONFIG_REGEXP_PATHS[key][-1]}: {result[CONFIG_REGEXP_PATHS[key][-1]]}")
        # print()
    # handles ValueError from index
    except ValueError:
      pass
    # handles KeyError from get_path
    # handles AttributeError from None match
    # handles IndexError from match.group(key)
    except (KeyError, AttributeError, IndexError):
      # print(f"raise for {key} // {CONFIG_REGEXP_PATHS[key][-1]}")
      result[CONFIG_REGEXP_PATHS[key][-1]] = ''
  return result
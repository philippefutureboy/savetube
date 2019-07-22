import json 
from mutagen.mp4 import MP4

# TODO: might want some error logging for when the type cast fails
# TODO: add disk, trkn, bpm to configure file
def convert_tags_to_id3(rc_json, data):
  ID3_TAGS_TO_DATA_TAGS = {
    "\xa9nam": ["songname", str],
    "\xa9ART": ["artist", str],
    "\xa9alb": ["album", str],
    "aART": ["album_artist", str],
    "\xa9grp": ["compilation", str],
    "\xa9wrt": ["composer", str],
    "\xa9day": ["release_year", str],
    "\xa9cmt": ["comment", str],
    "disk": [
      ["disk_1", int],
      ["disk_2", int]
    ],
    "trkn": [
      ["trkn_1", int], 
      ["trkn_2", int]
    ],
    "tmpo": ["bpm", int],
    "\xa9gen": ["genre", str],
  }

  data_tags = data['tags']
  data_appendix = f"\n\nData:\n{json.dumps(data)}"
  tags = {}
  for k, v in ID3_TAGS_TO_DATA_TAGS.items():
    v1, v2 = v
    if type(v1) is str and v1 in data_tags:
      key = v1
      typefn = v2
      value = safe_cast(data_tags[key], typefn) if key in data_tags else None
      if value is not None:
        tags[k] = [value]
    elif type(v1) is list:
      res = [safe_cast(data_tags[key], typefn) if key in data_tags else None for key, typefn in v]
      if all(value is not None for value in res):
        tags[k] = [res]

  if rc_json["save_tracklist_in_lyrics"] and "tracklist" in data_tags:
    tags["\xa9lyr"] = data_tags["tracklist"]

  if rc_json["append_all_data_in_lyrics"]:
    tags["\xa9lyr"] = tags["\xa9lyr"] + data_appendix if "\xa9lyr" in tags else data_appendix
    
  if rc_json["save_all_data_on_file"]: 
    tags["savetubedata"] = data_appendix

  return tags

def safe_cast(value, castfn):
  try:
    return castfn(value)
  except:
    return None

def write_tags_to_file(filename, id3_tags, retry=True):
  old_tags = {}
  try:
    file = MP4(filename)
    old_tags = { **file.tags }
    for k, v in id3_tags.items():
      file.tags[k] = v
    file.save()
  except Exception as error:
    if len(old_tags.keys()) != 0 and retry is True:
      write_tags_to_file(filename, old_tags, retry=False)
    raise error


# if __name__ == "__main__":
#   readFileTags()
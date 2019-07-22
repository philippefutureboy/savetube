import os
import json
import time
import copy
import subprocess
import shutil
from pprint import pprint
from functools import partial
import youtube
import handlebars
import objutils
import args
import fs
from functional import both
from watcher import Watcher, ConditionalFileEventHandler, is_moved_event, filename_matches
from configure import get_configuration_from_file
from parser import parse_info
from tagger import convert_tags_to_id3, write_tags_to_file

def say_hello():
  print(
"""
                                         $$\               $$\                 
                                         $$ |              $$ |                
 $$$$$$$\  $$$$$$\ $$\     $$\ $$$$$$\ $$$$$$\   $$\   $$\ $$$$$$$\   $$$$$$\  
$$  _____| \____$$\\$$\    $$ |$$  __$$ \\_$$  _|  $$ |  $$ |$$  __$$\ $$  __$$\ 
\$$$$$$\   $$$$$$$ |\$$\$$  / $$$$$$$$ | $$ |    $$ |  $$ |$$ |  $$ |$$$$$$$$ |
 \____$$\ $$  __$$ | \$$$  /  $$   ____| $$ |$$\ $$ |  $$ |$$ |  $$ |$$   ____|
$$$$$$$  |\$$$$$$$ |  \$  /   \$$$$$$$\  \$$$$  |\$$$$$$  |$$$$$$$  |\$$$$$$$\ 
\_______/  \_______|   \_/     \_______|  \____/  \______/ \_______/  \_______|

"""                                                                                                                                                  
  )

def main():
  config = args.parse()
  say_hello()
  print('cli arguments as understood:\n')
  pprint(config, indent=2)
  print('\n\n')

  # dry run
  if config['dry'] is True:
    dry_run(config['dry_opts'])
  # real run
  elif len(config['watchers']):
    YOUTUBE_FILENAME_PATTERN = "(.*\\/)?([a-zA-Z0-9\\_\\-]{10,})\\.(mp3|m4a)$"
    watcher = Watcher()

    for watcher_config in config['watchers']:
      rc_json = get_configuration_from_file(watcher_config['rc_filename'])
      on_event = ConditionalFileEventHandler(
        both(is_moved_event, partial(filename_matches, YOUTUBE_FILENAME_PATTERN)),
        partial(on_youtube_music_file, rc_json=rc_json, watcher_config=watcher_config)
      )
      watcher.schedule(on_event, watcher_config['watch'], recursive=config['recursive'])
    
    watcher.start()

    try:
      while True:
        time.sleep(1)
    except KeyboardInterrupt:
      if watcher is not None:
        watcher.stop()
  # inconsistent state
  else:
    raise ValueError('ValueError: Program should be run with either the --dry flag or with some --watch and --out values')

def on_youtube_music_file(event, rc_json, watcher_config):
  print()
  filename = event.dest_path
  video_id = youtube.get_video_id_from_filename(event.dest_path)
  print("Processing {" + video_id + "}")
  
  render_data = extract_data(video_id, rc_json)
  full_data = add_filesystem_data(filename, rc_json, watcher_config, render_data)
  id3_tags = convert_tags_to_id3(rc_json, render_data)

  dest_filename = get_output_path(watcher_config, full_data)
  if dest_filename == filename:
    print("Writing tags for {" + video_id + "} " + f"{full_data['info']['title']} to source file")
    write_tags_to_file(filename, id3_tags)
  else:
    print("Writing {" + video_id + "} " + f"{full_data['info']['title']} to file > {dest_filename}")
    fs.mkdir_p(os.path.dirname(dest_filename))
    shutil.copyfile(filename, dest_filename)
    write_tags_to_file(dest_filename, id3_tags)

def dry_run(dry_opts):
  rc_json = get_configuration_from_file(dry_opts['rc_filename'])
  video_id = dry_opts['youtube_video_id']
  render_data = extract_data(video_id, rc_json)

  if dry_opts['out']:
    filename = dry_opts['out_src_filename']
    watcher_config = {
      'rc_filename': dry_opts['rc_filename'],
      'watch': os.path.dirname(filename),
      'watch_root': dry_opts['out_src_root'],
      'out_template': dry_opts['out_template'],
    }
    full_data = add_filesystem_data(filename, rc_json, watcher_config, render_data)

    print()
    print("Result:")
    pprint(full_data)
    print()

    print("Rendered out template:")
    print(get_output_path(watcher_config, full_data))
    print()
  else:
    print()
    print("Result:")
    pprint(render_data)
    print()
  

def extract_data(video_id, rc_json):
  info = youtube.get_video_info(video_id)
  # TODO: Parse release_date
  parsed_title = parse_info('title', rc_json, info, 'title')
  parsed_description = parse_info('description', rc_json, info, 'description')

  data = {
    'info': info,
    'title': parsed_title,
    'description': parsed_description,
    'config': {
      **rc_json['config'],
    }
  }
  # render the tags from rc_json
  tags = {k: handlebars.render(v, data) for k, v in rc_json['tags'].items()}
  # filter empty values
  tags = {k: v for k, v in tags.items() if v is not None and v != '' and v != 'null'}

  return {
    **data,
    'tags': tags
  }

def add_filesystem_data(filename, rc_json, watcher_config, data):
  # TODO: Add handlebars compile check
  src_extname = os.path.splitext(filename)[1]
  src_extname = src_extname[1:] if len(src_extname) > 1 else src_extname
  return { 
    **data,
    'config': {
      **data['config'],
      'src_filename': filename,
      'src_dirname': os.path.dirname(filename),
      'src_basename': os.path.basename(filename),
      'src_extname': src_extname,
      'src_root': watcher_config['watch_root'],
      'src_root_relative_dirname': os.path.dirname(filename)[len(watcher_config['watch_root']) + 1:]
    },
  }

def get_output_path(watcher_config, data):
  return handlebars.render(watcher_config['out_template'], data)


#############################################

if __name__ == "__main__":
  main()

#############################################
import os
import re
import argparse
import json
import pydash as _
import fs
import handlebars
from configure import fake_config

def parse():
  # Instantiate the parser
  parser = argparse.ArgumentParser(description='savetube: apply your youtube metadata to id3 tags')

  parser.add_argument(
    '--dry',
    type=str,
    nargs=2,
    metavar=('youtube_video_id', 'savetuberc_path'),
    help='Prints the raw data as well as the render_data that is available to you once parsed. Incompatible with the --watch and --out flags.'
  )

  parser.add_argument(
    '--dry_out',
    type=str,
    nargs=3,
    metavar=('src_root', 'src_filename', 'out_template'),
    help='Dry-run the out_template given the src_root and src_filename provided. Must be used jointly with --dry'
  )

  parser.add_argument(
    '--watch',
    type=str,
    nargs='+',
    metavar=('dir', 'dir'),
    help='Directories to watch. Supports multiple independent directories by specifying them after the --watch flag. The number of watch directories must match the number of out directory templates')
  
  parser.add_argument(
    '--recursive',
    action='store_true',
    default=False,
    help='Specifies if watched directories should be recursively watched.'
  )

  parser.add_argument(
    '--out',
    type=str,
    nargs='+',
    metavar=('out_template', 'out_template'),
    help='Template path for the destination filename. Supports multiple independent destinations by specifying them after the --out flag. The number of out directory templates must match the number of watch directories. Non-existent directories will be created '
  )

  args = parser.parse_args()
  if __name__ == "__main__":
    print(args)

  # Error handling for proper usage
  if args.dry is not None and (args.watch is not None or args.out is not None):
    parser.error("ParserError: --dry flag cannot be combined with --watch or --out flags")
  elif args.dry is None:
    if args.watch is None or args.out is None:
      if args.watch is None:
        parser.error("ParserError: --watch flag is required")
      if args.out is None:
        parser.error("ParserError: --out flag is required")
    elif len(args.watch) != len(args.out):
      parser.error("ParserError: --watch and --out flags should have the same number of values")
  
  # Convert args to usable configs
  if args.dry is not None:
    return {
      'dry': True,
      'dry_opts': {
        'out': args.dry_out is not None,
        'out_src_root': None if args.dry_out is None else args.dry_out[0],
        'out_src_filename': None if args.dry_out is None else args.dry_out[1],
        'out_template': None if args.dry_out is None else args.dry_out[2],
        'rc_filename': args.dry[1],
        'youtube_video_id': args.dry[0],
      },
      'recursive': args.recursive,
      'watchers': [],
    }
  else:
    # validate out_templates
    fake_config_data = fake_config()
    invalid_out_templates = [e for v in args.out if not validate_handlebars(v, fake_config_data)]
    if len(invalid_out_templates):
      parser.error(f"ParserError: The following arguments(s) to the --out flag are not valid templates: {json.dumps(invalidTemplates)}")
    
    return {
      'dry': False,
      'recursive': args.recursive,
      'watchers': get_watcher_configs_from_args(args),
    }

def validate_handlebars(template, data):
  try:
    handlebars.render(template, data)
    return True
  except re.error:
    return False

def get_watcher_configs_from_args(args):
  watch_and_out_pairs = zip(args.watch, args.out)
  watchers = None
  if args.recursive:
    watchers = _.flatten([
      [
        {
          'rc_filename': rc_filename,
          'watch': os.path.dirname(rc_filename),
          'watch_root': root_folder[:-1] if root_folder.endswith('/') else root_folder,
          'out_template': out,
        }
        for rc_filename in fs.find_pattern('savetuberc.json', root_folder)
      ]
      for root_folder, out in watch_and_out_pairs
    ])
  else:
    watchers = [
      { 
        'rc_filename': os.path.join(os.path.dirname(root_folder), 'savetuberc.json'),
        'watch': os.path.dirname(root_folder),
        'watch_root': root_folder[:-1] if root_folder.endswith('/') else root_folder,
        'out_template': out,
      } for root_folder, out in watch_and_out_pairs
    ]

  return watchers


# def main():
#   config = parse()
#   print(config)


# #############################################

# if __name__ == "__main__":
#   main()

# #############################################
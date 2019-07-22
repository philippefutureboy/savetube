import re
import math
import json
import subprocess
import objutils
from datetime import date
from configure import CONFIG_REGEXP_PATHS

def get_video_id_from_filename(filename):
  pattern = "(.*\\/)?(?P<id>[a-zA-Z0-9\\_\\-]{10,})\\..*"
  match = re.match(pattern, filename)
  if match is None:
    return None
  return match.group('id')

def get_video_info(video_id):
  ydl_info_stdout = subprocess.check_output(
    ["youtube-dl", "-j", f"https://www.youtube.com/watch?v={video_id}"], 
    encoding='UTF-8'
  )
  props_to_remove = [
    'formats',
    'requested_formats',
  ]
  raw_info = json.loads(ydl_info_stdout)
  info = {k: v for k, v in raw_info.items() if not(k in props_to_remove)}
  upload_date = safe_int(info['upload_date'])
  if upload_date:
    upload_year = math.floor(upload_date / (100 * 100))
    upload_month = math.floor(math.fmod(upload_date, 100 * 100) / 100)
    upload_day = math.floor(math.fmod(upload_date, 100))
    info['upload_date'] = str(date(
      upload_year,
      upload_month,
      upload_day,
    ))
    info['upload_year'] = upload_year
    info['upload_month'] = upload_month
    info['upload_day'] = upload_day
  else: 
    info['upload_date'] = ''
    info['upload_year'] = 0
    info['upload_month'] = 0
    info['upload_day'] = 0
  return info

def safe_int(s):
  try:
    return int(s)
  except:
    return None
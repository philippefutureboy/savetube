import os
import subprocess
import json
 
def render(template, data):
    current_dirname = os.path.dirname(os.path.realpath(__file__))
    handlebarsjs = os.path.join(current_dirname, "handlebars.js")
    proc = subprocess.Popen(
        ["node", handlebarsjs, template, json.dumps(data)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
 
    if proc.returncode == 0:
      return stdout.decode('utf-8')
    else:
      raise Exception(stderr.decode('utf-8'))
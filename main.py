from collections import defaultdict
import flask
from flask import request
from flask import render_template
from miner import run_miner
import re
import threading
import time
import yaml

def load_settings():
    settings_file = open('settings.yaml')
    s = yaml.safe_load(settings_file)
    settings_file.close()
    return s

current_settings = load_settings()


def run_miner_every_interval():
    while True:
        run_miner(current_settings['uris'],
                  current_settings['miner_name'],
                  current_settings['engine_uri'])
        time.sleep(current_settings['interval'])


def start_miner():
    miner_thread = threading.Thread(target=run_miner_every_interval)
    miner_thread.start()


integer_re = re.compile(r'^[0-9]+$');

url_re = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def validate_settings(settings_dict):
    errors = defaultdict(str)
    # ensure all the required keys are present
    for key in ['uris', 'miner_name', 'engine_uri', 'interval']:
        if key not in settings_dict:
            errors[key] = key + " is missing and must be specificed."
    # check they are all the correct types
    if 'uris' in settings_dict: # list of uris
        uris = settings_dict['uris'].split()
        if len(uris) == 0:
            errors['uris'] = "Please specify at least one RSS feed to mine."
        else:
            for uri in uris:
                if not url_re.match(uri):
                    errors['uris'] += uri + " is not a valid uri. "
    if 'engine_uri' in settings_dict:
        engine_uri = settings_dict['engine_uri']
        if len(engine_uri) == 0:
            errors['engine_uri'] = "Please specify the location of the engine."
        else:
            if not url_re.match(engine_uri):
                errors['engine_uri'] = engine_uri + " is not a valid uri."
    return len(errors) > 0, errors


# setup the Flask app
app = flask.Flask(__name__)
app.config['DEBUG'] = True

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'GET':
        return render_template('settings.html', settings=current_settings, errors={})
    elif request.method == "POST":
        has_errors, errors = validate_settings(request.form)
        if has_errors:
            return render_template('settings.html', settings=request.form, errors=errors)
        else:
            return 'OK', 200



app.run()
import requests
import json
from requests.auth import HTTPBasicAuth


def make_request(conf, jsondata):
    """
    Makes a request to the transmission API. Requires the above
    configuration to be set. First logs in, then sets the session id and
    finally makes the request and returns the data as json.
    """
    conf = conf["transmission"]
    session_id = {}
    url = "http://{0}:{1}/{2}/rpc".format(conf["host"], conf["port"], conf["path"])
    # Get the initial X-Transmission-Session-Id
    response = requests.get(url, auth=HTTPBasicAuth(conf["username"], conf["password"]))
    # Check for failure.
    if response.status_code == 401:
        raise Exception("Not a valid username!")
    if response.status_code == 409:
        session_id = {'X-Transmission-Session-Id': response.headers['X-Transmission-Session-Id']}
    response = requests.post(url,
                             data=json.dumps(jsondata),
                             headers=session_id,
                             auth=HTTPBasicAuth(conf["username"], conf["password"]))
    return json.loads(response.text)


def get_torrentlist(conf):
    """
    Uses make_request to request a list of all the torrents
    active. Returns a list of json objects.
    """
    jsondata = {'arguments':
                {'fields': ['id', 'name', 'secondsSeeding', 'uploadRatio']},
                'method': 'torrent-get'}
    return make_request(conf, jsondata)['arguments']['torrents']


def remove_torrent(conf, torrent):
    """
    Removes a torrent from transmission. Also removes the data from disk!
    """
    jsondata = {'arguments': {'ids': [torrent['id']], 'delete-local-data': conf["transmission"]["remove_from_disk"]},
                'method': 'torrent-remove'}
    make_request(conf, jsondata)


def old_torrent(conf, torrent):
    """
    Determines if a torrent is old according to settings above.
    """
    conf = conf["transmission"]
    age_epoch = int(torrent['secondsSeeding'])
    daysSeeding = age_epoch / 84600
    return daysSeeding > conf["remove_older_than"]


def seeded_torrent(conf, torrent):
    """
    Determines if a torrent is seeded plenty, according to settings above.
    """
    conf = conf["transmission"]
    ratio = float(torrent['uploadRatio'])
    return ratio > conf["remove_seeded"]


def print_torrent(torrent):
    """
    Prints torrent's name, ratio and seed time.
    """
    age_epoch = int(torrent['secondsSeeding'])
    daysSeeding = age_epoch / 84600
    print("Name: {0}, Ratio: {1:.2f}, Seeded: {2} days".format(torrent['name'],
          float(torrent['uploadRatio']), daysSeeding))
    return torrent


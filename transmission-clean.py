import requests
import json
import sys
from requests.auth import HTTPBasicAuth

####################################################################################
# Author: Christophe De Troyer                                                     #
# Created: 09/10/2015                                                              #
# Version: 1.0                                                                     #
#                                                                                  #
# Description:                                                                     #
# Removes stale and plenty seeded torrents from transmission daemon via the remote #
# api.                                                                             #
####################################################################################

host = "host.com"
port = "80"
path = "transmission"  # Must end with a slash and begin without! 

username = "username"
password = "password"

url = "http://{0}:{1}/{2}/rpc".format(host, port, path)

remove_older_than = 20  # Remove torrents older this amount of days.
remove_seeded = 3  # Remove torrents with ratio bigger than this.
remove_from_disk = 'true'  # Aso remove from disk.


def make_request(jsondata):
    """Makes a request to the transmission api. Requires the above
    configuration to be set. First logs in, then sets the session id and
    finally makes the request and returns the data as json.
    """
    session_id = {}
    # Get the initial X-Transmission-Session-Id
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    # Check for failure.
    if response.status_code == 401:
        raise Exception("Not a valid username!")
    if response.status_code == 409:
        session_id = {'X-Transmission-Session-Id': response.headers['X-Transmission-Session-Id']}
    response = requests.post(url, data=json.dumps(jsondata), headers=session_id, auth=HTTPBasicAuth(username, password))
    return json.loads(response.text)


def get_torrentlist():
    """Uses make_request to request a list of all the torrents
    active. Returns a list of json objects.
    """
    jsondata = {'arguments': {'fields': ['id', 'name', 'secondsSeeding', 'uploadRatio']}, 'method': 'torrent-get'}
    return make_request(jsondata)['arguments']['torrents']


def remove_torrent(torrent):
    """Removes a torrent from transmission. Also removes the data from disk!"""
    jsondata = {'arguments': {'ids': [torrent['id']], 'delete-local-data': remove_from_disk},
                'method': 'torrent-remove'}
    make_request(jsondata)


def old_torrent(torrent):
    """Determines if a torrent is old according to settings above."""
    age_epoch = int(torrent['secondsSeeding'])
    daysSeeding = age_epoch / 84600
    return daysSeeding > remove_older_than


def seeded_torrent(torrent):
    """Determines if a torrent is seeded plenty, according to settings above."""
    ratio = float(torrent['uploadRatio'])
    return ratio > remove_seeded


def print_torrent(torrent):
    age_epoch = int(torrent['secondsSeeding'])
    daysSeeding = age_epoch / 84600
    print("Name: {0:.20} Age: {1:.6} Seeded for: {2} days".format(torrent['name'], '%.3f'%(torrent['uploadRatio']), daysSeeding))
    return torrent

if len(sys.argv) > 1:
  if sys.argv[1] == "-print":
    map(print_torrent, get_torrentlist())
  elif sys.argv[1] == "-clean":
    map(lambda t: remove_torrent(print_torrent(t)), filter(lambda t: old_torrent(t) or seeded_torrent(t), get_torrentlist()))

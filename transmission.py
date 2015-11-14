import requests
import json
from requests.auth import HTTPBasicAuth


class Transmission:
    def __init__(self, **kwargs):
        self.host = kwargs['host']
        self.port = kwargs['port']
        self.path = kwargs['path']
        self.user = kwargs['username']
        self.pwrd = kwargs['password']
        self.remove_older_than = kwargs['remove_older_than']
        self.remove_seeded = kwargs['remove_seeded']
        self.remove_from_disk = kwargs['remove_from_disk']
        self.url = 'http://{0}:{1}/{2}/rpc'.format(self.host, self.port, self.path)
        self.session = self._create_session()

    def _create_session(self):
        """
        Authenticates with Transmission and returns an HTTP session
        """
        s = requests.Session()
        r = s.get(self.url, auth=HTTPBasicAuth(self.user, self.pwrd))
        if r.status_code == 401:
            raise Exception('Not a valid username!')
        elif r.status_code == 409:
            s.headers.update(r.headers)
        return s

    def _make_request(self, jsondata):
        """
        Makes a request to the transmission api and returns the data as json.
        """
        response = self.session.post(self.url, auth=HTTPBasicAuth(self.user, self.pwrd), data=json.dumps(jsondata))
        return json.loads(response.text)

    def get_torrentlist(self):
        """
        Uses make_request to request a list of all the torrents
        active. Returns a list of json objects.
        """
        jsondata = {'arguments':
                    {'fields': ['id', 'name', 'secondsSeeding', 'uploadRatio']},
                    'method': 'torrent-get'}
        return self._make_request(jsondata)['arguments']['torrents']

    def remove_torrent(self, torrent):
        """
        Removes a torrent from transmission. Also removes the data from disk!
        """
        jsondata = {'arguments': {'ids': [torrent['id']], 'delete-local-data': self.remove_from_disk},
                    'method': 'torrent-remove'}
        self._make_request(jsondata)

    def old_torrent(self, torrent):
        """
        Determines if a torrent is old according to settings above.
        """
        age_epoch = int(torrent['secondsSeeding'])
        daysSeeding = age_epoch / 84600
        return daysSeeding > self.remove_older_than

    def seeded_torrent(self, torrent):
        """
        Determines if a torrent is seeded plenty, according to settings above.
        """
        ratio = float(torrent['uploadRatio'])
        return ratio > self.remove_seeded

    def print_torrent(self, torrent):
        """
        Prints torrent's name, ratio and seed time.
        """
        age_epoch = int(torrent['secondsSeeding'])
        daysSeeding = age_epoch / 84600
        print('Name: {0}, Ratio: {1:.2f}, Seeded: {2} days'.format(torrent['name'],
              float(torrent['uploadRatio']), daysSeeding))
        return torrent


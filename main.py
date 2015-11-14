import sys
import os
import yaml
import datetime
from pushbullet import PushBullet
import transmission as tr


def read_config():
    """
    Reads the YAML config file
    """
    path = os.path.dirname(os.path.realpath(sys.argv[0]))
    with open('%s/config.yaml' % path, 'r') as f:
        conf = yaml.load(f)
    return conf

conf = read_config()
pb = PushBullet(conf['pushbullet']['access_token'])
devices = conf['pushbullet']['devices']
dt_time = datetime.datetime.now().strftime('%I:%M%p %d/%m/%y')

if '-p' in sys.argv or '--print' in sys.argv:
    map(tr.print_torrent, tr.get_torrentlist(conf))
elif '-l' in sys.argv or '--list-devices' in sys.argv:
    for idx, device in enumerate(pb.get_devices()):
        print('[{0}] {1}: {2}'.format(idx, *device))
elif '-c' in sys.argv or '--clean' in sys.argv:
    complete_torrents = filter(lambda t: tr.old_torrent(conf, t) or tr.seeded_torrent(conf, t),
                               tr.get_torrentlist(conf))

    # Send a push for each torrent to be remove
    map(lambda t: pb.push_note("Torrent Removed",
                               "Torrent {0} has been removed at {1}".format(t['name'], dt_time),
                               devices), complete_torrents)

    # Remove and print torrents
    map(lambda t: tr.remove_torrent(conf, tr.print_torrent(t)), complete_torrents)


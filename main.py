import sys
import os
import yaml
import transmission


def read_config():
    """
    Reads the YAML config file
    """
    path = os.path.dirname(os.path.realpath(sys.argv[0]))
    with open('%s/config.yaml' % path, 'r') as f:
        conf = yaml.load(f)
    return conf


if '-print' in sys.argv:
    map(transmission.print_torrent, transmission.get_torrentlist())
elif '-clean' in sys.argv:
    map(lambda t: transmission.remove_torrent(transmission.print_torrent(t)),
        filter(lambda t: transmission.old_torrent(t) or
        transmission.seeded_torrent(t), transmission.get_torrentlist()))


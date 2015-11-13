import sys
import transmission

if '-print' in sys.argv:
    map(transmission.print_torrent, transmission.get_torrentlist())
elif '-clean' in sys.argv:
    map(lambda t: transmission.remove_torrent(transmission.print_torrent(t)),
        filter(lambda t: transmission.old_torrent(t) or
        transmission.seeded_torrent(t), transmission.get_torrentlist()))


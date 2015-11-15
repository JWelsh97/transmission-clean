import sys
import datetime
import config
from pushbullet import PushBullet
from transmission import Transmission


def add_device(pb, conf, dev_num):
    """
    Adds a device identity to config
    using --add-device or -a command
    """
    dev_lst = pb.get_devices()
    try:
        dev_name, dev_id = dev_lst[dev_num]
    except:
        print('Invalid device')
        return

    if 'devices' not in conf['pushbullet']:
        conf['pushbullet']['devices'] = []

    if not isinstance(conf['pushbullet']['devices'], list):
        conf['pushbullet']['devices'] = []

    if dev_id in conf['pushbullet']['devices']:
        print('%s is already listed' % dev_name)
    else:
        conf['pushbullet']['devices'].append(dev_id)
        config.write_config(conf)
        print('Added %s' % dev_name)


def remove_device(pb, conf, dev_num):
    """
    Removes a device identity
    from the config using
    --remove-device or -r
    """
    dev_lst = pb.get_devices()
    try:
        dev_name, dev_id = dev_lst[dev_num]
    except:
        print('Invalid device')
        return

    if 'devices' in conf['pushbullet']:
        try:
            conf['pushbullet']['devices'].pop(conf['pushbullet']['devices'].index(dev_id))
        except:
            print('That device is not in your config')
            return
        config.write_config(conf)
        print('Removed %s' % dev_name)

conf = config.read_config()
tr = Transmission(**conf['transmission'])
pb = PushBullet(conf['pushbullet']['access_token'])
devices = conf['pushbullet']['devices']
dt_time = datetime.datetime.now().strftime('%I:%M%p %d/%m/%y')

if '-p' in sys.argv or '--print' in sys.argv:
    map(tr.print_torrent, tr.get_torrentlist())

elif '-l' in sys.argv or '--list-devices' in sys.argv:
    for idx, device in enumerate(pb.get_devices()):
        print('[{0}] {1}: {2}'.format(idx, *device))

elif '-a' in sys.argv or '--add-device' in sys.argv:
    try:
        dev_num = int(sys.argv[2])
    except:
        print('Incorrect usage')
        print('Example: -a/--add-device NUMBER')
        sys.exit()
    add_device(pb, conf, dev_num)

elif '-r' in sys.argv or '--remove-device' in sys.argv:
    try:
        dev_num = int(sys.argv[2])
    except:
        print('Incorrect usage')
        print('Example: -r/--remove-device NUMBER')
        sys.exit()
    remove_device(pb, conf, dev_num)

elif '-c' in sys.argv or '--clean' in sys.argv:
    complete_torrents = filter(lambda t: tr.old_torrent(t) or tr.seeded_torrent(t),
                               tr.get_torrentlist())

    # Send a push for each torrent to be remove
    if conf["pushbullet"]["enabled"]:
        map(lambda t: pb.push_note('Torrent Removed',
                                   "Torrent '{0}' was removed at {1}".format(t['name'], dt_time),
                                   devices), complete_torrents)

    # Remove and print torrents
    map(lambda t: tr.remove_torrent(tr.print_torrent(t)), complete_torrents)


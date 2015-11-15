# transmission-clean #
Uses the Transmission API to check if torrents are old or seeded enough according to the configuration set by the user.
If the torrent is old or seededed enough it will remove the torrent and its data (if specified in config) and push a notification using the Pushbullet platform to the selected devices.

## Configuration ##
Rename example.config.yaml to config.yaml. Fill out all of the fields.

## Dependencies  ##
`pip install pyyaml`

## Usage ##
`python main.py args`

## Arguments ##
**-l**  
**--list-devices**  
Prints the list of devices on your Pushbullet account  
[device_id] device_name: device_identity  

**-a**  
**--add-device** *device_id*  
Adds the selected device_id (found using -l/--list-devices argument) to your configuration.  

**-r**  
**--remove-device** *device_id*  
Removes the selected device_id (found using -l/--list-devices argument) from your configuration.  
 
**-p**  
**--print**  
Prints list of torrents.  

**-c**  
**--clean**  
Removes old and seeded torrents and sends Pushbullet notifications.


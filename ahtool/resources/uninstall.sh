#!/bin/sh

set -x

UNINSTALLER=https://my.anthill.farm/static/firmwares/integration/anthill_remove_vnish_3.8.6.tar.gz

echo "Removing Anthill integraion"

# Update rootfs
cd /tmp
curl --insecure $UNINSTALLER -o anthill_remove_vnish.tar.gz
tar -xzf anthill_remove_vnish.tar.gz -C /

# Kill processes
killall -INT ahagent
killall -9 monitorcg
killall -9 bmminer

# Remove config files
rm -f /config/anthill.json

echo "Done!"
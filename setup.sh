#!/bin/sh
cd `dirname $0`

python3 -m pip install fake-bpy-module Pillow
# echo $(pwd -P)/blender_roblox_sync/message_formats
ln -s "$(pwd -P)/message_formats" "$(pwd -P)/blender_roblox_sync/"
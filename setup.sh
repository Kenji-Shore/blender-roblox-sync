#!/bin/sh
cd `dirname $0`
DIR=$(pwd -P)
BL_NAME=$(basename $(dirname $(find . -name "blender_manifest.toml")))
RBX_NAME=roblox_plugin
BL_PATH="$DIR/$BL_NAME"
RBLX_PATH="$DIR/$RBX_NAME"

FMT_NAME=message_formats
FMT_RBLX_NAME=messageFormats
FMT_PATH="$BL_PATH/$FMT_NAME"
FMT_RBLX_PATH="$RBLX_PATH/src/$FMT_RBLX_NAME"

if [ "$1" = "rojo" ]; then
	rm -rf $FMT_RBLX_PATH
	cp -R $FMT_PATH $FMT_RBLX_PATH

	cd $RBLX_PATH
	pnpm rbxtsc --writeOnlyChanged --optimizedLoops
	pnpm rojo build . --output "$BL_PATH/roblox_plugin.rbxm"
	cd $DIR
	exit
fi

cd $RBLX_PATH
pnpm install
cd $DIR

python3 -m pip install --upgrade pip
python3 -m pip install fake-bpy-module Pillow
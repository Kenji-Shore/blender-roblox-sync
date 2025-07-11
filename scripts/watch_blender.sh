#!/bin/sh
. `dirname $0`/common.sh

FMT_NAME=message_formats
FMT_RBLX_NAME=messageFormats
FMT_PATH="$BL_PATH/$FMT_NAME"
FMT_RBLX_PATH="$BL_RBLX_PATH/src/$FMT_RBLX_NAME"

compile_roblox_plugin ()
{
	echo_col 4 "rbxtsc: compiling $BL_NAME roblox plugin..." 
	rm -rf $FMT_RBLX_PATH
	cp -R $FMT_PATH $FMT_RBLX_PATH

	pnpm rbxtsc --writeOnlyChanged --optimizedLoops
	pnpm rojo build . --output "$BL_PATH/roblox_plugin.rbxm"
	echo_col 2 "rbxtsc: successfully compiled $BL_NAME roblox plugin!" 
}

brew install fswatch &
(
	python3 -m pip install --upgrade pip
	python3 -m pip install fake-bpy-module
) &
wait

(
	#setup and compile roblox plugin for blender addon
	cd $BL_RBLX_PATH
	pnpm install
	compile_roblox_plugin
	fswatch -o -l 0.1 "$BL_RBLX_PATH/src" -e "$FMT_RBLX_PATH" | while read num; do
		compile_roblox_plugin
	done
) &
wait
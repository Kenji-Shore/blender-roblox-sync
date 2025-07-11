cd `dirname $0`/..
DIR=$(pwd -P)
BL_ROOT_PATH=$DIR

BL_NAME=$(basename $(dirname $(find $BL_ROOT_PATH -name "blender_manifest.toml")))
BL_PATH="$BL_ROOT_PATH/$BL_NAME"
BL_RBLX_PATH="$BL_ROOT_PATH/roblox_plugin"

echo_col() {
	tput setaf $1
	tput bold
	tput smul
	echo $2
	tput sgr0
}
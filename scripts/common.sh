TEMP_DIR="$(mktemp -d)"
trap 'rm -rf -- "$TEMP_DIR"' 0

cd `dirname $0`/..
DIR=$(pwd -P)
BL_ROOT_PATH=$DIR

BL_NAME=$(basename $(dirname $(find $BL_ROOT_PATH -name "blender_manifest.toml")))
BL_PATH="$BL_ROOT_PATH/$BL_NAME"
BL_RBLX_PATH="$BL_ROOT_PATH/roblox_plugin"

brew install flock > /dev/null
LOCK_FILE=$(mktemp --tmpdir=$TEMP_DIR)
echo_col() {
	flock $LOCK_FILE --command "tput setaf $1 && tput bold && tput smul && echo $2 && tput sgr0"
}
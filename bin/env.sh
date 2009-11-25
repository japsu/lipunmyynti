TRACON_ROOT_DIR=".."
TRACON_ROOT_DIR="$(cd $TRACON_ROOT_DIR && pwd)"

export PYTHONPATH="$TRACON_ROOT_DIR:$PYTHONPATH"
export PATH="$TRACON_ROOT_DIR/bin:$PATH"
export DJANGO_SETTINGS_MODULE="tracon.settings"

function manage {
	python $TRACON_ROOT_DIR/tracon/manage.py $@
}

.PHONY: all install-collections playbooks

playbooks:
	ansible-playbook \
		-i ./playbooks/inventory.ini \
		./playbooks/setup-raspberry-pi-node.yaml \
		./playbooks/setup_wand_reader/create_app_stream.yaml
install-collections:
	ansible-galaxy collection install community.general

.PHONY: setup-python
setup-python:
	venv/bin/pip install -r requirements.txt

.PHONY: requirements
requirements:
	venv/bin/pip freeze > requirements.txt
.PHONY: setup-camera
setup-camera:
	ansible-playbook \
		-i ./playbooks/inventory.ini \
		./playbooks/setup_wand_reader/create_app_stream.yaml

all: playbooks install-collections setup-camera

PI_HOST = ansible@raspberrypi1.local

.PHONY: debug follow restart

# Runs the debug command once and exits
debug:
	ssh $(PI_HOST) "sudo journalctl -u camera.service -n 50 --no-pager"

# Streams the logs in real-time (Ctrl+C to stop)
follow:
	ssh $(PI_HOST) "sudo journalctl -u camera.service -f"

# Restarts the service and then follows the logs
restart:
	ssh $(PI_HOST) "sudo systemctl restart camera.service && sudo journalctl -u camera.service -f"

.PHONY: all install-collections playbooks

playbooks:
	ansible-playbook \
		-i ./playbooks/inventory.ini \
		./playbooks/setup-raspberry-pi-node.yaml
install-collections:
	ansible-galaxy collection install community.general

.PHONY: setup-python
setup-python:
	venv/bin/pip install -r requirements.txt

.PHONY: requirements
requirements:
	venv/bin/pip freeze > requirements.txt
.PHONY: setup-camera

all: playbooks install-collections 

PI_HOST = ansible@raspberrypi1.local

.PHONY: deploy
deploy:
	ansible-playbook \
		-i ./playbooks/inventory.ini \
		./playbooks/wand_reader/setup-wandreader.yaml
	$(MAKE) follow

follow:
	ssh $(PI_HOST) "sudo journalctl -u wand_reader.service -f"

restart:
	ssh $(PI_HOST) "sudo systemctl restart wand_reader.service"

debug:
	ssh $(PI_HOST) "sudo journalctl -u wand_reader.service -n 50 --no-pager"

get_snapshot:
	scp $(PI_HOST):/tmp/wand_startup.jpg ~/Desktop/
	open ~/Desktop/wand_startup.jpg

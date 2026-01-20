.PHONY: all install-collections playbooks

playbooks:
	ansible-playbook \
		-i playbooks/inventory.ini \
		playbooks/setup-raspberry-pi-node.yaml  
install-collections:
	ansible-galaxy collection install community.general

.PHONY: setup-python
setup-python:
	venv/bin/pip install -r requirements.txt

.PHONY: create-reqs
create-reqs:
	venv/bin/pip freeze > requirements.txt

all: playbooks install-collections

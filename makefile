.PHONY: all install-collections playbooks

playbooks:
	ansible-playbook \
		-i playbooks/inventory.ini \
		playbooks/setup-raspberry-pi-node.yaml  
install-collections:
	ansible-galaxy collection install community.general

all: playbooks install-collections

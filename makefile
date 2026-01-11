.PHONY: all playbooks

playbooks:
	for pb in playbooks/*.yaml; do \
		ansible-playbook -i playbooks/inventory.ini $$pb; \
	done

all: playbooks

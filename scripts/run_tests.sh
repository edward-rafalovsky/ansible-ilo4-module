#!/bin/bash

# Check for .env file
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    echo "Please copy .env.example to .env and update with your settings"
    exit 1
fi

# Build Docker image
docker build -t hpe-ilo-ssh-module .

# Run tests based on argument
case "$1" in
  "unit")
    docker run --rm -v $(pwd):/root/.ansible/collections/ansible_collections/hpe/ilo_ssh hpe-ilo-ssh-module python -m pytest tests/unit/
    ;;
  "integration")
    docker run --rm -v $(pwd):/root/.ansible/collections/ansible_collections/hpe/ilo_ssh --env-file .env hpe-ilo-ssh-module ansible-playbook -i tests/integration/inventory/hosts.yml tests/integration/playbooks/*.yml -v
    ;;
  "user")
    docker run --rm -v $(pwd):/root/.ansible/collections/ansible_collections/hpe/ilo_ssh --env-file .env hpe-ilo-ssh-module ansible-playbook -i tests/integration/inventory/hosts.yml tests/integration/playbooks/user_test.yml -v
    ;;
  "power")
    docker run --rm -v $(pwd):/root/.ansible/collections/ansible_collections/hpe/ilo_ssh --env-file .env hpe-ilo-ssh-module ansible-playbook -i tests/integration/inventory/hosts.yml tests/integration/playbooks/power_test.yml -v
    ;;
  "power_settings")
    docker run --rm -v $(pwd):/root/.ansible/collections/ansible_collections/hpe/ilo_ssh --env-file .env hpe-ilo-ssh-module ansible-playbook -i tests/integration/inventory/hosts.yml tests/integration/playbooks/power_settings_test.yml -v
    ;;
  "boot_settings")
    docker run --rm -v $(pwd):/root/.ansible/collections/ansible_collections/hpe/ilo_ssh --env-file .env hpe-ilo-ssh-module ansible-playbook -i tests/integration/inventory/hosts.yml tests/integration/playbooks/boot_settings_test.yml -v
    ;;
  "virtual_media")
    docker run --rm -v $(pwd):/root/.ansible/collections/ansible_collections/hpe/ilo_ssh --env-file .env hpe-ilo-ssh-module ansible-playbook -i tests/integration/inventory/hosts.yml tests/integration/playbooks/virtual_media_test.yml -v
    ;;
  "raid")
    docker run --rm -v $(pwd):/root/.ansible/collections/ansible_collections/hpe/ilo_ssh --env-file .env hpe-ilo-ssh-module ansible-playbook -i tests/integration/inventory/hosts.yml tests/integration/playbooks/raid_test.yml -v
    ;;
  "hostname")
    docker run --rm -v $(pwd):/root/.ansible/collections/ansible_collections/hpe/ilo_ssh --env-file .env hpe-ilo-ssh-module ansible-playbook -i tests/integration/inventory/hosts.yml tests/integration/playbooks/hostname_test.yml -v
    ;;
  *)
    echo "Usage: $0 {unit|integration|user|power|power_settings|boot_settings|virtual_media|raid|hostname}"
    exit 1
    ;;
esac 
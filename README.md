# HPE iLO SSH Module for Ansible

Ansible module collection for managing HPE iLO via SSH connection.

## Features

### Power Management
- Control server power state (on/off/reset/cold boot)
- Get current power state
- Configure power optimization settings:
  - Power Regulator modes (dynamic/max/min/os)
  - Auto Power On settings (delay/random/restore)

### Boot Settings
- Get current boot settings
- Set boot mode (UEFI/Legacy)
- Configure boot sources order
- Set one-time boot source (USB/Network/etc.)
- View and modify UEFI boot sources

### Virtual Media Management
- Mount/unmount ISO images
- Configure boot from virtual media
- Get virtual media status
- Support for CD/DVD devices

### User Management
- Create and delete user accounts
- Set and update user privileges
- Manage user passwords
- Verify user existence and privileges

### Enhanced RAID management:
  - Automatic detection of controller capabilities
  - Extended physical drive information including backplane and zone table data
  - Support for READ_BACKPLANE_INFO and READ_ZONE_TABLE commands
  - Skip unsupported operations with informative messages

## Requirements

- Python >= 3.6
- Ansible >= 2.9
- paramiko

## Installation

### Via ansible-galaxy

1. Create `requirements.yml`:
```yaml
collections:
  - name: hpe.ilo_ssh
    source: https://github.com/rafalovsky/ansible-ilo4-module.git
    type: git
```

2. Install the collection:
```bash
ansible-galaxy collection install -r requirements.yml
```

### Direct installation from git

```bash
ansible-galaxy collection install git+https://github.com/rafalovsky/ansible-ilo4-module.git
```

## Module Reference

### Common Parameters

All modules share these base parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| hostname | str | yes | iLO IP address or hostname |
| username | str | yes | Username for iLO connection |
| password | str | yes | Password for iLO connection |

### Power Management

#### Module: ilo_power

Control server power state.

##### Additional Parameters

| Parameter | Type | Required | Default | Choices | Description |
|-----------|------|----------|----------|----------|-------------|
| state | str | no | get | on, off, reset, cold_boot, get | Desired power state |
| force | bool | no | false | | Force power off without OS shutdown |

##### Example Usage

```yaml
# Get current power state
- name: Get power state
  hpe.ilo_ssh.ilo_power:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    state: get

# Power on server
- name: Power on server
  hpe.ilo_ssh.ilo_power:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    state: on

# Graceful shutdown
- name: Power off server gracefully
  hpe.ilo_ssh.ilo_power:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    state: off
    force: no
```

#### Module: ilo_power_settings

Configure power optimization settings.

##### Additional Parameters

| Parameter | Type | Required | Default | Choices | Description |
|-----------|------|----------|----------|----------|-------------|
| power_reg_mode | str | no | | dynamic, max, min, os | Power Regulator mode |
| auto_power | str | no | | on, 15, 30, 45, 60, random, restore, off | Auto Power On setting |

##### Example Usage

```yaml
# Set power regulator to dynamic mode
- name: Configure dynamic power optimization
  hpe.ilo_ssh.ilo_power_settings:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    power_reg_mode: dynamic

# Configure auto power on with delay
- name: Set auto power on delay
  hpe.ilo_ssh.ilo_power_settings:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    auto_power: "30"
```

### Boot Settings

#### Module: ilo_boot_settings

Manage server boot configuration.

##### Additional Parameters

| Parameter | Type | Required | Default | Choices | Description |
|-----------|------|----------|----------|----------|-------------|
| state | str | no | present | present, get | Operation to perform |
| boot_mode | str | no | | UEFI, Legacy | Boot mode to set |
| boot_sources | list | no | | | List of boot sources in desired order |
| one_time_boot | str | no | | none, usb, ip, smartstartLX, netdev1 | One-time boot source |

##### Example Usage

```yaml
# Get current boot settings
- name: Get current boot settings
  hpe.ilo_ssh.ilo_boot_settings:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    state: get

# Set UEFI boot mode
- name: Set UEFI boot mode
  hpe.ilo_ssh.ilo_boot_settings:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    boot_mode: UEFI
    state: present

# Configure one-time network boot
- name: Set one-time network boot
  hpe.ilo_ssh.ilo_boot_settings:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    one_time_boot: netdev1
    state: present
```

### Virtual Media Management

#### Module: ilo_virtual_media

Manage virtual media devices.

##### Additional Parameters

| Parameter | Type | Required | Default | Choices | Description |
|-----------|------|----------|----------|----------|-------------|
| state | str | no | present | present, absent, get | Operation to perform |
| device_type | str | no | cdrom | cdrom | Type of virtual media device |
| image_url | str | yes (if state=present) | | | URL of the image to mount |
| boot_on_next_reset | bool | no | false | | Boot from this device on next reset |

##### Return Values

The module returns a dictionary with:

```yaml
status:
  device_type: Type of virtual media device (str)
  image_url: URL of mounted image (str)
  connected: Whether device is connected (bool)
  boot_on_next_reset: Whether device will be used for boot (bool)
  write_protect: Whether media is write protected (bool)
  vm_applet: Whether VM applet is enabled (bool)
```

##### Example Usage

```yaml
# Get virtual media status
- name: Get virtual media status
  hpe.ilo_ssh.ilo_virtual_media:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    state: get

# Mount ISO image with boot option
- name: Mount ISO image
  hpe.ilo_ssh.ilo_virtual_media:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    device_type: cdrom
    image_url: "http://server/image.iso"
    boot_on_next_reset: true
    state: present
```

### User Management

#### Module: ilo_user

Manage iLO user accounts.

##### Additional Parameters

| Parameter | Type | Required | Default | Choices | Description |
|-----------|------|----------|----------|----------|-------------|
| state | str | no | present | present, absent | Whether user should exist |
| user_name | str | yes | | | Username to manage |
| user_password | str | yes (if creating) | | | User password |
| privileges | dict | no | {} | | User privileges |

Available privileges (all default to no):
```yaml
privileges:
  admin: yes/no              # Administrator rights
  config: yes/no             # iLO Settings
  remote_console: yes/no     # Remote Console
  virtual_media: yes/no      # Virtual Media
  virtual_power_and_reset: yes/no  # Power Management
```

##### Example Usage

```yaml
# Create user with minimal privileges
- name: Create iLO user
  hpe.ilo_ssh.ilo_user:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    user_name: "operator"
    user_password: "secure_password"
    privileges:
      remote_console: yes
      virtual_power_and_reset: yes
    state: present

# Update user privileges
- name: Update user privileges
  hpe.ilo_ssh.ilo_user:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    user_name: "existing_user"
    privileges:
      config: yes
      remote_console: yes
    state: present
```

### RAID Management

#### Module: ilo_raid

The RAID management module (`ilo_raid`) has been enhanced with the following features:

### Extended Storage Information
- Automatic detection of controller capabilities
- Detailed physical drive information including:
  - Drive bay mapping
  - Status monitoring
  - Backplane configuration
  - Zone table information
- Support for commands:
  - GET_EMBEDDED_HEALTH (enhanced parsing)
  - READ_BACKPLANE_INFO
  - READ_ZONE_TABLE

### Smart Operation Handling
- Automatic detection of supported operations
- Graceful handling of unsupported commands
- Informative messages about controller capabilities

### Example Usage

```yaml
# Get RAID configuration with extended information
- name: Get RAID configuration
  hpe.ilo_ssh.ilo_raid:
    hostname: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    state: get

# Get physical drives information
- name: Get physical drives
  hpe.ilo_ssh.ilo_raid:
    hostname: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    state: get_drives

# Create RAID volume (if supported)
- name: Create RAID volume
  hpe.ilo_ssh.ilo_raid:
    hostname: "{{ inventory_hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    state: present
    controller: "Smart Array P440ar"
    raid_level: "1"
    drives: 
      - "1I:1:1"
      - "1I:1:2"
    volume_name: "Data_Volume"
    size_gb: 500
```

### Return Values Update
The module now returns extended information in the `raid_info` dictionary:

```json
{
    "changed": false,
    "raid_info": {
        "controllers": [
            {
                "model": "Smart HBA H240ar",
                "status": "OK",
                "supported_commands": ["get", "get_drives"],
                "physical_drives": [
                    {
                        "label": "Port 1I Box 1 Bay 1",
                        "status": "OK",
                        "drive_bay": "01",
                        "capacity": "1.2TB"
                    }
                ],
                "backplane": {
                    "type_id": "1",
                    "sep_node_id": "0x500143801234567",
                    "bay_count": 8
                },
                "zone_table": {
                    "host_ports": [
                        {
                            "port": 1,
                            "bays": [1, 2]
                        }
                    ]
                }
            }
        ]
    },
    "msg": "Successfully retrieved RAID configuration"
}
```

## Security

### Using ansible-vault

1. Create an encrypted file:
```bash
ansible-vault create group_vars/all/vault.yml
```

2. Add variables:
```yaml
vault_ilo_host: "192.168.1.100"
vault_ilo_username: "admin"
vault_ilo_password: "password123"
```

3. Use in inventory:
```yaml
all:
  hosts:
    ilo_server:
      ansible_connection: local
      ilo_host: "{{ vault_ilo_host }}"
      ilo_username: "{{ vault_ilo_username }}"
      ilo_password: "{{ vault_ilo_password }}"
```

4. Run playbook with vault:
```bash
ansible-playbook playbook.yml --ask-vault-pass
```

### Using Environment Variables

1. Create `.env` file:
```bash
ILO_HOST="192.168.1.100"
ILO_USERNAME="admin"
ILO_PASSWORD="password123"
```

2. Use in playbook:
```yaml
- name: Manage iLO
  hpe.ilo_ssh.ilo_user:
    hostname: "{{ lookup('env', 'ILO_HOST') }}"
    username: "{{ lookup('env', 'ILO_USERNAME') }}"
    password: "{{ lookup('env', 'ILO_PASSWORD') }}"
    # ... other parameters ...
```

## Development

### Environment Setup

1. Clone repository:
```bash
git clone https://github.com/rafalovsky/ansible-ilo4-module.git
cd ansible-ilo4-module
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Testing

1. Run unit tests:
```bash
python -m pytest tests/unit/
```

2. Run integration tests:
```bash
./scripts/run_tests.sh
```

## License

MIT

## Author

Edward Rafalovsky (<edward.rafalovsky@gmail.com>)

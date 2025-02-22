#!/usr/bin/python

DOCUMENTATION = '''
module: ilo_boot_settings
short_description: Manage HPE iLO server boot settings
description:
    - Manage boot settings of HPE servers via iLO SSH interface
    - Configure boot mode (UEFI/Legacy)
    - Configure boot sources order
    - Set one-time boot source
    - Get current boot configuration
    - Changes to boot mode may require a system restart to take effect
    - Boot sources order can be set only for existing sources
    - Available boot sources may vary depending on server hardware configuration
    - One-time boot setting is automatically cleared after the next system boot
options:
    hostname:
        description: The iLO hostname or IP address
        required: true
        type: str
    username:
        description: The iLO username
        required: true
        type: str
    password:
        description: The iLO password
        required: true
        type: str
    boot_mode:
        description: Boot mode to set (UEFI or Legacy)
        required: false
        type: str
        choices: ['UEFI', 'Legacy']
    boot_sources:
        description: List of boot sources in desired order
        required: false
        type: list
        elements: str
    one_time_boot:
        description: One-time boot source
        required: false
        type: str
        choices: ['none', 'usb', 'ip', 'smartstartLX', 'netdev1']
    state:
        description: Operation to perform
        type: str
        default: present
        choices: ['present', 'get']
    reboot:
        description: Whether to reboot the server if required to apply boot mode changes
        type: bool
        default: false
'''

EXAMPLES = '''
- name: Get current boot settings
  hpe.ilo_ssh.ilo_boot_settings:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    state: get

- name: Set UEFI boot mode
  hpe.ilo_ssh.ilo_boot_settings:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    boot_mode: UEFI
    state: present

- name: Set USB as primary boot source
  hpe.ilo_ssh.ilo_boot_settings:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    boot_sources:
      - "Generic USB Boot"
    state: present

- name: Configure PXE boot order
  hpe.ilo_ssh.ilo_boot_settings:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    boot_mode: UEFI
    boot_sources:
      - "Generic USB Boot"
      - "Embedded LOM 1 Port 1 : HPE Ethernet 1Gb 4-port 331i Adapter - NIC (PXE IPv4)"
    state: present
'''

RETURN = '''
changed:
    description: Whether the boot settings were modified
    type: bool
    returned: always
msg:
    description: Status message
    type: str
    returned: always
settings:
    description: Current boot settings
    type: dict
    returned: always
    contains:
        boot_mode:
            description: Current boot mode (UEFI/Legacy)
            type: str
        pending_boot_mode:
            description: Pending boot mode that will be active after restart
            type: str
        boot_sources:
            description: List of current boot sources in order
            type: list
            elements: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hpe.ilo_ssh.plugins.module_utils.ilo_base import IloBaseModule
import time
import re
import os
import requests
import urllib3

class IloBootSettingsModule(IloBaseModule):
    def __init__(self):
        self.module = AnsibleModule(
            argument_spec=dict(
                hostname=dict(type='str', required=True),
                username=dict(type='str', required=True),
                password=dict(type='str', required=True, no_log=True),
                boot_mode=dict(type='str', required=False, choices=['UEFI', 'Legacy']),
                boot_sources=dict(type='list', elements='str', required=False),
                one_time_boot=dict(type='str', required=False, choices=['none', 'usb', 'ip', 'smartstartLX', 'netdev1']),
                state=dict(type='str', default='present', choices=['present', 'get']),
                reboot=dict(type='bool', default=False)
            ),
            supports_check_mode=True
        )
        
        super().__init__(self.module)
        
        self.hostname = self.module.params['hostname']
        self.username = self.module.params['username']
        self.password = self.module.params['password']
        self.boot_mode = self.module.params['boot_mode']
        self.boot_sources = self.module.params['boot_sources']
        self.one_time_boot = self.module.params['one_time_boot']
        self.state = self.module.params['state']
        self.reboot = self.module.params['reboot']

    def get_boot_settings(self):
        """Get current boot settings"""
        settings = {
            'boot_mode': None,
            'pending_boot_mode': None,
            'boot_sources': [],
            'one_time_boot': None
        }
        
        # Get boot mode settings
        command = "show /system1/bootconfig1"
        success, stdout, stderr = self.execute_command(command)
        if not success:
            self.module.fail_json(msg=f"Failed to get boot settings: {stderr}")
        self.log(f"Boot settings output: {stdout}")
        
        # Find boot mode
        boot_mode_match = re.search(r'oemhp_bootmode=(\w+)', stdout)
        if boot_mode_match:
            settings['boot_mode'] = boot_mode_match.group(1)
            self.log(f"Found boot_mode: {settings['boot_mode']}")
            
        # Find pending boot mode
        pending_mode_match = re.search(r'oemhp_pendingbootmode=(\w+)', stdout)
        if pending_mode_match:
            settings['pending_boot_mode'] = pending_mode_match.group(1)
            self.log(f"Found pending_boot_mode: {settings['pending_boot_mode']}")
            
        # Get one-time boot setting
        command = "onetimeboot"
        success, stdout, stderr = self.execute_command(command)
        if success:
            # Parse the output to get the actual setting
            match = re.search(r'one-time boot:\s*(.*?)(?:\r|\n|$)', stdout.lower())
            if match:
                boot_value = match.group(1).strip()
                # Convert the verbose output to our enum values
                if 'no one-time boot' in boot_value:
                    settings['one_time_boot'] = 'none'
                elif 'network device 1' in boot_value:
                    settings['one_time_boot'] = 'netdev1'
                elif 'intelligent provisioning' in boot_value:
                    settings['one_time_boot'] = 'ip'
                elif 'usb' in boot_value:
                    settings['one_time_boot'] = 'usb'
                elif 'smart start linux pe' in boot_value:
                    settings['one_time_boot'] = 'smartstartLX'
                else:
                    settings['one_time_boot'] = 'none'
            self.log(f"Found one_time_boot: {settings['one_time_boot']}")

        # Get boot sources and their order
        sources = []
        for i in range(1, 6):  # iLO typically has 5 boot sources
            success, stdout, stderr = self.execute_command(f'show /system1/bootconfig1/oemhp_uefibootsource{i}')
            if not success:
                continue
                
            self.log(f"Boot source {i} output:")
            self.log("-" * 40)
            self.log(stdout)
            self.log("-" * 40)
                
            # Find boot source description and order
            desc_match = re.search(r'oemhp_description=(.+)', stdout)
            order_match = re.search(r'bootorder=(\d+)', stdout)
            
            if desc_match and order_match:
                description = desc_match.group(1).strip()
                order = int(order_match.group(1))
                sources.append((description, order))
                self.log(f"Found boot source: {description} with order {order}")
                
        # Sort boot sources by order and extract only descriptions
        if sources:
            settings['boot_sources'] = [source[0] for source in sorted(sources, key=lambda x: x[1])]
            self.log(f"Found boot sources: {settings['boot_sources']}")

        self.log("=" * 40)
        self.log("Final settings:")
        self.log(str(settings))
        self.log("=" * 40)
        
        # Ensure we have valid values
        if settings['boot_mode'] is None and settings['pending_boot_mode'] is None:
            self.module.fail_json(msg=f"Failed to get boot mode settings from iLO response. Raw output: {stdout}")
            
        return settings

    def set_boot_sources(self, sources):
        """Set boot sources order"""
        if not sources:
            self.log("No boot sources specified, skipping")
            return False
            
        # Get initial settings
        initial_settings = self.get_boot_settings()
        self.log(f"Initial settings: {initial_settings}")
        
        # Check if sources are already in correct order
        for i, source in enumerate(sources):
            if i >= len(initial_settings['boot_sources']) or initial_settings['boot_sources'][i] != source:
                break
        else:
            self.log("Boot sources are already in desired order")
            return False
            
        # Get current boot sources mapping
        source_mapping = {}  # Maps source description to number
        for i in range(1, 6):  # iLO typically has 5 boot sources
            success, stdout, stderr = self.execute_command(f'show /system1/bootconfig1/oemhp_uefibootsource{i}', timeout=5)
            if not success:
                continue
                
            desc_match = re.search(r'oemhp_description=(.+)', stdout)
            if desc_match:
                description = desc_match.group(1).strip()
                source_mapping[description] = i
                
        # Set boot order for each source
        for order, source in enumerate(sources, 1):
            if source not in source_mapping:
                self.module.fail_json(msg=f"Boot source {source} not found in available sources: {list(source_mapping.keys())}")
                
            source_num = source_mapping[source]
            command = f"set /system1/bootconfig1/oemhp_uefibootsource{source_num} bootorder={order}"
            self.log(f"Executing command: {command}")
            success, stdout, stderr = self.execute_command(command, timeout=5)
            if not success:
                self.module.fail_json(msg=f"Failed to set boot order for source {source}: {stderr}")
            self.log(f"Command output: {stdout}")
            
        # Verify changes
        current_settings = self.get_boot_settings()
        self.log(f"Current settings: {current_settings}")
        
        # Check if specified sources are in correct order
        for i, source in enumerate(sources):
            if i >= len(current_settings['boot_sources']) or current_settings['boot_sources'][i] != source:
                self.module.fail_json(msg=f"Failed to set boot sources order. Source {source} is not at position {i}")
            
        return True

    def set_boot_mode(self, mode):
        """Set boot mode (UEFI/Legacy)"""
        if mode not in ['UEFI', 'Legacy']:
            self.module.fail_json(msg=f"Invalid boot mode: {mode}")
        
        initial_settings = self.get_boot_settings()
        self.log(f"Initial settings: {initial_settings}")
        
        # Check if mode is already set or pending
        if initial_settings['boot_mode'] == mode and not initial_settings['pending_boot_mode']:
            self.log(f"Boot mode is already set to {mode} with no pending changes")
            return False
            
        # If there's a pending change to a different mode, we need to change it
        if initial_settings['pending_boot_mode']:
            if initial_settings['pending_boot_mode'] == mode:
                self.log(f"Boot mode {mode} is already pending")
                if self.reboot:
                    self.log("Rebooting to apply pending changes")
                else:
                    self.log("Reboot required but not enabled")
                    return False
            else:
                self.log(f"Need to change pending boot mode from {initial_settings['pending_boot_mode']} to {mode}")
        elif initial_settings['boot_mode'] != mode:
            self.log(f"Need to change boot mode from {initial_settings['boot_mode']} to {mode}")
        else:
            self.log(f"Boot mode is already set to {mode}")
            return False
        
        # Create RIBCL XML
        xml = f"""<?xml version="1.0"?>
<RIBCL VERSION="2.0">
<LOGIN USER_LOGIN="{self.username}" PASSWORD="{self.password}">
<SERVER_INFO MODE="write">
<SET_PENDING_BOOT_MODE VALUE="{mode}"/>
</SERVER_INFO>
</LOGIN>
</RIBCL>"""

        try:
            # Disable SSL warnings
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Send XML via RIBCL API with timeout
            response = requests.post(
                f"https://{self.hostname}/ribcl",
                data=xml,
                verify=False,
                auth=(self.username, self.password),
                headers={'Content-Type': 'application/xml'},
                timeout=10
            )
            
            self.log(f"Response status code: {response.status_code}")
            
            if response.status_code != 200:
                self.module.fail_json(msg=f"Server returned status code {response.status_code}")
            
            response_text = response.content.decode('utf-8', errors='ignore')
            self.log(f"Response XML:\n{response_text}")
            
            # Check for success in RIBCL response
            if 'STATUS="0x0000"' not in response_text:
                error_msg = "Unknown error"
                match = re.search(r'MESSAGE="([^"]*)"', response_text)
                if match:
                    error_msg = match.group(1)
                self.module.fail_json(msg=f"RIBCL command failed: {error_msg}")
            
            # Verify changes
            current_settings = self.get_boot_settings()
            self.log(f"Current settings: {current_settings}")
            
            # Check if mode is set or pending
            if current_settings['boot_mode'] != mode and current_settings['pending_boot_mode'] != mode:
                self.module.fail_json(msg=f"Failed to set boot mode. Expected {mode} to be set or pending, got {current_settings['boot_mode']} (pending: {current_settings['pending_boot_mode']})")
            
            # If reboot is enabled and boot mode is pending, reboot the server
            if self.reboot and current_settings['pending_boot_mode'] == mode:
                self.log("Rebooting server to apply boot mode changes")
                command = "power reset"
                success, stdout, stderr = self.execute_command(command, timeout=10)
                if not success:
                    self.module.fail_json(msg=f"Failed to reboot server: {stderr}")
                self.log(f"Server reboot initiated: {stdout}")
                
                # Wait for reboot to complete
                # Initial wait reduced to 30 seconds as iLO usually responds by then
                time.sleep(30)
                
                # Try to verify settings up to 3 times with short intervals
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        final_settings = self.get_boot_settings()
                        
                        # Check if boot mode is set correctly and no pending changes
                        if final_settings['boot_mode'] == mode and not final_settings['pending_boot_mode']:
                            self.log("Boot mode change completed successfully")
                            return True
                            
                        self.log(f"Boot mode not yet applied (attempt {attempt + 1}/{max_retries}): {final_settings}")
                        if attempt < max_retries - 1:
                            time.sleep(5)  # Short wait between attempts
                            
                    except Exception as e:
                        self.log(f"Failed to verify settings (attempt {attempt + 1}/{max_retries}): {str(e)}")
                        if attempt < max_retries - 1:
                            time.sleep(5)
                
                self.module.fail_json(msg=f"Failed to apply boot mode change after reboot. Current settings: {final_settings}")
            
            return True
            
        except Exception as e:
            self.module.fail_json(msg=f"Failed to set boot mode: {str(e)}")
            return False

    def set_one_time_boot(self, source):
        """Set one-time boot source"""
        if not source:
            self.log("No one-time boot source specified, skipping")
            return False
            
        # Get initial settings
        initial_settings = self.get_boot_settings()
        self.log(f"Initial settings: {initial_settings}")
        
        # Check if source is already set
        if initial_settings['one_time_boot'] == source:
            self.log(f"One-time boot source is already set to {source}")
            return False
            
        # Set one-time boot source using ONETIMEBOOT command
        command = f"onetimeboot {source}"
        self.log(f"Executing command: {command}")
        success, stdout, stderr = self.execute_command(command, timeout=5)
        if not success:
            self.module.fail_json(msg=f"Failed to set one-time boot source: {stderr}")
        self.log(f"Command output: {stdout}")
        
        # Get current settings to verify
        command = "onetimeboot"
        success, stdout, stderr = self.execute_command(command, timeout=5)
        if not success:
            self.module.fail_json(msg=f"Failed to verify one-time boot source: {stderr}")
            
        # Parse the current setting from output
        match = re.search(r'one-time boot:\s*(.*?)(?:\r|\n|$)', stdout.lower())
        if not match:
            self.module.fail_json(msg=f"Failed to parse one-time boot output: {stdout}")
            
        boot_value = match.group(1).strip()
        current_source = None
        
        # Convert the verbose output to our enum values
        if 'no one-time boot' in boot_value:
            current_source = 'none'
        elif 'network device 1' in boot_value:
            current_source = 'netdev1'
        elif 'intelligent provisioning' in boot_value:
            current_source = 'ip'
        elif 'usb' in boot_value:
            current_source = 'usb'
        elif 'smart start linux pe' in boot_value:
            current_source = 'smartstartLX'
        else:
            current_source = 'none'
            
        if source != current_source:
            self.module.fail_json(msg=f"Failed to set one-time boot source. Expected {source}, got {current_source} (raw: {boot_value})")
            
        return True

    def run_module(self):
        """Run the module"""
        result = dict(
            changed=False,
            msg='',
            settings=None
        )

        # Get current settings
        current_settings = self.get_boot_settings()
        self.log(f"Current settings: {current_settings}")

        if self.state == 'get':
            result['settings'] = current_settings
            result['msg'] = 'Successfully retrieved boot settings'
            self.module.exit_json(**result)
            return

        # Set boot mode if specified
        if self.boot_mode:
            self.log(f"Setting boot mode to {self.boot_mode}")
            changed = self.set_boot_mode(self.boot_mode)
            result['changed'] = result['changed'] or changed
            if changed:
                result['msg'] = f"Boot mode set to {self.boot_mode}"

        # Set boot sources if specified
        if self.boot_sources:
            self.log(f"Setting boot sources to {self.boot_sources}")
            changed = self.set_boot_sources(self.boot_sources)
            result['changed'] = result['changed'] or changed
            if changed:
                result['msg'] += f"{'; ' if result['msg'] else ''}Boot sources order updated"

        # Set one-time boot if specified
        if self.one_time_boot:
            self.log(f"Setting one-time boot source to {self.one_time_boot}")
            changed = self.set_one_time_boot(self.one_time_boot)
            result['changed'] = result['changed'] or changed
            if changed:
                result['msg'] += f"{'; ' if result['msg'] else ''}One-time boot source set"

        # Get final settings
        result['settings'] = self.get_boot_settings()
        self.log(f"Final settings: {result['settings']}")

        if not result['changed']:
            result['msg'] = 'No changes required'

        self.module.exit_json(**result)

def main():
    module = IloBootSettingsModule()
    module.run_module()

if __name__ == '__main__':
    main() 
#!/usr/bin/python

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hpe.ilo_ssh.plugins.module_utils.ilo_base import IloBaseModule

DOCUMENTATION = '''
---
module: ilo_power
short_description: Manage HPE iLO server power state
description:
    - Manage power state of HPE servers via iLO
    - Power on, power off, reset, cold boot
    - Get current power state
options:
    hostname:
        description: The hostname or IP address of the iLO interface
        required: true
        type: str
    username:
        description: The username to connect to iLO
        required: true
        type: str
    password:
        description: The password to connect to iLO
        required: true
        type: str
    state:
        description: 
            - Desired power state
            - on - Power on the server
            - off - Power off the server immediately
            - reset - Reset the server (warm boot)
            - cold_boot - Power off then power on (cold boot)
            - get - Get current power state (default)
        choices: [ on, off, reset, cold_boot, get ]
        default: get
        type: str
    force:
        description: Force power off without OS shutdown
        type: bool
        default: false
'''

EXAMPLES = '''
# Get server power state
- name: Get power state
  ilo_power:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    state: get

# Power on server
- name: Power on server
  ilo_power:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    state: on

# Graceful shutdown
- name: Power off server gracefully
  ilo_power:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    state: off
    force: no

# Force power off
- name: Force power off server
  ilo_power:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    state: off
    force: yes

# Reset server
- name: Reset server
  ilo_power:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    state: reset

# Cold boot server
- name: Cold boot server
  ilo_power:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    state: cold_boot
'''

class IloPowerModule(IloBaseModule):
    def __init__(self, module):
        super().__init__(module)
        self.state = module.params['state']
        self.force = module.params['force']
        
        # Mapping of states to commands
        self.power_commands = {
            'on': 'power on',
            'off': 'power off hard' if self.force else 'power off',
            'reset': 'power reset',
            'cold_boot': 'power off hard; power on'
        }

    def get_power_state(self):
        """Get current power state."""
        success, stdout, stderr = self.execute_command("power")
        if not success:
            self.module.fail_json(msg=f"Failed to get power state: {stderr}")
        
        output = stdout.lower()
        if "server power is currently: off" in output:
            return "off"
        elif "server power is currently: on" in output:
            return "on"
        else:
            self.module.fail_json(msg=f"Failed to parse power state from output: {stdout}")

    def power_on(self):
        """Power on the server."""
        if self.get_power_state() == "on":
            return False
        success, stdout, stderr = self.execute_command("power on")
        if not success:
            self.module.fail_json(msg=f"Failed to power on server: {stderr}")
        time.sleep(5)  # Wait for power on command to take effect
        return True

    def power_off(self):
        """Power off the server."""
        if self.get_power_state() == "off":
            return False
        command = "power off hard" if self.force else "power off"
        success, stdout, stderr = self.execute_command(command)
        if not success:
            self.module.fail_json(msg=f"Failed to power off server: {stderr}")
        time.sleep(5)  # Wait for power off command to take effect
        return True

    def reset(self):
        """Reset the server."""
        success, stdout, stderr = self.execute_command("power reset")
        if not success:
            self.module.fail_json(msg=f"Failed to reset server: {stderr}")
        time.sleep(5)  # Wait for reset command to take effect
        return True

    def cold_boot(self):
        """Perform a cold boot of the server."""
        success, stdout, stderr = self.execute_command("power off hard")
        if not success:
            self.module.fail_json(msg=f"Failed to power off server for cold boot: {stderr}")
        time.sleep(10)  # Wait for hard power off
        
        success, stdout, stderr = self.execute_command("power on")
        if not success:
            self.module.fail_json(msg=f"Failed to power on server after cold boot: {stderr}")
        time.sleep(5)  # Wait for power on
        return True

    def wait_for_power_state(self, target_state, timeout=300):
        """Wait for server to reach target power state."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            current_state = self.get_power_state()
            if current_state == target_state:
                return True
            time.sleep(10)
        raise Exception(f"Timeout waiting for power state {target_state}")

    def run_module(self):
        """Run the module."""
        result = dict(
            changed=False,
            power_state=None
        )

        # Get current power state
        current_state = self.get_power_state()
        result["power_state"] = current_state

        if self.state == "get":
            return result

        try:
            if self.state == "on" and current_state != "on":
                result["changed"] = self.power_on()
                self.wait_for_power_state("on")
                result["power_state"] = "on"
            elif self.state == "off" and current_state != "off":
                result["changed"] = self.power_off()
                self.wait_for_power_state("off")
                result["power_state"] = "off"
            elif self.state == "reset":
                result["changed"] = self.reset()
                result["power_state"] = "reset_initiated"
            elif self.state == "cold_boot":
                result["changed"] = self.cold_boot()
                self.wait_for_power_state("on")
                result["power_state"] = "on"
        except Exception as e:
            self.module.fail_json(msg=str(e))

        return result

def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(required=True, type='str'),
            username=dict(required=True, type='str'),
            password=dict(required=True, type='str', no_log=True),
            state=dict(default='get', choices=['on', 'off', 'reset', 'cold_boot', 'get'], type='str'),
            force=dict(default=False, type='bool')
        )
    )
    
    ilo_power = IloPowerModule(module)
    result = ilo_power.run_module()
    
    module.exit_json(**result)

if __name__ == '__main__':
    main() 
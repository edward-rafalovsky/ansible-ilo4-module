#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hpe.ilo_ssh.plugins.module_utils.ilo_base import IloBaseModule

DOCUMENTATION = '''
---
module: ilo_power_settings
short_description: Manage HPE iLO power optimization settings
description:
    - Configure power regulator mode and automatic power on settings
    - Get current power optimization configuration
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
    power_reg_mode:
        description: 
            - Set Power Regulator mode
            - dynamic - Automatically optimize for power or performance
            - max - Maximum performance mode
            - min - Minimum power usage mode
            - os - Operating system control mode
        choices: [ dynamic, max, min, os ]
        type: str
    auto_power:
        description:
            - Configure server automatic power on setting
            - on - Turn on with minimum delay
            - '15/30/45/60' - Turn on with specified delay (seconds)
            - random - Turn on with random delay
            - restore - Restore last power state
            - off - Disable automatic power on
        choices: [ on, '15', '30', '45', '60', random, restore, off ]
        type: str
'''

EXAMPLES = '''
# Set power regulator to dynamic mode
- name: Configure dynamic power optimization
  ilo_power_settings:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    power_reg_mode: dynamic

# Configure auto power on with 30 second delay
- name: Set auto power on delay
  ilo_power_settings:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    auto_power: '30'

# Get current power settings
- name: Get power optimization settings
  ilo_power_settings:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
  register: power_settings
'''

class IloPowerSettingsModule(IloBaseModule):
    def __init__(self, module):
        super().__init__(module)
        self.power_reg_mode = module.params['power_reg_mode']
        self.auto_power = module.params['auto_power']

    def get_power_settings(self):
        """Get current power optimization settings."""
        success, stdout, stderr = self.execute_command("show /system1/oemhp_power1")
        if not success:
            self.module.fail_json(msg=f"Failed to get power settings: {stderr}")
        
        self.module.log(f"Power settings output: {stdout}")
        
        settings = {}
        in_properties = False
        
        for line in stdout.splitlines():
            line = line.strip()
            
            if line == "Properties":
                in_properties = True
                continue
            elif line and line[0] == "/" or line == "Targets" or line == "Verbs":
                in_properties = False
                continue
                
            if in_properties and "=" in line:
                key, value = line.split("=", 1)
                if key == "oemhp_powerreg":
                    settings['power_reg_mode'] = value.strip().lower()
                elif key == "oemhp_auto_pwr":
                    value = value.strip().lower()
                    # Convert "on (X seconds)" to "X"
                    if "seconds" in value:
                        import re
                        match = re.search(r'on \((\d+) seconds\)', value)
                        if match:
                            value = match.group(1)
                    settings['auto_power'] = value
        
        self.module.log(f"Parsed settings: {settings}")
        return settings

    def set_power_regulator(self):
        """Configure Power Regulator mode."""
        if not self.power_reg_mode:
            return False
            
        success, stdout, stderr = self.execute_command(f"set /system1/oemhp_power1 oemhp_powerreg={self.power_reg_mode}")
        if not success:
            self.module.fail_json(msg=f"Failed to set power regulator mode: {stderr}")
        return True

    def set_auto_power(self):
        """Configure automatic power on settings."""
        if not self.auto_power:
            return False
            
        success, stdout, stderr = self.execute_command(f"set /system1/oemhp_power1 oemhp_auto_pwr={self.auto_power}")
        if not success:
            self.module.fail_json(msg=f"Failed to set auto power settings: {stderr}")
        return True

    def run_module(self):
        """Run the module."""
        result = dict(
            changed=False,
            settings=None
        )

        # Get current settings
        current_settings = self.get_power_settings()
        result['settings'] = current_settings

        # Apply changes if requested
        if self.power_reg_mode:
            if current_settings.get('power_reg_mode') != self.power_reg_mode:
                result['changed'] |= self.set_power_regulator()
                current_settings['power_reg_mode'] = self.power_reg_mode

        if self.auto_power:
            if current_settings.get('auto_power') != self.auto_power:
                result['changed'] |= self.set_auto_power()
                current_settings['auto_power'] = self.auto_power

        result['settings'] = current_settings
        return result

def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(required=True, type='str'),
            username=dict(required=True, type='str'),
            password=dict(required=True, type='str', no_log=True),
            power_reg_mode=dict(type='str', choices=['dynamic', 'max', 'min', 'os']),
            auto_power=dict(type='str', choices=['on', '15', '30', '45', '60', 'random', 'restore', 'off'])
        )
    )
    
    ilo_power_settings = IloPowerSettingsModule(module)
    result = ilo_power_settings.run_module()
    
    module.exit_json(**result)

if __name__ == '__main__':
    main() 
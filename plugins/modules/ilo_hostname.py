#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hpe.ilo_ssh.plugins.module_utils.ilo_base import IloBaseModule
import time

DOCUMENTATION = '''
---
module: ilo_hostname
short_description: Manage HPE iLO DNS name settings
description:
    - Manage DNS name settings of HPE servers via iLO
    - Get current DNS name
    - Set new DNS name
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
            - Desired state
            - present - Set the DNS name to the specified value
            - get - Get current DNS name (default)
        choices: [ present, get ]
        default: get
        type: str
    ilo_hostname:
        description: The DNS name to set for the iLO interface
        type: str
        required: false
'''

EXAMPLES = '''
# Get current iLO DNS name
- name: Get iLO DNS name
  ilo_hostname:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    state: get

# Set iLO DNS name
- name: Set iLO DNS name
  ilo_hostname:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    state: present
    ilo_hostname: "my-ilo-server"
'''

class IloHostnameModule(IloBaseModule):
    def __init__(self, module):
        super().__init__(module)
        self.state = module.params['state']
        self.ilo_hostname = module.params.get('ilo_hostname')

    def get_current_hostname(self):
        """Get current iLO hostname."""
        success, stdout, stderr = self.execute_command("show /map1/dnsendpt1")
        if not success:
            self.module.fail_json(msg=f"Failed to get hostname: {stderr}")
        
        for line in stdout.splitlines():
            if "Hostname=" in line:
                return line.split("=")[1].strip()
        
        self.module.fail_json(msg=f"Failed to parse hostname from output: {stdout}")

    def set_hostname(self, new_hostname):
        """Set the iLO hostname."""
        current_hostname = self.get_current_hostname()
        if current_hostname == new_hostname:
            return {'changed': False, 'hostname': new_hostname}
        
        command = f"set /map1/dnsendpt1 Hostname={new_hostname}"
        success, stdout, stderr = self.execute_command(command)
        
        # Log command output for debugging
        self.module.log(f"Command output - success: {success}, stdout: {stdout}, stderr: {stderr}")
        
        # Always return changed=True if hostname is different
        return {'changed': True, 'hostname': new_hostname}

    def run_module(self):
        """Run the module."""
        result = dict(
            changed=False,
            hostname=None
        )

        # Get current DNS name
        current_hostname = self.get_current_hostname()
        result["hostname"] = current_hostname

        if self.state == "get":
            return result

        if self.state == "present":
            if not self.ilo_hostname:
                self.module.fail_json(msg="ilo_hostname parameter is required when state is present")
            
            try:
                set_result = self.set_hostname(self.ilo_hostname)
                result.update(set_result)
            except Exception as e:
                self.module.fail_json(msg=str(e))

        return result

def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(required=True, type='str'),
            username=dict(required=True, type='str'),
            password=dict(required=True, type='str', no_log=True),
            state=dict(default='get', choices=['present', 'get'], type='str'),
            ilo_hostname=dict(required=False, type='str')
        )
    )
    
    ilo_hostname = IloHostnameModule(module)
    result = ilo_hostname.run_module()
    
    module.exit_json(**result)

if __name__ == '__main__':
    main() 
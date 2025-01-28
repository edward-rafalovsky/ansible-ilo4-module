#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hpe.ilo_ssh.plugins.module_utils.ilo_base import IloBaseModule
import time

DOCUMENTATION = '''
---
module: ilo_user
short_description: Manage HPE iLO users
description:
    - Manage users on HPE iLO devices
    - Allows creating, updating, and deleting users
    - Supports setting user privileges
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
    user_name:
        description: The name of the user to manage
        required: true
        type: str
    user_password:
        description: The password for the user (required when creating a new user)
        required: false
        type: str
    state:
        description: Whether the user should exist or not
        choices: [ present, absent ]
        default: present
        type: str
    privileges:
        description: 
            - User privileges
            - admin - Maps to oemhp_admin privilege
            - config - Maps to oemhp_config privilege
            - remote_console - Maps to oemhp_rc privilege
            - virtual_media - Maps to oemhp_vm privilege
            - virtual_power_and_reset - Maps to oemhp_power privilege
        required: false
        type: dict
        default: {}
        suboptions:
            admin:
                description: Administrator privileges
                type: bool
                default: no
            config:
                description: Configure iLO Settings privileges
                type: bool
                default: no
            remote_console:
                description: Remote Console privileges
                type: bool
                default: no
            virtual_media:
                description: Virtual Media privileges
                type: bool
                default: no
            virtual_power_and_reset:
                description: Virtual Power and Reset privileges
                type: bool
                default: no
'''

EXAMPLES = '''
# Create user with minimal privileges
- name: Create iLO user with minimal privileges
  hpe.ilo_ssh.ilo_user:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    user_name: "newuser"
    user_password: "newpassword"
    state: present
    privileges:
      remote_console: yes

# Create user with full administrator privileges
- name: Create iLO admin user
  hpe.ilo_ssh.ilo_user:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    user_name: "admin_user"
    user_password: "admin_password"
    state: present
    privileges:
      admin: yes
      config: yes
      remote_console: yes
      virtual_media: yes
      virtual_power_and_reset: yes

# Update existing user privileges
- name: Update user privileges
  hpe.ilo_ssh.ilo_user:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    user_name: "existing_user"
    state: present
    privileges:
      remote_console: yes
      virtual_power_and_reset: yes

# Remove user
- name: Remove iLO user
  hpe.ilo_ssh.ilo_user:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    user_name: "user_to_remove"
    state: absent
'''

class IloUserModule(IloBaseModule):
    def __init__(self, module):
        super().__init__(module)
        self.user_name = module.params['user_name']
        self.user_password = module.params.get('user_password')
        self.state = module.params['state']
        self.privileges = module.params.get('privileges', {})
        
        # Mapping of Ansible privileges to iLO privileges
        self.privilege_map = {
            'admin': 'admin',
            'config': 'config',
            'remote_console': 'oemhp_rc',
            'virtual_media': 'oemhp_vm',
            'virtual_power_and_reset': 'oemhp_power'
        }

    def user_exists(self):
        """
        Check if user exists using pure SSH command
        """
        self.log(f"Checking if user {self.user_name} exists")
        
        # Get list of all users
        success, stdout, stderr = self.execute_command("show /map1/accounts1")
        if not success:
            self.module.fail_json(msg=f"Failed to get user list: {stderr}")
            
        self.log(f"Show accounts raw output: {repr(stdout)}")
        
        # Check if user exists in the list
        user_exists = False
        if "Targets" in stdout:
            # Parse command output
            try:
                # Split into lines and clean special characters
                lines = [line.strip() for line in stdout.replace('\r', '').split('\n') if line.strip()]
                self.log(f"Cleaned lines: {lines}")
                
                # Find Targets section
                in_targets = False
                users = []
                for line in lines:
                    if "Targets" in line:
                        in_targets = True
                        continue
                    if in_targets:
                        if "Properties" in line:
                            break
                        if line.strip() and not line.strip().isdigit():
                            users.append(line.strip())
                
                self.log(f"Found users: {users}")
                user_exists = any(self.user_name.lower() == user.lower() for user in users)
                self.log(f"User exists check: {user_exists} (comparing {self.user_name.lower()} with {[u.lower() for u in users]})")
                
            except Exception as e:
                self.log(f"Error parsing user list: {str(e)}")
                self.module.fail_json(msg=f"Error parsing user list: {str(e)}")
            
        self.log(f"User {self.user_name} {'exists' if user_exists else 'does not exist'}")
        return user_exists

    def create_user(self):
        self.log("Starting create_user operation")
        
        # Check if user exists
        exists = self.user_exists()
        self.log(f"User exists check result: {exists}")
        
        # If user exists and has privileges to update
        if exists and self.privileges:
            self.log(f"User exists and has privileges to update: {self.privileges}")
            changed = self.set_privileges()
            self.log(f"Privileges update result: {changed}")
            return changed
            
        # If user exists but no privileges to update
        if exists:
            self.log("User exists but no privileges to update")
            return False
            
        # If creating user, check for password
        if not self.user_password:
            self.log("Password required but not provided")
            self.module.fail_json(msg="user_password is required when creating a user")
        
        # Create user
        self.log(f"Creating new user: {self.user_name}")
        
        # Form list of privileges
        self.log(f"Input privileges: {self.privileges}")
        self.log(f"Privilege map: {self.privilege_map}")
        
        ilo_privileges = []
        for priv, value in self.privileges.items():
            self.log(f"Processing privilege {priv}: {value}")
            if value:
                mapped_priv = self.privilege_map.get(priv)
                self.log(f"Mapped {priv} to {mapped_priv}")
                if mapped_priv:
                    ilo_privileges.append(mapped_priv)
        
        # Create user with correct command format
        command = f"create /map1/accounts1 username={self.user_name} password={self.user_password}"
        if ilo_privileges:
            command += f" group={','.join(ilo_privileges)}"
            self.log(f"Added privileges to command: {','.join(ilo_privileges)}")
        
        self.log(f"Final command: {command}")
        success, stdout, stderr = self.execute_command(command)
        
        self.log(f"Create command result:")
        self.log(f"Success: {success}")
        self.log(f"Output: {repr(stdout)}")
        self.log(f"Errors: {repr(stderr)}")
        
        if not success or "status=0" not in stdout:
            self.module.fail_json(msg=f"Failed to create user. Command output: {stdout}, Error: {stderr}")
            return False
            
        # Wait for iLO to process the command
        time.sleep(5)
            
        # Check user list after creation
        success, stdout, stderr = self.execute_command("show /map1/accounts1")
        self.log(f"Directory contents after user creation:\n{repr(stdout)}")
            
        # Verify user was created
        if not self.user_exists():
            self.log("User creation succeeded but user does not exist")
            self.module.fail_json(msg=f"User creation failed. Command output: {stdout}, Error: {stderr}")
            return False
            
        return True

    def delete_user(self):
        command = f"delete /map1/accounts1/{self.user_name}"
        success, stdout, stderr = self.execute_command(command)
        return success

    def set_privileges(self):
        self.log(f"Setting privileges: {self.privileges}")
        
        # Get current privileges
        success, stdout, stderr = self.execute_command(f"show -a /map1/accounts1/{self.user_name}")
        self.log(f"Current privileges - success: {success}, stdout: {stdout}, stderr: {stderr}")
        
        if not success:
            self.module.fail_json(msg=f"Failed to get current privileges: {stderr}")
        
        # Form list of privileges
        ilo_privileges = []
        for priv, value in self.privileges.items():
            if value:
                mapped_priv = self.privilege_map.get(priv)
                if mapped_priv:
                    ilo_privileges.append(mapped_priv)
        
        if not ilo_privileges:
            return False
        
        # Set privileges in one command
        command = f"set /map1/accounts1/{self.user_name} group={','.join(ilo_privileges)}"
        success, stdout, stderr = self.execute_command(command)
        
        self.log(f"Set privileges result - success: {success}, stdout: {stdout}, stderr: {stderr}")
        
        if not success:
            self.module.fail_json(msg=f"Failed to set privileges: {stderr}")
        
        return "status=0" in stdout

def main():
    module_args = dict(
        hostname=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        user_name=dict(type='str', required=True),
        user_password=dict(type='str', required=False, no_log=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        privileges=dict(type='dict', default={})
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    ilo_user = IloUserModule(module)
    
    result = dict(
        changed=False,
        stdout=[],
        stderr=[]
    )

    try:
        user_exists = ilo_user.user_exists()

        if module.check_mode:
            result['changed'] = (
                (module.params['state'] == 'present' and not user_exists) or
                (module.params['state'] == 'absent' and user_exists)
            )
            module.exit_json(**result)

        if module.params['state'] == 'present':
            # Try to create user or update privileges
            changed = ilo_user.create_user()
            result['changed'] = changed
            if changed:
                if user_exists:
                    result['msg'] = f"User {module.params['user_name']} privileges updated"
                else:
                    result['msg'] = f"User {module.params['user_name']} created successfully"
            else:
                result['msg'] = f"User {module.params['user_name']} already exists with correct settings"
        else:
            if user_exists:
                if ilo_user.delete_user():
                    result['changed'] = True
                    result['msg'] = f"User {module.params['user_name']} deleted successfully"

    except Exception as e:
        module.fail_json(msg=str(e))
    finally:
        ilo_user.disconnect()

    module.exit_json(**result)

if __name__ == '__main__':
    main() 
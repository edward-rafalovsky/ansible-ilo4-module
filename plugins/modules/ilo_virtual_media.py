#!/usr/bin/python

DOCUMENTATION = '''
module: ilo_virtual_media
short_description: Manage HPE iLO Virtual Media devices
description:
    - Manage Virtual Media devices via iLO SSH interface
    - Mount/unmount ISO images
    - Connect/disconnect virtual media devices
    - Get current virtual media status
    - Support for CD-ROM devices
    - Changes take effect immediately
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
    device_type:
        description: Type of virtual media device
        required: false
        type: str
        choices: ['cdrom']
        default: cdrom
    image_url:
        description: URL of the image to mount (supported protocols: http, https, nfs)
        required: false
        type: str
    boot_on_next_reset:
        description: Whether to boot from this device on next server reset
        required: false
        type: bool
        default: false
    state:
        description: Operation to perform
        type: str
        default: present
        choices: ['present', 'absent', 'get']
'''

EXAMPLES = '''
- name: Get virtual media status
  hpe.ilo_ssh.ilo_virtual_media:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    state: get

- name: Mount ISO image with boot option
  hpe.ilo_ssh.ilo_virtual_media:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    device_type: cdrom
    image_url: "http://server/image.iso"
    boot_on_next_reset: true
    state: present

- name: Unmount virtual media
  hpe.ilo_ssh.ilo_virtual_media:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    device_type: cdrom
    state: absent
'''

RETURN = '''
changed:
    description: Whether the virtual media state was modified
    type: bool
    returned: always
msg:
    description: Status message
    type: str
    returned: always
status:
    description: Current virtual media status
    type: dict
    returned: always
    contains:
        device_type:
            description: Type of virtual media device
            type: str
        image_url:
            description: URL of mounted image
            type: str
        connected:
            description: Whether device is connected
            type: bool
        boot_on_next_reset:
            description: Whether device will be used for boot on next reset
            type: bool
        write_protect:
            description: Whether media is write protected
            type: bool
        vm_applet:
            description: Whether VM applet is enabled
            type: bool
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hpe.ilo_ssh.plugins.module_utils.ilo_base import IloBaseModule
import time
import re

class IloVirtualMediaModule(IloBaseModule):
    def __init__(self):
        self.module = AnsibleModule(
            argument_spec=dict(
                hostname=dict(type='str', required=True),
                username=dict(type='str', required=True),
                password=dict(type='str', required=True, no_log=True),
                device_type=dict(type='str', required=False, choices=['cdrom'], default='cdrom'),
                image_url=dict(type='str', required=False),
                boot_on_next_reset=dict(type='bool', required=False, default=False),
                state=dict(type='str', default='present', choices=['present', 'absent', 'get'])
            ),
            supports_check_mode=True,
            required_if=[
                ('state', 'present', ['image_url'])
            ]
        )
        
        super().__init__(self.module)
        
        self.hostname = self.module.params['hostname']
        self.username = self.module.params['username']
        self.password = self.module.params['password']
        self.device_type = self.module.params['device_type']
        self.image_url = self.module.params['image_url']
        self.boot_on_next_reset = self.module.params['boot_on_next_reset']
        self.state = self.module.params['state']

    def get_virtual_media_status(self):
        """Get current virtual media status."""
        command = f"vm {self.device_type} get"
        success, stdout, stderr = self.execute_command(command)
        if not success:
            self.module.fail_json(msg=f"Failed to get virtual media status: {stderr}")
        
        self.log(f"=== Command output START ===\n{stdout}\n=== Command output END ===")
        
        status = {
            "device_type": self.device_type,
            "image_url": None,
            "connected": False,
            "boot_on_next_reset": False,
            "write_protect": False,
            "vm_applet": False
        }
        
        for line in stdout.splitlines():
            line = line.strip()
            self.log(f"Processing line: [{line}]")
            
            if "=" in line:
                key, value = [part.strip() for part in line.split("=", 1)]
                self.log(f"Found key-value pair: key=[{key}] value=[{value}]")
                
                if key == "Image URL" and value.lower() != "none":
                    status["image_url"] = value
                    self.log(f"Setting image_url to: {value}")
                elif key == "Image Connected":
                    status["connected"] = value.lower() == "yes"
                    self.log(f"Setting connected to: {value.lower() == 'yes'}")
                elif key == "Boot Option":
                    status["boot_on_next_reset"] = value.lower() in ["boot_once", "boot_always"]
                    self.log(f"Setting boot_on_next_reset to: {value.lower() in ['boot_once', 'boot_always']}")
                elif key == "Write Protect":
                    status["write_protect"] = value.lower() == "yes"
                    self.log(f"Setting write_protect to: {value.lower() == 'yes'}")
                elif key == "VM Applet":
                    status["vm_applet"] = value.lower() == "yes"
                    self.log(f"Setting vm_applet to: {value.lower() == 'yes'}")
        
        self.log(f"Final status: {status}")
        return status

    def validate_url(self):
        """Validate image URL format and protocol."""
        if not self.image_url:
            return
            
        # Check URL format
        url_pattern = r'^(http|https|nfs)://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, self.image_url):
            self.module.fail_json(
                msg=f"Invalid URL format: {self.image_url}. Supported protocols are http, https, and nfs."
            )

    def mount_virtual_media(self):
        """Mount virtual media with the specified image URL."""
        # Validate URL
        self.validate_url()
        
        # Check current status first
        current_status = self.get_virtual_media_status()
        
        # Check if already mounted with same settings
        if (current_status['image_url'] == self.image_url and
            current_status['connected'] == True and
            current_status['boot_on_next_reset'] == self.boot_on_next_reset):
            return False
            
        # If there's a different image mounted or different settings, unmount it first
        if current_status['image_url'] or current_status['connected']:
            self.log("Unmounting current media before mounting new one")
            self.unmount_virtual_media()
            
        # Insert the image
        command = f'vm {self.device_type} insert "{self.image_url}"'
        success, stdout, stderr = self.execute_command(command)
        self.log(f"Insert command output: {stdout}")
        if not success or 'status=0' not in stdout:
            error_msg = stderr or stdout
            if 'Unable to access url path' in error_msg or 'Unable to connect to URL' in error_msg:
                self.module.fail_json(msg=f"Image URL is not accessible: {self.image_url}")
            elif 'Error mounting media' in error_msg:
                self.module.fail_json(msg=f"Error mounting media - invalid image format or corrupted image")
            else:
                self.module.fail_json(msg=f"Failed to insert virtual media image: {error_msg}")

        # Connect the device
        command = f'vm {self.device_type} set connect'
        success, stdout, stderr = self.execute_command(command)
        self.log(f"Connect command output: {stdout}")
        if not success or 'status=0' not in stdout:
            error_msg = stderr or stdout
            if 'Unable to access url path' in error_msg or 'Unable to connect to URL' in error_msg:
                self.module.fail_json(msg=f"Image URL is not accessible: {self.image_url}")
            else:
                self.module.fail_json(msg=f"Failed to connect device: {error_msg}")

        # Set boot option if requested
        if self.boot_on_next_reset:
            command = f"vm {self.device_type} set boot_once"
            success, stdout, stderr = self.execute_command(command)
            self.log(f"Boot option command output: {stdout}")
            if not success or 'status=0' not in stdout:
                self.module.fail_json(msg=f"Failed to set boot option: {stderr or stdout}")

        # Wait for device to be fully mounted (up to 10 seconds)
        retries = 10
        while retries > 0:
            status = self.get_virtual_media_status()
            if (status['image_url'] == self.image_url and 
                status['connected'] == True and
                status['boot_on_next_reset'] == self.boot_on_next_reset):
                break
            time.sleep(1)
            retries -= 1
        
        if retries == 0:
            self.module.fail_json(msg=f"Image URL is not accessible: {self.image_url}")

        return True

    def unmount_virtual_media(self):
        """Unmount virtual media."""
        # Check current status first
        current_status = self.get_virtual_media_status()
        
        # Check if already unmounted
        if (not current_status['connected'] and 
            not current_status['image_url'] and 
            not current_status['boot_on_next_reset']):
            return False
            
        # First disable boot option
        command = f'vm {self.device_type} set no_boot'
        success, stdout, stderr = self.execute_command(command)
        if not success or 'status=0' not in stdout:
            self.module.fail_json(msg=f"Failed to disable boot option: {stderr or stdout}")
        self.log(f"Boot option command output: {stdout}")
        
        # Disconnect device
        command = f'vm {self.device_type} set disconnect'
        success, stdout, stderr = self.execute_command(command)
        if not success or 'status=0' not in stdout:
            self.module.fail_json(msg=f"Failed to disconnect device: {stderr or stdout}")
        self.log(f"Disconnect command output: {stdout}")
        
        # Eject media only if there's an image mounted
        if current_status['image_url']:
            command = f'vm {self.device_type} eject'
            success, stdout, stderr = self.execute_command(command)
            if not success or 'status=0' not in stdout:
                # Ignore "No image present" error as it means the image is already ejected
                if 'No image present' not in (stderr or stdout):
                    self.module.fail_json(msg=f"Failed to eject virtual media: {stderr or stdout}")
            self.log(f"Eject command output: {stdout}")
        
        # Wait for device to be fully unmounted (up to 10 seconds)
        retries = 10
        while retries > 0:
            status = self.get_virtual_media_status()
            if not status['connected'] and not status['image_url'] and not status['boot_on_next_reset']:
                break
            time.sleep(1)
            retries -= 1
        
        if retries == 0:
            self.module.fail_json(
                msg=f"Failed to unmount virtual media - device still has active settings after timeout. Status: {status}"
            )
        
        return True

    def run_module(self):
        """Run the module"""
        result = dict(
            changed=False,
            msg='',
            status=None
        )

        # Get current status
        current_status = self.get_virtual_media_status()
        self.log(f"Current status: {current_status}")

        if self.state == 'get':
            result['status'] = current_status
            result['msg'] = 'Successfully retrieved virtual media status'
            self.module.exit_json(**result)
            return

        if self.state == 'present':
            self.log("Mounting virtual media")
            changed = self.mount_virtual_media()
            result['changed'] = changed
            if changed:
                result['msg'] = 'Virtual media mounted successfully'
            else:
                result['msg'] = 'No changes required'
        else:  # state == 'absent'
            self.log("Unmounting virtual media")
            changed = self.unmount_virtual_media()
            result['changed'] = changed
            if changed:
                result['msg'] = 'Virtual media unmounted successfully'
            else:
                result['msg'] = 'No changes required'

        # Get final status
        result['status'] = self.get_virtual_media_status()
        self.log(f"Final status: {result['status']}")

        self.module.exit_json(**result)

def main():
    module = IloVirtualMediaModule()
    module.run_module()

if __name__ == '__main__':
    main() 
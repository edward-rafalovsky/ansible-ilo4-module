#!/usr/bin/python

from unittest.mock import MagicMock, patch
import pytest
from ansible.module_utils.basic import AnsibleModule
from plugins.modules.ilo_boot_settings import IloBootSettingsModule

def test_get_boot_settings():
    """Test retrieving boot settings"""
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            boot_mode=dict(type='str', required=False, choices=['UEFI', 'Legacy']),
            secure_boot=dict(type='bool', required=False),
            state=dict(type='str', default='present', choices=['present', 'get'])
        ),
        supports_check_mode=True
    )
    module.params = {
        'hostname': 'test-ilo',
        'username': 'test-user',
        'password': 'test-pass',
        'state': 'get'
    }
    module.fail_json = MagicMock()
    module.exit_json = MagicMock()
    
    ilo_module = IloBootSettingsModule()
    ilo_module.module = module
    ilo_module.execute_command = MagicMock()
    
    # Mock command output
    ilo_module.execute_command.return_value = (True, """
    status=0
    status_tag=COMMAND COMPLETED
    Tue Jan 14 21:54:45 2025

    /system1/bootconfig1
      Targets
        oemhp_uefibootsource1
        oemhp_uefibootsource2
        oemhp_uefibootsource3
        oemhp_uefibootsource4
        oemhp_uefibootsource5
    Properties
        oemhp_bootmode=UEFI
        oemhp_secureboot=no
        oemhp_pendingbootmode=UEFI
      Verbs
        cd version exit show set
    """, "")
    
    settings = ilo_module.get_boot_settings()
    assert settings['boot_mode'] == 'UEFI'
    assert settings['secure_boot'] == False
    assert settings['pending_boot_mode'] == 'UEFI'

def test_set_boot_mode():
    """Test setting boot mode"""
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            boot_mode=dict(type='str', required=False, choices=['UEFI', 'Legacy']),
            secure_boot=dict(type='bool', required=False),
            state=dict(type='str', default='present', choices=['present', 'get'])
        ),
        supports_check_mode=True
    )
    module.params = {
        'hostname': 'test-ilo',
        'username': 'test-user',
        'password': 'test-pass',
        'boot_mode': 'UEFI',
        'state': 'present'
    }
    module.fail_json = MagicMock()
    module.exit_json = MagicMock()
    
    ilo_module = IloBootSettingsModule()
    ilo_module.module = module
    
    # Mock command execution for setting boot mode
    ilo_module.execute_command = MagicMock()
    ilo_module.execute_command.side_effect = [
        # First call - set boot mode
        (True, "", ""),
        # Second call - get settings to verify
        (True, """
        status=0
        status_tag=COMMAND COMPLETED
        Tue Jan 14 21:54:45 2025

        /system1/bootconfig1
          Properties
            oemhp_bootmode=UEFI
            oemhp_secureboot=no
            oemhp_pendingbootmode=UEFI
          Verbs
            cd version exit show set
        """, "")
    ]
    
    ilo_module.set_boot_mode("UEFI")
    
    # Verify set command was called
    assert ilo_module.execute_command.call_args_list[0][0][0] == "set /system1/bootconfig1 oemhp_bootmode=UEFI"
    
    # Verify get settings was called to check the result
    assert ilo_module.execute_command.call_args_list[1][0][0] == "show /system1/bootconfig1"

def test_set_secure_boot():
    """Test setting secure boot"""
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            boot_mode=dict(type='str', required=False, choices=['UEFI', 'Legacy']),
            secure_boot=dict(type='bool', required=False),
            state=dict(type='str', default='present', choices=['present', 'get'])
        ),
        supports_check_mode=True
    )
    module.params = {
        'hostname': 'test-ilo',
        'username': 'test-user',
        'password': 'test-pass',
        'secure_boot': True,
        'state': 'present'
    }
    module.fail_json = MagicMock()
    module.exit_json = MagicMock()
    
    ilo_module = IloBootSettingsModule()
    ilo_module.module = module
    
    # Mock command execution for setting secure boot
    ilo_module.execute_command = MagicMock()
    ilo_module.execute_command.side_effect = [
        # First call - set secure boot
        (True, "", ""),
        # Second call - get settings to verify
        (True, """
        status=0
        status_tag=COMMAND COMPLETED
        Tue Jan 14 21:54:45 2025

        /system1/bootconfig1
          Properties
            oemhp_bootmode=UEFI
            oemhp_secureboot=yes
            oemhp_pendingbootmode=UEFI
          Verbs
            cd version exit show set
        """, "")
    ]
    
    ilo_module.set_secure_boot(True)
    
    # Verify set command was called
    assert ilo_module.execute_command.call_args_list[0][0][0] == "set /system1/bootconfig1 oemhp_secureboot=yes"
    
    # Verify get settings was called to check the result
    assert ilo_module.execute_command.call_args_list[1][0][0] == "show /system1/bootconfig1" 
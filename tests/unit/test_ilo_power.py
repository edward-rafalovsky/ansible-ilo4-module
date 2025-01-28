#!/usr/bin/python

from unittest.mock import patch, MagicMock
import pytest
from ansible.module_utils.basic import AnsibleModule
from plugins.modules.ilo_power import IloPowerModule

def test_get_power_state_on(mocker):
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'admin',
        'password': 'password',
        'state': 'get',
        'force': False
    }
    
    ilo_power = IloPowerModule(module)
    
    # Mock execute_command to return powered on state
    mocker.patch.object(
        ilo_power, 
        'execute_command',
        return_value=(True, "EnabledState=enabled", "")
    )
    
    assert ilo_power.get_power_state() == 'on'

def test_get_power_state_off(mocker):
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'admin',
        'password': 'password',
        'state': 'get',
        'force': False
    }
    
    ilo_power = IloPowerModule(module)
    
    # Mock execute_command to return powered off state
    mocker.patch.object(
        ilo_power, 
        'execute_command',
        return_value=(True, "EnabledState=disabled", "")
    )
    
    assert ilo_power.get_power_state() == 'off'

def test_power_on_server(mocker):
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'admin',
        'password': 'password',
        'state': 'on',
        'force': False
    }
    
    ilo_power = IloPowerModule(module)
    
    # Mock execute_command for initial state check (off) and power on command
    execute_command_mock = mocker.patch.object(
        ilo_power,
        'execute_command',
        side_effect=[
            (True, "EnabledState=disabled", ""),  # Initial state: off
            (True, "Command completed successfully", ""),  # Power on command
            (True, "EnabledState=enabled", "")  # Final state check: on
        ]
    )
    
    changed, state = ilo_power.set_power_state()
    assert changed is True
    assert state == 'on'
    assert execute_command_mock.call_count == 3

def test_power_off_server_graceful(mocker):
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'admin',
        'password': 'password',
        'state': 'off',
        'force': False
    }
    
    ilo_power = IloPowerModule(module)
    
    # Mock execute_command for initial state check (on) and power off command
    execute_command_mock = mocker.patch.object(
        ilo_power,
        'execute_command',
        side_effect=[
            (True, "EnabledState=enabled", ""),  # Initial state: on
            (True, "Command completed successfully", ""),  # Power off command
            (True, "EnabledState=disabled", "")  # Final state check: off
        ]
    )
    
    changed, state = ilo_power.set_power_state()
    assert changed is True
    assert state == 'off'
    assert execute_command_mock.call_count == 3

def test_power_off_server_force(mocker):
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'admin',
        'password': 'password',
        'state': 'off',
        'force': True
    }
    
    ilo_power = IloPowerModule(module)
    
    # Mock execute_command for initial state check (on) and force power off command
    execute_command_mock = mocker.patch.object(
        ilo_power,
        'execute_command',
        side_effect=[
            (True, "EnabledState=enabled", ""),  # Initial state: on
            (True, "Command completed successfully", ""),  # Force power off command
            (True, "EnabledState=disabled", "")  # Final state check: off
        ]
    )
    
    changed, state = ilo_power.set_power_state()
    assert changed is True
    assert state == 'off'
    assert execute_command_mock.call_count == 3
    # Verify force power off command was used
    assert 'stop /system1/powerunit1' in execute_command_mock.call_args_list[1][0][0]

def test_reset_server(mocker):
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'admin',
        'password': 'password',
        'state': 'reset',
        'force': False
    }
    
    ilo_power = IloPowerModule(module)
    
    # Mock execute_command for initial state check and reset command
    execute_command_mock = mocker.patch.object(
        ilo_power,
        'execute_command',
        side_effect=[
            (True, "EnabledState=enabled", ""),  # Initial state check
            (True, "Command completed successfully", "")  # Reset command
        ]
    )
    
    changed, state = ilo_power.set_power_state()
    assert changed is True
    assert state == 'reset_initiated'
    assert execute_command_mock.call_count == 2

def test_cold_boot_server(mocker):
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'admin',
        'password': 'password',
        'state': 'cold_boot',
        'force': False
    }
    
    ilo_power = IloPowerModule(module)
    
    # Mock execute_command for initial state check and cold boot command
    execute_command_mock = mocker.patch.object(
        ilo_power,
        'execute_command',
        side_effect=[
            (True, "EnabledState=enabled", ""),  # Initial state check
            (True, "Command completed successfully", "")  # Cold boot command
        ]
    )
    
    changed, state = ilo_power.set_power_state()
    assert changed is True
    assert state == 'reset_initiated'
    assert execute_command_mock.call_count == 2 
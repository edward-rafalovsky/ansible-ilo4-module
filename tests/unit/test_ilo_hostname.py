#!/usr/bin/python

from unittest.mock import patch, MagicMock
import pytest
from ansible.module_utils.basic import AnsibleModule
from plugins.modules.ilo_hostname import IloHostnameModule

def test_get_hostname(mocker):
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'admin',
        'password': 'password',
        'state': 'get'
    }
    
    ilo_hostname = IloHostnameModule(module)
    
    # Mock execute_command to return hostname
    mocker.patch.object(
        ilo_hostname, 
        'execute_command',
        return_value=(True, "hostname=test-server", "")
    )
    
    result = ilo_hostname.run_module()
    assert result == {
        'changed': False,
        'hostname': 'test-server'
    }

def test_set_hostname(mocker):
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'admin',
        'password': 'password',
        'state': 'present',
        'ilo_hostname': 'new-server'
    }
    
    ilo_hostname = IloHostnameModule(module)
    
    # Mock execute_command for get and set
    execute_command_mock = mocker.patch.object(
        ilo_hostname,
        'execute_command',
        side_effect=[
            (True, "hostname=old-server", ""),  # Get current hostname
            (True, "Command completed successfully", "")  # Set new hostname
        ]
    )
    
    result = ilo_hostname.run_module()
    assert result == {
        'changed': True,
        'hostname': 'new-server'
    }
    assert execute_command_mock.call_count == 2

def test_set_hostname_no_change(mocker):
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'admin',
        'password': 'password',
        'state': 'present',
        'ilo_hostname': 'current-server'
    }
    
    ilo_hostname = IloHostnameModule(module)
    
    # Mock execute_command to return same hostname
    mocker.patch.object(
        ilo_hostname,
        'execute_command',
        return_value=(True, "hostname=current-server", "")
    )
    
    result = ilo_hostname.run_module()
    assert result == {
        'changed': False,
        'hostname': 'current-server'
    }

def test_get_hostname_fail(mocker):
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'admin',
        'password': 'password',
        'state': 'get'
    }
    module.fail_json = MagicMock(side_effect=Exception("Failed to get hostname"))
    
    ilo_hostname = IloHostnameModule(module)
    
    # Mock execute_command to fail
    mocker.patch.object(
        ilo_hostname,
        'execute_command',
        return_value=(False, "", "Command failed")
    )
    
    with pytest.raises(Exception) as exc_info:
        ilo_hostname.run_module()
    assert "Failed to get hostname" in str(exc_info.value)

def test_set_hostname_fail(mocker):
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'admin',
        'password': 'password',
        'state': 'present',
        'ilo_hostname': 'new-server'
    }
    module.fail_json = MagicMock(side_effect=Exception("Failed to set hostname"))
    
    ilo_hostname = IloHostnameModule(module)
    
    # Mock execute_command to fail on set
    mocker.patch.object(
        ilo_hostname,
        'execute_command',
        side_effect=[
            (True, "hostname=old-server", ""),  # Get current hostname
            (False, "", "Command failed")  # Set new hostname fails
        ]
    )
    
    with pytest.raises(Exception) as exc_info:
        ilo_hostname.run_module()
    assert "Failed to set hostname" in str(exc_info.value) 
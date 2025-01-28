#!/usr/bin/python

import pytest
from unittest.mock import MagicMock
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hpe.ilo_ssh.plugins.modules.ilo_power_settings import IloPowerSettingsModule

def test_get_power_settings_success():
    """Test successful retrieval of power settings"""
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'test',
        'password': 'test',
        'power_reg_mode': None,
        'auto_power': None
    }
    
    ilo = IloPowerSettingsModule(module)
    ilo.execute_command = MagicMock(return_value=(
        True,
        '''
        /system1/oemHPE_power1
        Properties
        oemHPE_powerreg=dynamic
        oemHPE_auto_pwr=off
        ''',
        ''
    ))
    
    settings = ilo.get_power_settings()
    assert settings == {
        'power_reg_mode': 'dynamic',
        'auto_power': 'off'
    }

def test_set_power_regulator_success():
    """Test successful power regulator mode change"""
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'test',
        'password': 'test',
        'power_reg_mode': 'os',
        'auto_power': None
    }
    
    ilo = IloPowerSettingsModule(module)
    ilo.execute_command = MagicMock(return_value=(True, '', ''))
    
    assert ilo.set_power_regulator() == True
    ilo.execute_command.assert_called_once_with('set /system1/oemHPE_power1 oemHPE_powerreg=os')

def test_set_auto_power_success():
    """Test successful auto power setting change"""
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'test',
        'password': 'test',
        'power_reg_mode': None,
        'auto_power': '30'
    }
    
    ilo = IloPowerSettingsModule(module)
    ilo.execute_command = MagicMock(return_value=(True, '', ''))
    
    assert ilo.set_auto_power() == True
    ilo.execute_command.assert_called_once_with('set /system1/oemHPE_power1 oemHPE_auto_pwr=30')

def test_get_power_settings_failure():
    """Test failure in getting power settings"""
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'test',
        'password': 'test',
        'power_reg_mode': None,
        'auto_power': None
    }
    module.fail_json = MagicMock(side_effect=Exception('Test failure'))
    
    ilo = IloPowerSettingsModule(module)
    ilo.execute_command = MagicMock(return_value=(False, '', 'Command failed'))
    
    with pytest.raises(Exception):
        ilo.get_power_settings()

def test_run_module_no_changes():
    """Test module run with no changes needed"""
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'test',
        'password': 'test',
        'power_reg_mode': 'dynamic',
        'auto_power': 'off'
    }
    
    ilo = IloPowerSettingsModule(module)
    ilo.get_power_settings = MagicMock(return_value={
        'power_reg_mode': 'dynamic',
        'auto_power': 'off'
    })
    
    result = ilo.run_module()
    assert result['changed'] == False
    assert result['settings'] == {
        'power_reg_mode': 'dynamic',
        'auto_power': 'off'
    }

def test_run_module_with_changes():
    """Test module run with changes needed"""
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'test',
        'password': 'test',
        'power_reg_mode': 'os',
        'auto_power': '30'
    }
    
    ilo = IloPowerSettingsModule(module)
    ilo.get_power_settings = MagicMock(return_value={
        'power_reg_mode': 'dynamic',
        'auto_power': 'off'
    })
    ilo.set_power_regulator = MagicMock(return_value=True)
    ilo.set_auto_power = MagicMock(return_value=True)
    
    result = ilo.run_module()
    assert result['changed'] == True
    assert result['settings'] == {
        'power_reg_mode': 'os',
        'auto_power': '30'
    } 
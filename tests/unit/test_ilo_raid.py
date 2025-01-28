#!/usr/bin/python

from unittest.mock import patch, MagicMock
import pytest
import xml.etree.ElementTree as ET
from ansible.module_utils.basic import AnsibleModule
from plugins.modules.ilo_raid import IloRAIDModule

def get_mock_xml_response():
    return """<?xml version="1.0"?>
<RIBCL VERSION="2.23">
<RESPONSE STATUS="0x0000" MESSAGE="No error"/>
<GET_EMBEDDED_HEALTH_DATA>
    <STORAGE>
        <CONTROLLER>
            <LABEL VALUE="Controller on System Board"/>
            <MODEL VALUE="Smart Array P440ar"/>
            <STATUS VALUE="OK"/>
            <SERIAL_NUMBER VALUE="PDNLH0BRH7C1EX"/>
            <FW_VERSION VALUE="1.62"/>
            <DRIVE_ENCLOSURE>
                <LABEL VALUE="Port 1I Box 1"/>
                <STATUS VALUE="OK"/>
                <DRIVE_BAY VALUE="1"/>
            </DRIVE_ENCLOSURE>
            <LOGICAL_DRIVE>
                <LABEL VALUE="LogicalDrive 1"/>
                <STATUS VALUE="OK"/>
                <CAPACITY VALUE="279.4 GB"/>
                <FAULT_TOLERANCE VALUE="RAID 1"/>
                <LOGICAL_DRIVE_TYPE VALUE="Data LUN"/>
                <PHYSICAL_DRIVE>
                    <LABEL VALUE="Physical Drive 1I:1:1"/>
                    <STATUS VALUE="OK"/>
                    <SERIAL_NUMBER VALUE="S2M3NX0J"/>
                    <MODEL VALUE="EG0300JWJPH"/>
                    <CAPACITY VALUE="300 GB"/>
                    <LOCATION VALUE="Port 1I Box 1 Bay 1"/>
                    <FW_VERSION VALUE="HPD6"/>
                </PHYSICAL_DRIVE>
                <PHYSICAL_DRIVE>
                    <LABEL VALUE="Physical Drive 1I:1:2"/>
                    <STATUS VALUE="OK"/>
                    <SERIAL_NUMBER VALUE="S2M3NX1K"/>
                    <MODEL VALUE="EG0300JWJPH"/>
                    <CAPACITY VALUE="300 GB"/>
                    <LOCATION VALUE="Port 1I Box 1 Bay 2"/>
                    <FW_VERSION VALUE="HPD6"/>
                </PHYSICAL_DRIVE>
            </LOGICAL_DRIVE>
        </CONTROLLER>
    </STORAGE>
</GET_EMBEDDED_HEALTH_DATA>
</RIBCL>"""

def get_mock_backplane_info():
    return """<?xml version="1.0"?>
<RIBCL VERSION="2.23">
<RESPONSE STATUS="0x0000" MESSAGE="No error"/>
<READ_BACKPLANE_INFO>
    <TYPE_ID VALUE="1"/>
    <SEP_NODE_ID VALUE="0x500143801234567"/>
    <WWID VALUE="5001438012345678"/>
    <SEP_ID VALUE="1"/>
    <BACKPLANE_NAME VALUE="SAS Expander Card"/>
    <FW_REV VALUE="2.10"/>
    <BAY_CNT VALUE="8"/>
    <START_BAY VALUE="1"/>
    <HOST_PORT_CNT VALUE="2"/>
    <HOST_PORT VALUE="1">
        <NODE_NUM VALUE="1"/>
        <SLOT_NUM VALUE="0"/>
    </HOST_PORT>
    <HOST_PORT VALUE="2">
        <NODE_NUM VALUE="2"/>
        <SLOT_NUM VALUE="0"/>
    </HOST_PORT>
</READ_BACKPLANE_INFO>
</RIBCL>"""

def get_mock_zone_table():
    return """<?xml version="1.0"?>
<RIBCL VERSION="2.23">
<RESPONSE STATUS="0x0000" MESSAGE="No error"/>
<READ_ZONE_TABLE>
    <TYPE_ID VALUE="1"/>
    <SEP_NODE_ID VALUE="0x500143801234567"/>
    <HOST_PORT VALUE="1">
        <BAY VALUE="1"/>
        <BAY VALUE="2"/>
    </HOST_PORT>
    <HOST_PORT VALUE="2">
        <BAY VALUE="3"/>
        <BAY VALUE="4"/>
    </HOST_PORT>
</READ_ZONE_TABLE>
</RIBCL>"""

def test_parse_storage_info():
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'admin',
        'password': 'password',
        'state': 'get',
        'controller': 'Smart Array P440ar'
    }
    
    raid_module = IloRAIDModule(module)
    
    # Mock send_xml to return our test XML
    raid_module.send_xml = MagicMock(side_effect=[
        get_mock_xml_response(),
        get_mock_backplane_info(),
        get_mock_zone_table()
    ])
    
    raid_info = raid_module.get_raid_info()
    
    # Проверяем информацию о контроллере
    assert raid_info["status"] == "OK"
    assert len(raid_info["controllers"]) == 1
    controller = raid_info["controllers"][0]
    assert controller["id"] == "Controller on System Board"
    assert controller["model"] == "Smart Array P440ar"
    assert controller["status"] == "OK"
    assert controller["serial_number"] == "PDNLH0BRH7C1EX"
    assert controller["firmware_version"] == "1.62"
    
    # Проверяем логические диски
    assert len(controller["volumes"]) == 1
    volume = controller["volumes"][0]
    assert volume["id"] == "LogicalDrive 1"
    assert volume["status"] == "OK"
    assert volume["capacity"] == "279.4 GB"
    assert volume["fault_tolerance"] == "RAID 1"
    
    # Проверяем физические диски
    assert len(volume["physical_drives"]) == 2
    drive = volume["physical_drives"][0]
    assert drive["label"] == "Physical Drive 1I:1:1"
    assert drive["status"] == "OK"
    assert drive["serial_number"] == "S2M3NX0J"
    assert drive["model"] == "EG0300JWJPH"
    assert drive["capacity"] == "300 GB"
    assert drive["location"] == "Port 1I Box 1 Bay 1"
    
    # Проверяем информацию о backplane
    assert "backplane" in raid_info
    backplane = raid_info["backplane"]
    assert backplane["type_id"] == "1"
    assert backplane["sep_node_id"] == "0x500143801234567"
    assert backplane["wwid"] == "5001438012345678"
    assert backplane["backplane_name"] == "SAS Expander Card"
    assert backplane["bay_cnt"] == "8"
    assert len(backplane["host_ports"]) == 2
    
    # Проверяем zone table
    assert "zone_table" in raid_info
    zone_table = raid_info["zone_table"]
    assert zone_table["type_id"] == "1"
    assert zone_table["sep_node_id"] == "0x500143801234567"
    assert len(zone_table["host_ports"]) == 2
    assert len(zone_table["host_ports"][0]["bays"]) == 2

def test_no_storage_info():
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'admin',
        'password': 'password',
        'state': 'get',
        'controller': 'Smart Array P440ar'
    }
    
    raid_module = IloRAIDModule(module)
    
    # Mock send_xml to return XML without storage section
    xml_without_storage = """<?xml version="1.0"?>
    <RIBCL VERSION="2.23">
    <RESPONSE STATUS="0x0000" MESSAGE="No error"/>
    <GET_EMBEDDED_HEALTH_DATA>
    </GET_EMBEDDED_HEALTH_DATA>
    </RIBCL>"""
    
    raid_module.send_xml = MagicMock(return_value=xml_without_storage)
    
    raid_info = raid_module.get_raid_info()
    assert raid_info["status"] == "NO_STORAGE_INFO"

def test_parse_error():
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'admin',
        'password': 'password',
        'state': 'get',
        'controller': 'Smart Array P440ar'
    }
    
    raid_module = IloRAIDModule(module)
    
    # Mock send_xml to return invalid XML
    raid_module.send_xml = MagicMock(return_value="Invalid XML")
    
    raid_info = raid_module.get_raid_info()
    assert raid_info["status"] == "PARSE_ERROR"

def test_no_response():
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'admin',
        'password': 'password',
        'state': 'get',
        'controller': 'Smart Array P440ar'
    }
    
    raid_module = IloRAIDModule(module)
    
    # Mock send_xml to return None
    raid_module.send_xml = MagicMock(return_value=None)
    
    raid_info = raid_module.get_raid_info()
    assert raid_info["status"] == "NO_RESPONSE" 

def test_get_supported_commands():
    module = MagicMock(spec=AnsibleModule)
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'admin',
        'password': 'password',
        'state': 'get_commands',
        'controller': 'Smart Array P440ar'
    }
    
    raid_module = IloRAIDModule(module)
    
    # Mock send_xml to return our test XML
    raid_module.send_xml = MagicMock(return_value=get_mock_xml_response())
    
    raid_info = raid_module.get_supported_commands()
    
    # Проверяем статус и наличие контроллеров
    assert raid_info["status"] == "OK"
    assert len(raid_info["controllers"]) == 1
    
    # Проверяем информацию о контроллере
    controller = raid_info["controllers"][0]
    assert controller["id"] == "Controller on System Board"
    assert controller["model"] == "Smart Array P440ar"
    assert "supported_commands" in controller
    assert set(controller["supported_commands"]) == set(["get", "get_commands", "present", "absent"]) 

def test_create_volume():
    module = MagicMock()
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'Administrator',
        'password': 'password',
        'state': 'present',
        'controller': 'SmartRAID 1',
        'raid_level': '1',
        'drives': ['1I:1:1', '1I:1:2'],
        'volume_name': 'Data_Volume',
        'size_gb': 100,
        'spare_drives': []
    }
    
    raid_module = IloRAIDModule(module)
    raid_module.send_xml = MagicMock(return_value=get_mock_xml_response())
    
    result = raid_module.run()
    
    assert result['changed'] is True
    assert result['msg'] == 'Volume Data_Volume created successfully'
    assert result['raid_info']['status'] == 'OK'
    assert len(result['raid_info']['controllers']) > 0
    
def test_delete_volume():
    module = MagicMock()
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'Administrator',
        'password': 'password',
        'state': 'absent',
        'controller': 'SmartRAID 1',
        'volume_name': 'Data_Volume'
    }
    
    raid_module = IloRAIDModule(module)
    raid_module.send_xml = MagicMock(return_value=get_mock_xml_response())
    
    result = raid_module.run()
    
    assert result['changed'] is True
    assert result['msg'] == 'Volume Data_Volume deleted successfully'
    assert result['raid_info']['status'] == 'OK'
    
def test_get_physical_drives():
    module = MagicMock()
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'Administrator',
        'password': 'password',
        'state': 'get_drives',
        'controller': 'Smart Array P440ar'
    }
    
    raid_module = IloRAIDModule(module)
    raid_module.send_xml = MagicMock(side_effect=[
        get_mock_xml_response(),  # GET_EMBEDDED_HEALTH
        get_mock_backplane_info(),  # READ_BACKPLANE_INFO
        get_mock_zone_table()  # READ_ZONE_TABLE
    ])
    
    result = raid_module.get_physical_drives()
    
    # Проверяем основную информацию
    assert result['changed'] is False
    assert result['raid_info']['status'] == 'OK'
    assert 'physical_drives' in result['raid_info']
    
    # Проверяем информацию о физических дисках
    drives = result['raid_info']['physical_drives']
    assert len(drives) > 0
    drive = drives[0]
    assert 'label' in drive
    assert 'status' in drive
    assert 'drive_bay' in drive or ('serial_number' in drive and 'model' in drive)
    
    # Проверяем информацию о бэкплейне
    assert 'backplane' in result['raid_info']
    backplane = result['raid_info']['backplane']
    assert backplane['type_id'] == '1'
    assert backplane['sep_node_id'] == '0x500143801234567'
    assert backplane['wwid'] == '5001438012345678'
    assert backplane['backplane_name'] == 'SAS Expander Card'
    assert backplane['bay_cnt'] == '8'
    assert backplane['host_port_cnt'] == '2'
    assert len(backplane['host_ports']) == 2
    
    # Проверяем информацию о зонах
    assert 'zone_table' in result['raid_info']
    zone_table = result['raid_info']['zone_table']
    assert zone_table['type_id'] == '1'
    assert zone_table['sep_node_id'] == '0x500143801234567'
    assert len(zone_table['host_ports']) == 2
    host_port = zone_table['host_ports'][0]
    assert 'value' in host_port
    assert 'bays' in host_port
    assert len(host_port['bays']) == 2
    
def test_create_volume_with_spares():
    module = MagicMock()
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'Administrator',
        'password': 'password',
        'state': 'present',
        'controller': 'SmartRAID 1',
        'raid_level': '5',
        'drives': ['1I:1:1', '1I:1:2', '1I:1:3'],
        'volume_name': 'Data_Volume_R5',
        'size_gb': 200,
        'spare_drives': ['1I:1:4']
    }
    
    raid_module = IloRAIDModule(module)
    raid_module.send_xml = MagicMock(return_value=get_mock_xml_response())
    
    result = raid_module.run()
    
    assert result['changed'] is True
    assert result['msg'] == 'Volume Data_Volume_R5 created successfully'
    assert result['raid_info']['status'] == 'OK'
    assert len(result['raid_info']['controllers']) > 0
    
def test_create_volume_invalid_params():
    module = MagicMock()
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'Administrator',
        'password': 'password',
        'state': 'present',
        'controller': 'SmartRAID 1',
        'raid_level': '1',
        'drives': ['1I:1:1'],  # Not enough drives for RAID 1
        'volume_name': 'Data_Volume',
        'size_gb': 100
    }
    
    raid_module = IloRAIDModule(module)
    raid_module.send_xml = MagicMock(return_value=get_mock_xml_response())
    
    result = raid_module.run()
    
    assert result['changed'] is False
    assert 'Not enough drives' in result['msg']
    assert result['raid_info']['status'] == 'ERROR'
    
def test_delete_nonexistent_volume():
    module = MagicMock()
    module.params = {
        'hostname': 'ilo.example.com',
        'username': 'Administrator',
        'password': 'password',
        'state': 'absent',
        'controller': 'SmartRAID 1',
        'volume_name': 'NonExistentVolume'
    }
    
    raid_module = IloRAIDModule(module)
    raid_module.send_xml = MagicMock(return_value=get_mock_xml_response())
    
    result = raid_module.run()
    
    assert result['changed'] is False
    assert 'Volume not found' in result['msg']
    assert result['raid_info']['status'] == 'ERROR' 
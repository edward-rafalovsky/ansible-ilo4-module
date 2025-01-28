#!/usr/bin/python

DOCUMENTATION = '''
module: ilo_raid
short_description: Manage HPE Smart Array RAID configuration via iLO RIBCL
description:
    - Manage RAID configuration using HPE iLO RIBCL XML interface
    - Create and delete RAID volumes
    - Get RAID configuration status and information
    - Get physical drives information
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
    state:
        description: Desired state of the RAID configuration
        choices: ['get', 'get_commands', 'get_drives', 'present', 'absent']
        default: get
        type: str
    controller:
        description: Controller slot number or ID
        type: str
        required: true
    raid_level:
        description: RAID level for volume creation (required for state=present)
        type: str
        required: false
    drives:
        description: List of physical drives to use for volume creation (required for state=present)
        type: list
        elements: str
        required: false
    volume_name:
        description: Name of the volume (required for state=present and state=absent)
        type: str
        required: false
    size_gb:
        description: Size of the volume in GB (optional for state=present)
        type: int
        required: false
    spare_drives:
        description: List of physical drives to use as spares (optional for state=present)
        type: list
        elements: str
        required: false
'''

EXAMPLES = '''
# Get current RAID configuration
- name: Get RAID configuration
  hpe.ilo_ssh.ilo_raid:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    controller: "SmartRAID 1"
    state: get

# Get physical drives information
- name: Get physical drives
  hpe.ilo_ssh.ilo_raid:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    controller: "SmartRAID 1"
    state: get_drives

# Create RAID 1 volume
- name: Create RAID 1 volume
  hpe.ilo_ssh.ilo_raid:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    controller: "SmartRAID 1"
    state: present
    raid_level: "1"
    drives:
      - "1I:1:1"
      - "1I:1:2"
    volume_name: "Data_Volume"
    size_gb: 100

# Create RAID 5 volume with spare drive
- name: Create RAID 5 volume with spare
  hpe.ilo_ssh.ilo_raid:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    controller: "SmartRAID 1"
    state: present
    raid_level: "5"
    drives:
      - "1I:1:1"
      - "1I:1:2"
      - "1I:1:3"
    spare_drives:
      - "1I:1:4"
    volume_name: "Data_Volume_R5"
    size_gb: 200

# Delete RAID volume
- name: Delete RAID volume
  hpe.ilo_ssh.ilo_raid:
    hostname: "{{ ilo_host }}"
    username: "{{ ilo_username }}"
    password: "{{ ilo_password }}"
    controller: "SmartRAID 1"
    state: absent
    volume_name: "Data_Volume"
'''

RETURN = '''
changed:
    description: Whether the RAID configuration was modified
    type: bool
    returned: always
msg:
    description: Status message
    type: str
    returned: always
raid_info:
    description: Current RAID configuration information
    type: dict
    returned: always
    contains:
        status:
            description: Status of the operation
            type: str
            returned: always
        controllers:
            description: List of storage controllers
            type: list
            elements: dict
            returned: when state=get or state=present or state=absent
            contains:
                id:
                    description: Controller ID
                    type: str
                model:
                    description: Controller model
                    type: str
                status:
                    description: Controller status
                    type: str
                serial_number:
                    description: Controller serial number
                    type: str
                firmware_version:
                    description: Controller firmware version
                    type: str
                volumes:
                    description: List of logical volumes
                    type: list
                    elements: dict
                    contains:
                        id:
                            description: Volume ID
                            type: str
                        status:
                            description: Volume status
                            type: str
                        capacity:
                            description: Volume capacity
                            type: str
                        fault_tolerance:
                            description: RAID level
                            type: str
                        logical_drive_type:
                            description: Type of logical drive
                            type: str
                        physical_drives:
                            description: List of physical drives in the volume
                            type: list
                            elements: dict
                            contains:
                                label:
                                    description: Drive label
                                    type: str
                                status:
                                    description: Drive status
                                    type: str
                                serial_number:
                                    description: Drive serial number
                                    type: str
                                model:
                                    description: Drive model
                                    type: str
                                capacity:
                                    description: Drive capacity
                                    type: str
                                location:
                                    description: Drive location
                                    type: str
                                firmware_version:
                                    description: Drive firmware version
                                    type: str
                physical_drives:
                    description: List of physical drives
            type: list
            elements: dict
            returned: when state=get_drives
            contains:
                label:
                    description: Drive label
                    type: str
                status:
                    description: Drive status
                    type: str
                serial_number:
                    description: Drive serial number
                    type: str
                model:
                    description: Drive model
                    type: str
                capacity:
                    description: Drive capacity
                    type: str
                location:
                    description: Drive location
                    type: str
                firmware_version:
                    description: Drive firmware version
                    type: str
                drive_bay:
                    description: Drive bay number
                    type: str
                    returned: when available
        backplane:
            description: Backplane information
            type: dict
            returned: when state=get_drives
            contains:
                type_id:
                    description: Type of Storage Enclosure Processor (SEP) configuration
                    type: str
                sep_node_id:
                    description: Node ID where SEP resides
                    type: str
                wwid:
                    description: World Wide Identifier
                    type: str
                sep_id:
                    description: SEP identifier
                    type: str
                backplane_name:
                    description: Name of the backplane
                    type: str
                fw_rev:
                    description: Firmware revision
                    type: str
                bay_cnt:
                    description: Number of drive bays
                    type: str
                start_bay:
                    description: Starting bay number
                    type: str
                host_port_cnt:
                    description: Number of host ports
                    type: str
                host_ports:
                    description: List of host ports
                    type: list
                    elements: dict
                    contains:
                        value:
                            description: Port number
                            type: str
                        node_num:
                            description: Node number
                            type: str
                        slot_num:
                            description: Slot number
                            type: str
        zone_table:
            description: Drive bay mapping information
            type: dict
            returned: when state=get_drives
            contains:
                type_id:
                    description: Type of SEP configuration
                    type: str
                sep_node_id:
                    description: Node ID where SEP resides
                    type: str
                host_ports:
                    description: List of host ports and their bay assignments
                    type: list
                    elements: dict
                    contains:
                        value:
                            description: Port number
                            type: str
                        bays:
                            description: List of drive bays assigned to this port
                            type: list
                            elements: str
'''

from ansible.module_utils.basic import AnsibleModule
import requests
import xml.etree.ElementTree as ET
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IloRAIDModule:
    def __init__(self, module):
        self.module = module
        self.hostname = module.params['hostname']
        self.username = module.params['username']
        self.password = module.params['password']
        self.state = module.params['state']
        self.controller = module.params['controller']
        self.raid_level = module.params.get('raid_level')
        self.drives = module.params.get('drives', [])
        self.volume_name = module.params.get('volume_name')
        self.size_gb = module.params.get('size_gb')
        self.spare_drives = module.params.get('spare_drives', [])

    def send_xml(self, xml_data):
        """Send XML request to iLO."""
        try:
            self.module.debug(f"\nSending XML request to {self.hostname}")
            self.module.debug(f"Request XML:\n{xml_data}")
            
            response = requests.post(
                f"https://{self.hostname}/ribcl",
                data=xml_data,
                verify=False,
                auth=(self.username, self.password),
                headers={'Content-Type': 'application/xml'}
            )
            
            self.module.debug(f"Response status code: {response.status_code}")
            self.module.debug(f"Response headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                raise Exception(f"Server returned status code {response.status_code}")
            
            response_text = response.content.decode('utf-8', errors='ignore')
            self.module.debug(f"Response XML:\n{response_text}")
            
            try:
                # Try to parse XML to see if it's valid
                ET.fromstring(response_text)
                self.module.debug("XML parsed successfully")
            except ET.ParseError as e:
                self.module.debug(f"XML parse error: {str(e)}")
                self.module.debug(f"Response content (hex): {' '.join(hex(x)[2:].zfill(2) for x in response.content)}")
            
            return response_text
            
        except Exception as e:
            self.module.fail_json(msg=f"Failed to send XML request: {str(e)}")
            return None

    def get_supported_commands(self):
        """Get supported RAID commands."""
        xml_request = f"""<?xml version="1.0"?>
<RIBCL VERSION="2.23">
<LOGIN USER_LOGIN="{self.username}" PASSWORD="{self.password}">
<SERVER_INFO MODE="read">
<GET_EMBEDDED_HEALTH/>
</SERVER_INFO>
</LOGIN>
</RIBCL>"""

        response = self.send_xml(xml_request)
        if not response:
            return {"status": "NO_RESPONSE"}
            
        try:
            # Разделяем ответ на отдельные XML документы
            xml_docs = response.split('<?xml version="1.0"?>')
            for doc in xml_docs:
                if not doc.strip():
                    continue
                    
                try:
                    root = ET.fromstring('<?xml version="1.0"?>' + doc)
                    
                    # Проверяем статус ответа
                    response_node = root.find('.//RESPONSE')
                    if response_node is not None:
                        status = response_node.get('STATUS', 'N/A')
                        message = response_node.get('MESSAGE', 'N/A')
                        self.module.debug(f"\nResponse status: {status}")
                        self.module.debug(f"Response message: {message}")
                        if status != '0x0000':  # Если статус не OK
                            continue
                    
                    # Проверяем GET_EMBEDDED_HEALTH_DATA
                    health_data = root.find('.//GET_EMBEDDED_HEALTH_DATA')
                    if health_data is None:
                        continue
                        
                    storage = health_data.find('.//STORAGE')
                    if storage is None:
                        continue
                        
                    raid_info = {
                        "status": "OK",
                        "controllers": []
                    }
                    
                    for controller in storage.findall('.//CONTROLLER'):
                        controller_info = {
                            "id": controller.find('.//LABEL').get('VALUE', '') if controller.find('.//LABEL') is not None else '',
                            "model": controller.find('.//MODEL').get('VALUE', '') if controller.find('.//MODEL') is not None else '',
                            "supported_commands": ["get", "get_commands"]
                        }
                        raid_info["controllers"].append(controller_info)
                        
                    return raid_info
                    
                except ET.ParseError:
                    continue
            
            return {"status": "NO_STORAGE_INFO"}
            
        except ET.ParseError:
            return {"status": "PARSE_ERROR"}
        except Exception as e:
            self.module.fail_json(msg=f"Error getting supported commands: {str(e)}")

    def get_raid_info(self):
        """Get RAID configuration."""
        raid_info = {}
        
        # Get embedded health data first
        xml_request = f"""<?xml version="1.0"?>
<RIBCL VERSION="2.23">
<LOGIN USER_LOGIN="{self.username}" PASSWORD="{self.password}">
<SERVER_INFO MODE="read">
<GET_EMBEDDED_HEALTH/>
</SERVER_INFO>
</LOGIN>
</RIBCL>"""

        response = self.send_xml(xml_request)
        if not response:
            return {"status": "NO_RESPONSE"}
            
        try:
            # Разделяем ответ на отдельные XML документы
            xml_docs = response.split('<?xml version="1.0"?>')
            for doc in xml_docs:
                if not doc.strip():
                    continue
                    
                try:
                    root = ET.fromstring('<?xml version="1.0"?>' + doc)
                    
                    # Проверяем статус ответа
                    response_node = root.find('.//RESPONSE')
                    if response_node is not None:
                        status = response_node.get('STATUS', 'N/A')
                        message = response_node.get('MESSAGE', 'N/A')
                        self.module.debug(f"\nResponse status: {status}")
                        self.module.debug(f"Response message: {message}")
                        if status != '0x0000':  # Если статус не OK
                            continue
                    
                    # Проверяем GET_EMBEDDED_HEALTH_DATA
                    health_data = root.find('.//GET_EMBEDDED_HEALTH_DATA')
                    if health_data is None:
                        continue
                        
                    storage = health_data.find('.//STORAGE')
                    if storage is None:
                        continue
                        
                    raid_info["status"] = "OK"
                    raid_info["controllers"] = []
                    
                    # Parse controller information
                    for controller in storage.findall('.//CONTROLLER'):
                        controller_info = {
                            "id": controller.find('.//LABEL').get('VALUE', '') if controller.find('.//LABEL') is not None else '',
                            "model": controller.find('.//MODEL').get('VALUE', '') if controller.find('.//MODEL') is not None else '',
                            "status": controller.find('.//STATUS').get('VALUE', '') if controller.find('.//STATUS') is not None else '',
                            "serial_number": controller.find('.//SERIAL_NUMBER').get('VALUE', '') if controller.find('.//SERIAL_NUMBER') is not None else '',
                            "firmware_version": controller.find('.//FW_VERSION').get('VALUE', '') if controller.find('.//FW_VERSION') is not None else '',
                            "volumes": []
                        }
                        
                        # Parse logical drives
                        for drive in controller.findall('.//LOGICAL_DRIVE'):
                            volume = {
                                "id": drive.find('.//LABEL').get('VALUE', '') if drive.find('.//LABEL') is not None else '',
                                "status": drive.find('.//STATUS').get('VALUE', '') if drive.find('.//STATUS') is not None else '',
                                "capacity": drive.find('.//CAPACITY').get('VALUE', '') if drive.find('.//CAPACITY') is not None else '',
                                "fault_tolerance": drive.find('.//FAULT_TOLERANCE').get('VALUE', '') if drive.find('.//FAULT_TOLERANCE') is not None else '',
                                "logical_drive_type": drive.find('.//LOGICAL_DRIVE_TYPE').get('VALUE', '') if drive.find('.//LOGICAL_DRIVE_TYPE') is not None else '',
                                "physical_drives": []
                            }
                            
                            # Parse physical drives in logical drive
                            for pdrive in drive.findall('.//PHYSICAL_DRIVE'):
                                physical_drive = {
                                    "label": pdrive.find('.//LABEL').get('VALUE', '') if pdrive.find('.//LABEL') is not None else '',
                                    "status": pdrive.find('.//STATUS').get('VALUE', '') if pdrive.find('.//STATUS') is not None else '',
                                    "serial_number": pdrive.find('.//SERIAL_NUMBER').get('VALUE', '') if pdrive.find('.//SERIAL_NUMBER') is not None else '',
                                    "model": pdrive.find('.//MODEL').get('VALUE', '') if pdrive.find('.//MODEL') is not None else '',
                                    "capacity": pdrive.find('.//CAPACITY').get('VALUE', '') if pdrive.find('.//CAPACITY') is not None else '',
                                    "location": pdrive.find('.//LOCATION').get('VALUE', '') if pdrive.find('.//LOCATION') is not None else '',
                                    "firmware_version": pdrive.find('.//FW_VERSION').get('VALUE', '') if pdrive.find('.//FW_VERSION') is not None else ''
                                }
                                volume["physical_drives"].append(physical_drive)
                            
                            controller_info["volumes"].append(volume)
                        
                        raid_info["controllers"].append(controller_info)
                        
                except ET.ParseError:
                    continue
            
            if not raid_info:
                return {"status": "NO_STORAGE_INFO"}
            
            return raid_info
            
        except ET.ParseError:
            return {"status": "PARSE_ERROR"}
        except Exception as e:
            self.module.fail_json(msg=f"Error getting RAID info: {str(e)}")

    def create_volume(self):
        """Create a new RAID volume"""
        # Validate parameters
        if not self.module.params['raid_level']:
            return {
                'changed': False,
                'msg': 'raid_level is required for volume creation',
                'raid_info': {'status': 'ERROR'}
            }
        
        if not self.module.params['drives'] or len(self.module.params['drives']) < 2:
            return {
                'changed': False,
                'msg': 'At least 2 drives are required for volume creation',
                'raid_info': {'status': 'ERROR'}
            }
        
        if not self.module.params['volume_name']:
            return {
                'changed': False,
                'msg': 'volume_name is required for volume creation',
                'raid_info': {'status': 'ERROR'}
            }
        
        # Construct XML request for volume creation
        xml_request = f'''<?xml version="1.0"?>
        <RIBCL VERSION="2.0">
            <LOGIN USER_LOGIN="{self.module.params['username']}" PASSWORD="{self.module.params['password']}">
                <STORAGE>
                    <CREATE_LOGICAL_DRIVE>
                        <CONTROLLER VALUE="{self.module.params['controller']}"/>
                        <RAID_LEVEL VALUE="{self.module.params['raid_level']}"/>
                        <VOLUME_NAME VALUE="{self.module.params['volume_name']}"/>'''
                        
        if self.module.params['size_gb']:
            xml_request += f'\n                        <SIZE_GB VALUE="{self.module.params["size_gb"]}"/>'
            
        # Add physical drives
        for drive in self.module.params['drives']:
            xml_request += f'\n                        <PHYSICAL_DRIVE VALUE="{drive}"/>'
            
        # Add spare drives if specified
        if self.module.params.get('spare_drives'):
            for drive in self.module.params['spare_drives']:
                xml_request += f'\n                        <SPARE_DRIVE VALUE="{drive}"/>'
                
        xml_request += '''
                    </CREATE_LOGICAL_DRIVE>
                </STORAGE>
            </LOGIN>
        </RIBCL>'''
        
        response = self.send_xml(xml_request)
        if response is None:
            return {
                'changed': False,
                'msg': 'Failed to get response from iLO',
                'raid_info': {'status': 'NO_RESPONSE'}
            }
        
        try:
            root = ET.fromstring(response)
            status_node = root.find('.//STATUS')
            if status_node is not None and status_node.get('VALUE') == '0':
                # Get updated RAID configuration
                raid_info = self.get_raid_info()
                raid_info['status'] = 'OK'
                return {
                    'changed': True,
                    'msg': f'Volume {self.module.params["volume_name"]} created successfully',
                    'raid_info': raid_info
                }
        else:
                error_msg = root.find('.//MESSAGE').get('VALUE') if root.find('.//MESSAGE') is not None else 'Unknown error'
                return {
                    'changed': False,
                    'msg': f'Failed to create volume: {error_msg}',
                    'raid_info': {'status': 'ERROR'}
                }
        except ET.ParseError:
            return {
                'changed': False,
                'msg': 'Failed to parse XML response',
                'raid_info': {'status': 'PARSE_ERROR'}
            }

    def delete_volume(self):
        """Delete a RAID volume"""
        if not self.module.params['volume_name']:
        return {
                'changed': False,
                'msg': 'volume_name is required for volume deletion',
                'raid_info': {'status': 'ERROR'}
        }

        # Construct XML request for volume deletion
        xml_request = f'''<?xml version="1.0"?>
        <RIBCL VERSION="2.0">
            <LOGIN USER_LOGIN="{self.module.params['username']}" PASSWORD="{self.module.params['password']}">
                <STORAGE>
                    <DELETE_LOGICAL_DRIVE>
                        <CONTROLLER VALUE="{self.module.params['controller']}"/>
                        <VOLUME_NAME VALUE="{self.module.params['volume_name']}"/>
                    </DELETE_LOGICAL_DRIVE>
                </STORAGE>
            </LOGIN>
        </RIBCL>'''
        
        response = self.send_xml(xml_request)
        if response is None:
            return {
                'changed': False,
                'msg': 'Failed to get response from iLO',
                'raid_info': {'status': 'NO_RESPONSE'}
            }
        
        try:
            root = ET.fromstring(response)
            status_node = root.find('.//STATUS')
            if status_node is not None and status_node.get('VALUE') == '0':
                # Get updated RAID configuration
                raid_info = self.get_raid_info()
                raid_info['status'] = 'OK'
                return {
                    'changed': True,
                    'msg': f'Volume "{self.module.params["volume_name"]}" deleted successfully',
                    'raid_info': raid_info
                }
            else:
                error_msg = root.find('.//MESSAGE').get('VALUE') if root.find('.//MESSAGE') is not None else 'Unknown error'
                return {
                    'changed': False,
                    'msg': f'Failed to delete volume: {error_msg}',
                    'raid_info': {'status': 'ERROR'}
                }
        except ET.ParseError:
            return {
                'changed': False,
                'msg': 'Failed to parse XML response',
                'raid_info': {'status': 'PARSE_ERROR'}
            }

    def get_physical_drives(self):
        """Get information about physical drives"""
        drives_info = {
            'changed': False,
            'msg': '',
            'raid_info': {
                'status': 'OK',
                'physical_drives': [],
                'backplane': {},
                'zone_table': {}
            }
        }

        # Получаем информацию о дисках через GET_EMBEDDED_HEALTH
        xml_request = f"""<?xml version="1.0"?>
<RIBCL VERSION="2.23">
<LOGIN USER_LOGIN="{self.username}" PASSWORD="{self.password}">
                <SERVER_INFO MODE="read">
                    <GET_EMBEDDED_HEALTH/>
                </SERVER_INFO>
            </LOGIN>
</RIBCL>"""
        
        response = self.send_xml(xml_request)
        if not response:
            return {
                'changed': False,
                'msg': 'Failed to get response from iLO',
                'raid_info': {'status': 'NO_RESPONSE'}
            }
        
        self.module.debug(f"Raw XML response from GET_EMBEDDED_HEALTH: {response}")
        
        try:
            # Разделяем ответ на отдельные XML документы
            xml_docs = response.split('<?xml version="1.0"?>')
            for doc in xml_docs:
                if not doc.strip():
                    continue
                    
                try:
                    root = ET.fromstring('<?xml version="1.0"?>' + doc)
                    
                    # Проверяем статус ответа
                    response_node = root.find('.//RESPONSE')
                    if response_node is not None:
                        status = response_node.get('STATUS', 'N/A')
                        message = response_node.get('MESSAGE', 'N/A')
                        self.module.debug(f"\nResponse status: {status}")
                        self.module.debug(f"Response message: {message}")
                        if status != '0x0000':  # Если статус не OK
                            continue
                    
                    # Проверяем GET_EMBEDDED_HEALTH_DATA
                    health_data = root.find('.//GET_EMBEDDED_HEALTH_DATA')
                    if health_data is None:
                        continue
                        
                    storage = health_data.find('.//STORAGE')
                    if storage is None:
                        self.module.debug("No STORAGE section found in XML")
                        continue
                        
                    # Ищем нужный контроллер
                    for controller in storage.findall('.//CONTROLLER'):
                        model = controller.find('MODEL')
                        if model is None:
                            self.module.debug("No MODEL element found in controller")
                            continue
                            
                        model_value = model.get('VALUE')
                        self.module.debug(f"Found controller model: {model_value}")
                        
                        if model_value == self.controller:
                            self.module.debug("Found matching controller")
                            
                            # Собираем информацию о физических дисках
                            for drive_enclosure in controller.findall('.//DRIVE_ENCLOSURE'):
                                self.module.debug("Processing drive enclosure")
                                drive_info = {
                                    'label': drive_enclosure.find('LABEL').get('VALUE') if drive_enclosure.find('LABEL') is not None else 'Unknown',
                                    'status': drive_enclosure.find('STATUS').get('VALUE') if drive_enclosure.find('STATUS') is not None else 'Unknown',
                                    'drive_bay': drive_enclosure.find('DRIVE_BAY').get('VALUE') if drive_enclosure.find('DRIVE_BAY') is not None else 'Unknown'
                                }
                                drives_info['raid_info']['physical_drives'].append(drive_info)
                                
                            # Также собираем информацию о дисках в логических томах
                            for logical_drive in controller.findall('.//LOGICAL_DRIVE'):
                                self.module.debug("Processing logical drive")
                                for physical_drive in logical_drive.findall('.//PHYSICAL_DRIVE'):
                                    self.module.debug("Processing physical drive")
                                    drive_info = {
                                        'label': physical_drive.find('LABEL').get('VALUE') if physical_drive.find('LABEL') is not None else 'Unknown',
                                        'status': physical_drive.find('STATUS').get('VALUE') if physical_drive.find('STATUS') is not None else 'Unknown',
                                        'serial_number': physical_drive.find('SERIAL_NUMBER').get('VALUE') if physical_drive.find('SERIAL_NUMBER') is not None else 'Unknown',
                                        'model': physical_drive.find('MODEL').get('VALUE') if physical_drive.find('MODEL') is not None else 'Unknown',
                                        'capacity': physical_drive.find('CAPACITY').get('VALUE') if physical_drive.find('CAPACITY') is not None else 'Unknown',
                                        'location': physical_drive.find('LOCATION').get('VALUE') if physical_drive.find('LOCATION') is not None else 'Unknown',
                                        'firmware_version': physical_drive.find('FW_VERSION').get('VALUE') if physical_drive.find('FW_VERSION') is not None else 'Unknown'
                                    }
                                    drives_info['raid_info']['physical_drives'].append(drive_info)
                except ET.ParseError:
                    continue
                    
        except ET.ParseError as e:
            self.module.debug(f"XML parse error in GET_EMBEDDED_HEALTH: {str(e)}")
            return {
                'changed': False,
                'msg': 'Failed to parse XML response from GET_EMBEDDED_HEALTH',
                'raid_info': {'status': 'PARSE_ERROR'}
            }

        # Получаем информацию о бэкплейне через READ_BACKPLANE_INFO
        xml_request = f"""<?xml version="1.0"?>
            <RIBCL VERSION="2.23">
                <LOGIN USER_LOGIN="{self.username}" PASSWORD="{self.password}">
<HARD_DRIVE_ZONE MODE="read">
<READ_BACKPLANE_INFO/>
</HARD_DRIVE_ZONE>
                </LOGIN>
</RIBCL>"""

        response = self.send_xml(xml_request)
        if response:
            self.module.debug(f"Raw XML response from READ_BACKPLANE_INFO: {response}")
            try:
                root = ET.fromstring(response)
                backplane_info = root.find('.//READ_BACKPLANE_INFO')
                if backplane_info is not None:
                    drives_info['raid_info']['backplane'] = {
                        'type_id': backplane_info.find('TYPE_ID').get('VALUE') if backplane_info.find('TYPE_ID') is not None else 'Unknown',
                        'sep_node_id': backplane_info.find('SEP_NODE_ID').get('VALUE') if backplane_info.find('SEP_NODE_ID') is not None else 'Unknown',
                        'wwid': backplane_info.find('WWID').get('VALUE') if backplane_info.find('WWID') is not None else 'Unknown',
                        'sep_id': backplane_info.find('SEP_ID').get('VALUE') if backplane_info.find('SEP_ID') is not None else 'Unknown',
                        'backplane_name': backplane_info.find('BACKPLANE_NAME').get('VALUE') if backplane_info.find('BACKPLANE_NAME') is not None else 'Unknown',
                        'fw_rev': backplane_info.find('FW_REV').get('VALUE') if backplane_info.find('FW_REV') is not None else 'Unknown',
                        'bay_cnt': backplane_info.find('BAY_CNT').get('VALUE') if backplane_info.find('BAY_CNT') is not None else 'Unknown',
                        'start_bay': backplane_info.find('START_BAY').get('VALUE') if backplane_info.find('START_BAY') is not None else 'Unknown',
                        'host_port_cnt': backplane_info.find('HOST_PORT_CNT').get('VALUE') if backplane_info.find('HOST_PORT_CNT') is not None else 'Unknown',
                        'host_ports': []
                    }
                    
                    # Собираем информацию о портах хоста
                    for host_port in backplane_info.findall('.//HOST_PORT'):
                        port_info = {
                            'value': host_port.get('VALUE'),
                            'node_num': host_port.find('NODE_NUM').get('VALUE') if host_port.find('NODE_NUM') is not None else 'Unknown',
                            'slot_num': host_port.find('SLOT_NUM').get('VALUE') if host_port.find('SLOT_NUM') is not None else 'Unknown'
                        }
                        drives_info['raid_info']['backplane']['host_ports'].append(port_info)
            except ET.ParseError as e:
                self.module.debug(f"XML parse error in READ_BACKPLANE_INFO: {str(e)}")

        # Получаем информацию о зонах через READ_ZONE_TABLE
        xml_request = f"""<?xml version="1.0"?>
            <RIBCL VERSION="2.23">
                <LOGIN USER_LOGIN="{self.username}" PASSWORD="{self.password}">
<HARD_DRIVE_ZONE MODE="read">
<READ_ZONE_TABLE/>
</HARD_DRIVE_ZONE>
                </LOGIN>
</RIBCL>"""

        response = self.send_xml(xml_request)
        if response:
            self.module.debug(f"Raw XML response from READ_ZONE_TABLE: {response}")
            try:
                root = ET.fromstring(response)
                zone_table = root.find('.//READ_ZONE_TABLE')
                if zone_table is not None:
                    drives_info['raid_info']['zone_table'] = {
                        'type_id': zone_table.find('TYPE_ID').get('VALUE') if zone_table.find('TYPE_ID') is not None else 'Unknown',
                        'sep_node_id': zone_table.find('SEP_NODE_ID').get('VALUE') if zone_table.find('SEP_NODE_ID') is not None else 'Unknown',
                        'host_ports': []
                    }
                    
                    # Собираем информацию о портах хоста и их отсеках
                    for host_port in zone_table.findall('.//HOST_PORT'):
                        port_info = {
                            'value': host_port.get('VALUE'),
                            'bays': []
                        }
                        for bay in host_port.findall('.//BAY'):
                            port_info['bays'].append(bay.get('VALUE'))
                        drives_info['raid_info']['zone_table']['host_ports'].append(port_info)
            except ET.ParseError as e:
                self.module.debug(f"XML parse error in READ_ZONE_TABLE: {str(e)}")

        if not drives_info['raid_info']['physical_drives']:
            drives_info['msg'] = 'No physical drives found'
            drives_info['raid_info']['status'] = 'NO_STORAGE_INFO'
        else:
            drives_info['msg'] = 'Physical drives information retrieved successfully'
            
        return drives_info

    def run(self):
        """Run the module"""
        result = {}
        
        if self.module.params['state'] == 'get':
                result = self.get_raid_info()
        elif self.module.params['state'] == 'get_commands':
                result = self.get_supported_commands()
        elif self.module.params['state'] == 'get_drives':
            result = self.get_physical_drives()
        elif self.module.params['state'] == 'present':
            result = self.create_volume()
        elif self.module.params['state'] == 'absent':
            result = self.delete_volume()
                
            return result

def main():
    """Main function."""
    module_args = dict(
            hostname=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
        state=dict(type='str', default='get', choices=['get', 'get_commands', 'get_drives', 'present', 'absent']),
        controller=dict(type='str', required=True),
        raid_level=dict(type='str', required=False),
        drives=dict(type='list', elements='str', required=False),
            volume_name=dict(type='str', required=False),
        size_gb=dict(type='int', required=False),
        spare_drives=dict(type='list', elements='str', required=False)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[
            ('state', 'present', ['raid_level', 'drives', 'volume_name']),
            ('state', 'absent', ['volume_name'])
        ]
    )

    ilo = IloRAIDModule(module)
    result = ilo.run()
    
    if result.get('changed') is not None:
        module.exit_json(**result)
    else:
            module.exit_json(
            changed=False,
            msg=result.get('msg', 'Operation completed'),
            raid_info=result
        )

if __name__ == '__main__':
    main() 
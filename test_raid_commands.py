#!/usr/bin/python
import requests
import urllib3
import os
import sys
import xml.etree.ElementTree as ET

# Отключаем предупреждения о непроверенных HTTPS запросах
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Добавляем путь к модулю
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plugins.module_utils.ribcl_parser import RibclParser

def send_command(xml):
    host = os.environ.get('ILO_HOST')
    user = os.environ.get('ILO_USERNAME')
    password = os.environ.get('ILO_PASSWORD')

    if not all([host, user, password]):
        print("Error: Set ILO_HOST, ILO_USERNAME, ILO_PASSWORD environment variables")
        sys.exit(1)

    response = requests.post(
        f"https://{host}/ribcl",
        data=xml,
        verify=False,
        auth=(user, password),
        headers={'Content-Type': 'application/xml'}
    )
    
    return response.content.decode('utf-8', errors='ignore')

def parse_storage_info(xml_str):
    # Разделяем ответ на отдельные XML документы
    xml_docs = xml_str.split('<?xml version="1.0"?>')
    
    # Ищем документ с GET_EMBEDDED_HEALTH_DATA
    for doc in xml_docs:
        if not doc.strip():
            continue
            
        try:
            root = ET.fromstring('<?xml version="1.0"?>' + doc)
            
            # Проверяем статус ответа
            response = root.find('.//RESPONSE')
            if response is not None:
                status = response.get('STATUS', 'N/A')
                message = response.get('MESSAGE', 'N/A')
                print(f"\nResponse status: {status}")
                print(f"Response message: {message}")
                if status != '0x0000':  # Если статус не OK
                    continue
            
            # Проверяем GET_EMBEDDED_HEALTH_DATA
            health_data = root.find('.//GET_EMBEDDED_HEALTH_DATA')
            if health_data is not None:
                storage = health_data.find('.//STORAGE')
                if storage is None:
                    continue
                    
                print("\nStorage Information:")
                print("=" * 50)
                
                # Parse controller information
                for controller in storage.findall('.//CONTROLLER'):
                    print("\nController:")
                    print("-" * 20)
                    
                    for elem in controller:
                        if elem.tag in ['LABEL', 'MODEL', 'STATUS', 'CONTROLLER_STATUS', 'SERIAL_NUMBER', 'FW_VERSION']:
                            value = elem.get('VALUE', 'N/A')
                            print(f"{elem.tag}: {value}")
                            
                    # Parse drive enclosures
                    for enclosure in controller.findall('.//DRIVE_ENCLOSURE'):
                        print("\n  Drive Enclosure:")
                        print("  " + "-" * 18)
                        
                        for elem in enclosure:
                            if elem.tag in ['LABEL', 'STATUS', 'DRIVE_BAY']:
                                value = elem.get('VALUE', 'N/A')
                                print(f"  {elem.tag}: {value}")
                                
                    # Parse logical drives
                    for drive in controller.findall('.//LOGICAL_DRIVE'):
                        print("\n  Logical Drive:")
                        print("  " + "-" * 18)
                        
                        for elem in drive:
                            if elem.tag in ['LABEL', 'STATUS', 'CAPACITY', 'FAULT_TOLERANCE', 'LOGICAL_DRIVE_TYPE']:
                                value = elem.get('VALUE', 'N/A')
                                print(f"  {elem.tag}: {value}")
                                
                        # Parse physical drives in logical drive
                        for pdrive in drive.findall('.//PHYSICAL_DRIVE'):
                            print("\n    Physical Drive:")
                            print("    " + "-" * 16)
                            
                            for elem in pdrive:
                                if elem.tag in ['LABEL', 'STATUS', 'SERIAL_NUMBER', 'MODEL', 'CAPACITY', 'LOCATION', 'FW_VERSION']:
                                    value = elem.get('VALUE', 'N/A')
                                    print(f"    {elem.tag}: {value}")
                        
        except ET.ParseError as e:
            print(f"Error parsing XML document: {e}")
            continue

# Отправляем GET_EMBEDDED_HEALTH
print("\n=== GET_EMBEDDED_HEALTH ===")
xml = f"""<?xml version="1.0"?>
<RIBCL VERSION="2.23">
<LOGIN USER_LOGIN="{os.environ.get('ILO_USERNAME')}" PASSWORD="{os.environ.get('ILO_PASSWORD')}">
<SERVER_INFO MODE="read">
<GET_EMBEDDED_HEALTH/>
</SERVER_INFO>
</LOGIN>
</RIBCL>"""
response = send_command(xml)

print("\nRaw response:")
print("-" * 20)
print(response)

# Парсим и выводим информацию
xml_docs = response.split('<?xml version="1.0"?>')
for doc in xml_docs:
    if not doc.strip():
        continue
        
    try:
        root = ET.fromstring('<?xml version="1.0"?>' + doc)
        health_data = root.find('.//GET_EMBEDDED_HEALTH_DATA')
        if health_data is not None:
            storage = health_data.find('.//STORAGE')
            if storage is None:
                continue
                
            print("\nStorage Information:")
            print("=" * 50)
            
            # Информация о контроллере
            for controller in storage.findall('.//CONTROLLER'):
                print("\nController:")
                print("-" * 20)
                for elem in controller:
                    if elem.tag in ['LABEL', 'MODEL', 'STATUS', 'CONTROLLER_STATUS', 'SERIAL_NUMBER', 'FW_VERSION']:
                        value = elem.get('VALUE', 'N/A')
                        print(f"{elem.tag}: {value}")
                
                # Информация о физических дисках
                print("\nPhysical Drives:")
                print("-" * 20)
                for enclosure in controller.findall('.//DRIVE_ENCLOSURE'):
                    for elem in enclosure:
                        if elem.tag in ['LABEL', 'STATUS', 'DRIVE_BAY']:
                            value = elem.get('VALUE', 'N/A')
                            print(f"{elem.tag}: {value}")
                
                # Информация о логических дисках
                print("\nLogical Drives:")
                print("-" * 20)
                logical_drives = controller.findall('.//LOGICAL_DRIVE')
                if not logical_drives:
                    print("No logical drives configured")
                for drive in logical_drives:
                    print("\n  Logical Drive:")
                    for elem in drive:
                        if elem.tag in ['LABEL', 'STATUS', 'CAPACITY', 'FAULT_TOLERANCE', 'LOGICAL_DRIVE_TYPE']:
                            value = elem.get('VALUE', 'N/A')
                            print(f"  {elem.tag}: {value}")
                    
                    print("\n  Physical drives in this logical drive:")
                    for pdrive in drive.findall('.//PHYSICAL_DRIVE'):
                        print("\n    Physical Drive:")
                        for elem in pdrive:
                            if elem.tag in ['LABEL', 'STATUS', 'SERIAL_NUMBER', 'MODEL', 'CAPACITY', 'LOCATION', 'FW_VERSION', 'DRIVE_CONFIGURATION', 'ENCRYPTION_STATUS', 'MEDIA_TYPE']:
                                value = elem.get('VALUE', 'N/A')
                                print(f"    {elem.tag}: {value}")
                
    except ET.ParseError as e:
        print(f"Error parsing XML document: {e}")
        continue 
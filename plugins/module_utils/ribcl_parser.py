"""
Simple parser for RIBCL XML format.
"""

import re
from typing import Dict, List, Optional, Union, Tuple, Any

class RibclNode:
    def __init__(self, tag: str, attributes: Dict[str, str] = None, children: List['RibclNode'] = None):
        self.tag = tag
        self.attributes = attributes or {}
        self.children = children or []
        self.text: Optional[str] = None
        
    def add_child(self, node: 'RibclNode'):
        self.children.append(node)
        
    def find(self, path: str) -> Optional['RibclNode']:
        """Find first node matching the path.
        
        Path format: tag1/tag2/tag3
        Example: GET_EMBEDDED_HEALTH_DATA/STORAGE/CONTROLLER
        """
        parts = path.strip('/').split('/')
        current = self
        
        for part in parts:
            found = False
            for child in current.children:
                if child.tag == part:
                    current = child
                    found = True
                    break
            if not found:
                return None
                
        return current
        
    def findall(self, path: str) -> List['RibclNode']:
        """Find all nodes matching the path.
        
        Path format: tag1/tag2/tag3 or .//tag for any depth search
        Examples: 
        - GET_EMBEDDED_HEALTH_DATA/STORAGE/CONTROLLER
        - .//CONTROLLER
        """
        results = []
        
        # Handle .//tag format (search at any depth)
        if path.startswith('.//'):
            tag = path[3:]
            def _find_recursive(node: 'RibclNode'):
                if node.tag == tag:
                    results.append(node)
                for child in node.children:
                    _find_recursive(child)
            _find_recursive(self)
            return results
            
        # Handle path/to/tag format
        parts = path.strip('/').split('/')
        
        def _find_path(node: 'RibclNode', parts: List[str], depth: int):
            if depth == len(parts):
                results.append(node)
                return
                
            for child in node.children:
                if child.tag == parts[depth]:
                    _find_path(child, parts, depth + 1)
                    
        _find_path(self, parts, 0)
        return results
        
    def get(self, attr: str, default: str = None) -> Optional[str]:
        """Get attribute value."""
        return self.attributes.get(attr, default)

    def to_dict(self):
        result = {
            'tag': self.tag,
            'attributes': self.attributes
        }
        if self.children:
            result['children'] = [child.to_dict() for child in self.children]
        return result

class RibclParser:
    def __init__(self, debug_callback=None):
        self.debug_callback = debug_callback

    def debug(self, message):
        if self.debug_callback:
            self.debug_callback(message)

    def _parse_xml(self, xml_text: str) -> RibclNode:
        """Parse XML text into a RibclNode tree."""
        if not xml_text:
            print("DEBUG: Empty XML text")
            return None
            
        print("\nDEBUG: Parsing XML text:")
        print("="*80)
        print(xml_text)
        print("="*80)
        
        pos = 0
        xml_text = xml_text.strip()
        
        # Skip XML declaration if present
        if xml_text.startswith('<?xml'):
            pos = xml_text.find('?>') + 2
            xml_text = xml_text[pos:].strip()
            print("\nDEBUG: After skipping XML declaration:")
            print(xml_text[:200])
            
        # Parse root node
        root = None
        while pos < len(xml_text):
            # Skip whitespace
            while pos < len(xml_text) and xml_text[pos].isspace():
                pos += 1
                
            if pos >= len(xml_text):
                break
                
            # Parse opening tag
            if xml_text[pos] == '<':
                if xml_text[pos+1] == '/':
                    # Skip closing tags at root level
                    pos = xml_text.find('>', pos) + 1
                    continue
                    
                tag_end = xml_text.find('>', pos)
                if tag_end == -1:
                    print(f"DEBUG: Unclosed tag at position {pos}")
                    raise ValueError(f"Unclosed tag at position {pos}")
                    
                tag_text = xml_text[pos+1:tag_end]
                print(f"\nDEBUG: Found tag: {tag_text}")
                
                if ' ' in tag_text:
                    tag_name = tag_text[:tag_text.find(' ')]
                    attr_text = tag_text[tag_text.find(' ')+1:]
                else:
                    tag_name = tag_text.rstrip('/')
                    attr_text = ''
                    
                # Create node
                node = RibclNode(tag_name)
                print(f"DEBUG: Created node with tag: {tag_name}")
                
                # Parse attributes
                if attr_text:
                    print(f"DEBUG: Parsing attributes: {attr_text}")
                    parts = re.findall(r'(\w+)="([^"]*)"', attr_text)
                    for name, value in parts:
                        node.attributes[name] = value
                    print(f"DEBUG: Parsed attributes: {node.attributes}")
                        
                # Handle self-closing tags
                if tag_text.endswith('/'):
                    pos = tag_end + 1
                    if root is None:
                        root = node
                        print("DEBUG: Set self-closing tag as root")
                    continue
                    
                # Parse child nodes recursively
                pos = tag_end + 1
                child_pos = pos
                while child_pos < len(xml_text):
                    if xml_text[child_pos] == '<':
                        if xml_text[child_pos+1] == '/':
                            # Found closing tag
                            if xml_text[child_pos+2:].startswith(tag_name):
                                pos = xml_text.find('>', child_pos) + 1
                                break
                        else:
                            # Found child node
                            child_node = self._parse_node(xml_text[child_pos:])
                            if child_node:
                                node.children.append(child_node)
                                print(f"DEBUG: Added child node: {child_node.tag}")
                                child_pos = xml_text.find('>', child_pos) + 1
                                continue
                    child_pos += 1
                    
                if root is None:
                    root = node
                    print(f"DEBUG: Set node as root: {node.tag}")
            else:
                pos += 1
                
        if root is None:
            print("DEBUG: No root node found")
        else:
            print("\nDEBUG: Final root node structure:")
            print(root.to_dict())
            
        return root
        
    def _parse_node(self, xml_text: str) -> Optional[RibclNode]:
        """Parse an XML node.
        
        Args:
            xml_text: The XML text to parse
            
        Returns:
            The parsed node or None if no node was found
        """
        # Skip whitespace at start
        pos = 0
        while pos < len(xml_text) and xml_text[pos].isspace():
            pos += 1
            
        if pos >= len(xml_text):
            return None
            
        # Parse opening tag
        if xml_text[pos] != '<':
            return None
            
        tag_end = xml_text.find('>', pos)
        if tag_end == -1:
            self.debug(f"Unclosed tag at position {pos}")
            return None
            
        tag_text = xml_text[pos+1:tag_end]
        self.debug(f"Found tag: {tag_text}")
        
        if ' ' in tag_text:
            tag_name = tag_text[:tag_text.find(' ')]
            attr_text = tag_text[tag_text.find(' ')+1:]
        else:
            tag_name = tag_text.rstrip('/')
            attr_text = ''
            
        # Create node
        node = RibclNode(tag_name)
        self.debug(f"Created node with tag: {tag_name}")
        
        # Parse attributes
        if attr_text:
            self.debug(f"Parsing attributes: {attr_text}")
            parts = re.findall(r'(\w+)="([^"]*)"', attr_text)
            for name, value in parts:
                node.attributes[name] = value
            self.debug(f"Parsed attributes: {node.attributes}")
                
        # Handle self-closing tags
        if tag_text.endswith('/'):
            return node
            
        # Parse child nodes
        pos = tag_end + 1
        while pos < len(xml_text):
            if xml_text[pos] == '<':
                if xml_text[pos+1] == '/':
                    # Found closing tag
                    if xml_text[pos+2:].startswith(tag_name):
                        break
                else:
                    # Found child node
                    child_node = self._parse_node(xml_text[pos:])
                    if child_node:
                        node.children.append(child_node)
                        self.debug(f"Added child node: {child_node.tag}")
                        pos = xml_text.find('>', pos) + 1
                        continue
            pos += 1
            
        return node

    def parse_response(self, response_text: str) -> List[RibclNode]:
        """Parse RIBCL response text into a list of RibclNode trees."""
        if not response_text:
            self.debug("Empty response text")
            return []
            
        self.debug(f"Parsing response text: {response_text[:200]}...")
        
        # Split response into individual XML documents
        documents = []
        current_doc = []
        in_doc = False
        
        for line in response_text.splitlines():
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('<?xml'):
                if current_doc:
                    doc_text = '\n'.join(current_doc)
                    node = self._parse_xml(doc_text)
                    if node:
                        documents.append(node)
                    current_doc = []
                current_doc.append(line)
                in_doc = True
            elif in_doc:
                current_doc.append(line)
                
        if current_doc:
            doc_text = '\n'.join(current_doc)
            node = self._parse_xml(doc_text)
            if node:
                documents.append(node)
                
        self.debug(f"Found {len(documents)} XML documents")
        for i, doc in enumerate(documents):
            self.debug(f"Document {i+1}: {doc.to_dict()}")
            
        return documents

    def _parse_xml_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract useful data from RIBCL XML response using regex.
        
        Args:
            response_text: The XML response text to parse
            
        Returns:
            A list of dictionaries containing the extracted data
        """
        if not response_text:
            return []
        
        # Find all STORAGE sections
        storage_sections = re.findall(r'<STORAGE>(.*?)</STORAGE>', response_text, re.DOTALL)
        if not storage_sections:
            return []
        
        result = []
        for section in storage_sections:
            # Extract controller info
            controllers = re.findall(r'<CONTROLLER[^>]*>(.*?)</CONTROLLER>', section, re.DOTALL)
            for controller in controllers:
                controller_info = {}
                
                # Get label
                match = re.search(r'<LABEL[^>]*VALUE\s*=\s*["\']([^"\']*)["\']', controller)
                if match:
                    controller_info['name'] = match.group(1)
                    
                # Get status
                match = re.search(r'<STATUS[^>]*VALUE\s*=\s*["\']([^"\']*)["\']', controller)
                if match:
                    controller_info['status'] = match.group(1)
                    
                # Get model
                match = re.search(r'<MODEL[^>]*VALUE\s*=\s*["\']([^"\']*)["\']', controller)
                if match:
                    controller_info['model'] = match.group(1)
                    
                # Get serial number
                match = re.search(r'<SERIAL_NUMBER[^>]*VALUE\s*=\s*["\']([^"\']*)["\']', controller)
                if match:
                    controller_info['serial_number'] = match.group(1)
                    
                # Get firmware version
                match = re.search(r'<FW_VERSION[^>]*VALUE\s*=\s*["\']([^"\']*)["\']', controller)
                if match:
                    controller_info['firmware_version'] = match.group(1)
                    
                # Get drive enclosures
                enclosures = re.findall(r'<DRIVE_ENCLOSURE>(.*?)</DRIVE_ENCLOSURE>', controller, re.DOTALL)
                if enclosures:
                    controller_info['drive_enclosures'] = []
                    for enclosure in enclosures:
                        enclosure_info = {}
                        
                        match = re.search(r'<LABEL[^>]*VALUE\s*=\s*["\']([^"\']*)["\']', enclosure)
                        if match:
                            enclosure_info['label'] = match.group(1)
                            
                        match = re.search(r'<STATUS[^>]*VALUE\s*=\s*["\']([^"\']*)["\']', enclosure)
                        if match:
                            enclosure_info['status'] = match.group(1)
                            
                        match = re.search(r'<DRIVE_BAY[^>]*VALUE\s*=\s*["\']([^"\']*)["\']', enclosure)
                        if match:
                            enclosure_info['drive_bay'] = match.group(1)
                            
                        controller_info['drive_enclosures'].append(enclosure_info)
                        
                result.append(controller_info)
                
        # Check for discovery status
        match = re.search(r'<DISCOVERY_STATUS>.*?<STATUS[^>]*VALUE\s*=\s*["\']([^"\']*)["\']', section, re.DOTALL)
        if match:
            result.append({'discovery_status': match.group(1)})
            
        # Check for error response
        match = re.search(r'<RESPONSE[^>]*STATUS\s*=\s*["\']([^"\']*)["\'].*?MESSAGE\s*=\s*["\']([^"\']*)["\']', response_text)
        if match and match.group(1) != '0x0000':
            raise Exception(f"Error response: {match.group(2)} (status: {match.group(1)})")
            
        return result 
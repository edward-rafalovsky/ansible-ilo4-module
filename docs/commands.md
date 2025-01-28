# HPE iLO SMASH CLP Command Reference

## SSH Overview and Access

### Features
- Secure command line access to iLO
- Support for SSH protocol version 2
- Public key authentication
- Command line interface based on SMASH CLP standard
- Multiple simultaneous sessions support

### Connection Requirements
- SSH client supporting SSHv2
- Network access to iLO management port
- Valid iLO user credentials or SSH key
- Proper user privileges for commands

### SSH Key Authorization
- Supports both password and public key authentication
- Compatible with OpenSSH and PuTTY key formats
- Keys can be imported from:
  - PuTTY key generator (PPK format)
  - ssh-keygen (OpenSSH format)
- Maximum key length: 2048 bits
- Supported algorithms: RSA, DSA

## Access Methods
- Serial port using one connection (ESC ()
- Network using SSH (requires IP/DNS name, login, password)
  - Maximum 5 simultaneous network connections
  - Max login name length: 127 characters
  - Max password length: 63 characters
  - Connection timeout: 10 minutes of inactivity

## Command Line Format
- General syntax: `<verb> <target> <option> <property>`
- Default target is `/`
- Boolean values accepted: yes, no, true, false, y, n, t, f, 1, 0
- Case-sensitive commands and parameters
- Command completion using Tab key
- Command history using arrow keys

## Session Management
- Session timeout: 10 minutes by default
- Maximum concurrent sessions: 5
- Session termination:
  - Using `exit` command
  - Connection timeout
  - Administrator forced termination

## Escape Commands
- `ESC R` or `ESC r` - Reset system
- `ESC ^` - Power on system
- `ESC ESC` - Erase current line
- `ESC (` - Switch to Serial interface
Note: One second timeout for entering escape sequence characters

## Base Commands
- `help` - Display context-sensitive help
- `command help/?` - Display help for specific command
- `exit` - Terminate CLP session
- `cd` - Change current default target
- `show` - Display values/contents
- `create` - Create new instance
- `delete` - Remove instances
- `load` - Move binary image from URL
- `reset` - Cycle target from enabled to disabled and back
- `set` - Set property values
- `start` - Change target state to higher run level
- `stop` - Change target state to lower run level
- `version` - Query CLP implementation version

## Command Line Interface Structure

### Target Addressing
- Uses hierarchical namespace similar to filesystem
- Absolute paths start with `/`
- Relative paths are based on current target
- Use `cd` to navigate between targets
- Use `show -display targets` to list available targets

### Output Format
- Status line format: `status=<code>`
- Common status codes:
  - 0: Success
  - 1: Error
  - 2: Invalid parameter
  - 3: Operation not supported
- Command output includes:
  - Status code and message
  - Timestamp
  - Command-specific data
  - Error details (if any)

### Command Properties
- Properties are key-value pairs
- Case-sensitive names
- Multiple properties separated by space
- Values containing spaces must be quoted
- Use `show -display properties` to list available properties

## System Management

### System Information
```
show /system1
```
Displays:
- Server model and serial number
- BIOS version
- iLO firmware version
- System health status
- Power state

### Hardware Information
```
show /system1/[cpu1|memory1|fans1|temps1]
```
Available subsystems:
- `cpu1` - Processor information
- `memory1` - Memory configuration
- `fans1` - Fan status and speeds
- `temps1` - Temperature sensors

### Firmware Management
```
load -source <url> -oemhpe_waitforreboot yes
```
Options:
- `-source` - URL to firmware image
- `-oemhpe_waitforreboot` - Wait for reboot completion
- Supported protocols: HTTP, HTTPS, TFTP

### System Logs
```
show /system1/log1
```
Types:
- IML (Integrated Management Log)
- iLO Event Log
- Security Log
- Active Health System Log

## Power Management

### Advanced Power Settings
```
show /system1/power1
```
Displays:
- Power supply status
- Power readings
- Power capping configuration
- Power micro-controller version

### Power Regulation
```
set /system1/power1 regulation_mode=<mode>
```
Available modes:
- `os_control` - OS-based power management
- `dynamic` - Dynamic power optimization
- `static_low` - Minimum power usage
- `static_high` - Maximum performance

## Storage Management

### Physical Drives
```
show /system1/drives
```
Information includes:
- Drive status
- Capacity
- Interface type
- Location

### Array Controllers
```
show /system1/array_controllers
```
Displays:
- Controller status
- Cache status
- Battery backup status
- Logical drives

## Network Services

### SNMP Configuration
```
show /map1/snmp1
```
Settings:
- SNMP versions enabled
- Trap destinations
- Community strings
- Alert types

### Directory Services
```
show /map1/oemhpe_directory1
```
Configure:
- LDAP settings
- Active Directory settings
- Directory groups
- Search contexts

## Security Management

### SSL Certificate Management
```
show /map1/cert1
```
Operations:
- Generate CSR
- Import certificate
- View certificate details

### Security Settings
```
show /map1/security1
```
Configure:
- Authentication failure logging
- Password complexity
- Session timeouts
- Secure boot settings

## License Management
```
show /map1/license1
```
Features:
- View current license
- Install new license
- View licensed features

## Virtual Serial Port
```
start /system1/oemhpe_vsp1
```
Options:
- Connect to Virtual Serial Port
- Use `ESC (` to return to CLI
- Supports text console redirection

## Remote Console
```
start /map1/oemhpe_rc1
```
Features:
- Start remote console session
- Configure remote console settings
- Shared console access

## Event Subscription
```
set /map1/alerts1 destination=<ip> protocol=<type>
```
Supported types:
- SNMP traps
- Email alerts
- Remote syslog
- IPMI Platform Event Traps (PET)

## Performance Monitoring
```
show /system1/performance1
```
Metrics:
- CPU utilization
- Memory usage
- Network throughput
- Storage performance

## User Management Commands
- Create user:
  ```
  create /map1/accounts1 username=<name> password=<pwd> name=<display_name> group=<privileges>
  ```
  Privileges: admin, config, oemHPE_power, oemHPE_rc, oemHPE_vm

- Delete user:
  ```
  delete /map1/accounts1/<username>
  ```

- Modify user privileges:
  ```
  set /map1/accounts1/<username> group=<new_privileges>
  ```

## Network Configuration
- Set network properties:
  ```
  set /map1/enetport1 Speed=100
  set /map1/enetport1/lanendpt1/ipendpt1 IPv4Address=15.255.102.245 SubnetMask=255.255.248.0
  ```

- VLAN configuration:
  ```
  set /map1/vlan1 EnabledState=true VLANID=<id>
  ```

## NIC Auto-Selection Commands
- Enable NIC auto-selection:
  ```
  oemhpe_nicautosel <method> [sbvlan=<0-4094>] [sbport=<1-2>] [sbport_limit=<0|2>] [delay=<90-1800>]
  ```
  Methods: disabled, linkact, rcvdata, dhcp

- Configure NIC failover:
  ```
  oemhpe_nicfailover <method> [delay=<30-3600>]
  ```
  Methods: disabled, linkact, rcvdata, dhcp

## Power Management Commands
Path: `/system1`

### Description
The power command is used to change the power state of the server and is limited to users with the Power and Reset privilege.

### Basic Power Commands
- `power` - Displays the current server power state
- `power on` - Turns the server on
- `power off` - Turns the server off (graceful shutdown)
- `power off hard` - Force the server off using press and hold
- `power reset` - Reset the server

### Power Settings Commands
Path: `/system1/oemhp_power1`

- Get power settings:
  ```
  show /system1/oemhp_power1
  ```

- Set Power Regulator mode:
  ```
  set /system1/oemhp_power1 oemhp_powerreg=<mode>
  ```
  Modes: dynamic, max, min, os

- Set Auto Power On:
  ```
  set /system1/oemhp_power1 oemhp_auto_pwr=<setting>
  ```
  Settings: on, 15, 30, 45, 60, random, restore, off

### Power Monitoring
The following properties are available via `show /system1/oemhp_power1`:
- `oemhp_PresentPower` - Current power consumption
- `oemhp_AvgPower` - Average power consumption
- `oemhp_MaxPower` - Maximum observed power
- `oemhp_MinPower` - Minimum observed power
- `oemhp_powersupplycapacity` - Power supply capacity
- `oemhp_servermaxpower` - Server maximum power capacity
- `oemhp_serverminpower` - Server minimum power capacity

## Boot Settings Management
Path: `/system1/bootconfig1`

### Overview
The boot settings module allows managing HPE iLO server boot configuration via SSH interface. It provides functionality to:
- Get current boot settings
- Set boot mode (UEFI/Legacy)
- Configure boot sources order
- View and modify UEFI boot sources

### Commands

#### Show Current Boot Settings
```
show /system1/bootconfig1
```
This command displays:
- Current boot mode (UEFI/Legacy)
- Pending boot mode (if changed but not applied)
- Available boot sources and their order

#### Show Boot Source Details
```
show /system1/bootconfig1/oemhp_uefibootsource<N>
```
Where `<N>` is a number from 1 to 5. This command shows:
- Boot source description
- Current boot order number
- Other source-specific properties

#### Set Boot Mode
```
set /system1/bootconfig1 oemhp_bootmode=<mode>
```
Where `<mode>` can be:
- UEFI
- Legacy

Note: Changes to boot mode may require a system restart to take effect. The pending boot mode will show the mode that will be active after restart.

#### Set Boot Source Order
```
set /system1/bootconfig1/oemhp_uefibootsource<N> bootorder=<order>
```
Where:
- `<N>` is the source number (1-5)
- `<order>` is the desired boot order number (1 being first)

Example:
```
set /system1/bootconfig1/oemhp_uefibootsource1 bootorder=1
```
This sets the first boot source to be the primary boot device.

#### Set One-Time Boot Source
The ONETIMEBOOT command is used to view or alter the server One-Time Boot setting. When set, this boot source will be used only for the next server boot, after which it will be automatically cleared.

**Usage:**
```
ONETIMEBOOT [source]
```
Where `source` can be:
- `none` - Disable one-time boot (use normal boot order)
- `usb` - Boot from USB device
- `ip` - Boot to Intelligent Provisioning
- `smartstartLX` - Boot to IP Smart Start Linux PE
- `netdev1` - Boot from Network Device 1

**Notes:**
- The setting is automatically cleared after the next system boot
- If no source is specified, the command displays the current setting
- The command requires Power and Reset privileges
- Invalid options will result in an "INVALID OPTION" error

**Example Output:**
```
hpiLO-> onetimeboot
One-Time Boot: No One-Time Boot

hpiLO-> onetimeboot netdev1
status=0
status_tag=COMMAND COMPLETED
One-Time Boot: Network Device 1
```

### Common Boot Sources
Boot sources may include:
- Generic USB Boot
- Network adapters (PXE IPv4/IPv6)
- Hard drives
- CD/DVD drives
- Embedded network adapters

Note: Available boot sources may vary depending on server hardware configuration. The exact names and number of boot sources will depend on the server's hardware.

## HPE SSO Settings
- Set SSO trust level:
  ```
  set /map1/oemHPE_ssocfg1 oemHPE_ssotrust=<level>
  ```
  Levels: disabled, all, name, certificate

- Configure user roles:
  ```
  set /map1/oemHPE_ssocfg1 oemHPE_ssouser=<privileges>
  set /map1/oemHPE_ssocfg1 oemHPE_ssooperator=<privileges>
  set /map1/oemHPE_ssocfg1 oemHPE_ssoadministrator=<privileges>
  ```

## Additional Commands
- Test network connectivity:
  ```
  oemhpe_ping <ip_address>
  ```

- Clear REST API state:
  ```
  oemhpe_clearRESTAPIstate
  ```

- Configure IPv6 settings:
  ```
  oemhpe_ip6 <object> <command> [args] [dev n]
  ```
  Objects: addr, route, gateway, dns, options

- LED control:
  ```
  show /system1/led1   # Show status
  start /system1/led1  # Turn on
  stop /system1/led1   # Turn off
  ```

- Virtual Serial Port:
  ```
  start /system1/oemHPE_vsp1  # Start session
  ```
  Use ESC ( to return to CLI

- System properties:
  ```
  show /system1              # Show system info
  show /system1/cpu1        # Show CPU info
  show /system1/memory1     # Show memory info
  show /system1/firmware1   # Show firmware info
  ```

Virtual Media Management
--------------------------

Commands for managing virtual media devices via iLO SSH interface:

### Basic VM Commands
```
vm <device> insert <path>    # Insert/mount an image
vm <device> eject            # Eject/unmount an image  
vm device get               # Get virtual media status
vm <device> set <options>   # Set virtual media options
```

Where:
- `<device>` is either `floppy` or `cdrom` 
- `<path>` is the URL to the media image
- `<options>` include:
  - `write_protect` or `write_allow` (floppy only)
  - `connect` or `disconnect`
  - `boot_always`, `boot_once`, or `no_boot` (CD only on UEFI systems)

### Equivalent CLP Commands
Show Virtual Media Status:
```
show /map1/oemhp_vm1/<device>
```
Where `<device>` is:
- `cddr` - CD/DVD drive
- `floppydr` - Floppy drive

Mount Virtual Media:
```
set /map1/oemhp_vm1/<device> oemhp_image=<url>
```

Unmount Virtual Media:
```
set /map1/oemhp_vm1/<device> oemhp_image=none
```

Set Device Options:
```
set /map1/oemhp_vm1/<device> <property>=<value>
```
Properties:
- `oemhp_connect` - Connect/disconnect device (yes/no)
- `oemhp_boot` - Boot options (boot_always/boot_once/no_boot)
- `oemhp_wp` - Write protect for floppy (yes/no)

Example Output:
```
hpiLO-> vm device get
status=0
status_tag=COMMAND COMPLETED
/map1/oemhp_vm1/cddr
  Targets
  Properties
    oemhp_image=http://server/image.iso
    oemhp_connect=yes
    oemhp_boot=boot_once
  Verbs
    cd version exit show set
```
 
## HARD_DRIVE_ZONE Commands
Path: `/system1/hard_drive_zone1`

### Overview
The HARD_DRIVE_ZONE commands are used to manage drive bay mapping assignments for supported server configurations. These commands must be within a HARD_DRIVE_ZONE block of a LOGIN command block.

### Command Structure
```xml
<HARD_DRIVE_ZONE MODE="read|write">
  <!-- commands here -->
</HARD_DRIVE_ZONE>
```

### Available Commands

#### READ_BACKPLANE_INFO
Retrieves current backplane information including:
- Host port to node mappings
- Number of available host ports
- Available drive bays on backplane

**Usage:**
```xml
<HARD_DRIVE_ZONE MODE="read">
  <READ_BACKPLANE_INFO/>
</HARD_DRIVE_ZONE>
```

#### READ_ZONE_TABLE
Reads current host port to drive bay mapping table.

**Usage:**
```xml
<HARD_DRIVE_ZONE MODE="read">
  <READ_ZONE_TABLE/>
</HARD_DRIVE_ZONE>
```

Returns:
- Complete mapping table
- HOST_PORT assignments for bays
- UNASSIGNED bays

#### WRITE_ZONE_TABLE
Changes host port to drive bay mapping assignments.

**Requirements:**
- Write mode
- Administrative privileges
- System reboot required for activation

**Usage:**
```xml
<HARD_DRIVE_ZONE MODE="write">
  <WRITE_ZONE_TABLE>
    <TYPE_ID value="SEP_config_type"/>
    <SEP_NODE_ID value="node_id"/>
    <HOST_PORT value="port_number">
      <BAY value="bay_number"/>
      <!-- Additional BAY entries -->
    </HOST_PORT>
    <!-- Additional HOST_PORT blocks -->
  </WRITE_ZONE_TABLE>
</HARD_DRIVE_ZONE>
```

Parameters:
- TYPE_ID: SEP configuration type
- SEP_NODE_ID: Node ID containing SEP
- HOST_PORT: Host port for bay assignments
- BAY: Drive bay numbers to assign

#### ZONE_FACTORY_DEFAULTS
Resets drive bay mapping to factory defaults.

**Requirements:**
- Write mode
- Administrative privileges
- System reboot required for activation

**Usage:**
```xml
<HARD_DRIVE_ZONE MODE="write">
  <ZONE_FACTORY_DEFAULTS>
    <TYPE_ID value="SEP_config_type"/>
    <SEP_NODE_ID value="node_id"/>
  </ZONE_FACTORY_DEFAULTS>
</HARD_DRIVE_ZONE>
```

### Runtime Errors
Common errors for all commands:
- Insufficient privileges
- Invalid MODE value
- Command not supported on system
- Invalid parameters or values
- System in invalid state for operation

## RAID RIBCL Commands Update

### Enhanced Storage Information Commands

#### GET_EMBEDDED_HEALTH
Now includes extended storage information parsing:
- Detailed controller capabilities detection
- Physical drive enclosure information
- Drive bay mapping and status

**Example Response:**
```xml
<GET_EMBEDDED_HEALTH_DATA>
  <STORAGE>
    <CONTROLLER>
      <LABEL VALUE="Smart HBA H240ar"/>
      <STATUS VALUE="OK"/>
      <DRIVE_ENCLOSURE>
        <LABEL VALUE="Port 1I Box 1"/>
        <STATUS VALUE="OK"/>
        <DRIVE_BAY VALUE="04"/>
      </DRIVE_ENCLOSURE>
    </CONTROLLER>
  </STORAGE>
</GET_EMBEDDED_HEALTH_DATA>
```

#### READ_BACKPLANE_INFO
New command support for retrieving detailed backplane information:
- SEP configuration details
- Host port mapping
- Bay configuration

**Example Response:**
```xml
<READ_BACKPLANE_INFO>
  <TYPE_ID VALUE="1"/>
  <SEP_NODE_ID VALUE="0x500143801234567"/>
  <BACKPLANE_NAME VALUE="SAS Expander Card"/>
  <BAY_CNT VALUE="8"/>
  <HOST_PORT VALUE="1">
    <NODE_NUM VALUE="1"/>
    <SLOT_NUM VALUE="0"/>
  </HOST_PORT>
</READ_BACKPLANE_INFO>
```

#### READ_ZONE_TABLE
New command support for zone table information:
- Drive bay assignments
- Host port mapping
- Zone configuration

**Example Response:**
```xml
<READ_ZONE_TABLE>
  <TYPE_ID VALUE="1"/>
  <SEP_NODE_ID VALUE="0x500143801234567"/>
  <HOST_PORT VALUE="1">
    <BAY VALUE="1"/>
    <BAY VALUE="2"/>
  </HOST_PORT>
</READ_ZONE_TABLE>
```

### Command Support Notes
1. Controller capability detection:
   - Automatically checks supported commands
   - Skips unsupported operations
   - Provides informative messages about command availability

2. Error handling improvements:
   - Better XML parsing error detection
   - Detailed error messages for unsupported operations
   - Status checks for each command response

 
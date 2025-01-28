# Roadmap

## Boot Settings Module Status

### Completed Features
- Basic Boot Operations:
  - ✓ Get current boot settings
  - ✓ Set boot mode (UEFI/Legacy)
  - ✓ Configure boot sources order
  - ✓ Handle pending boot mode changes
  - ✓ Error handling and validation
  - ✓ Integration tests
  - ✓ Documentation
- Advanced Boot Operations:
  - ✓ One-time boot source selection
  - ✓ Set temporary boot source (usb, ip, smartstartLX, netdev1)
  - ✓ Reset after single use
  - ✓ Support for all available boot sources

### Future Features (Not Planned)
- Advanced Boot Configuration:
  - Boot source enablement/disablement
  - Custom boot order for specific events
  - Boot source aliases management

## Power Management Module Status

### Completed Features
- Basic Power Operations:
  - ✓ Power on/off commands
  - ✓ Force power off
  - ✓ Server reset
  - ✓ Cold boot
  - ✓ Get power state
  - ✓ Error handling and timeouts
  - ✓ Integration tests
  - ✓ Documentation
  - ✓ Power Regulator configuration (dynamic/max/min/os)
  - ✓ Auto Power On scheduling (on/delay/random/restore)

### Future Features (Not Planned)
- Power monitoring:
  - Present power consumption
  - Average power (24h)
  - Maximum power (24h)
  - Minimum power (24h)
- Power capping:
  - Set power cap in watts
  - Warning thresholds
  - Duration settings

## User Management Module Status

### Completed Features
- Basic User Operations:
  - ✓ Create user accounts
  - ✓ Delete user accounts
  - ✓ Set user privileges
  - ✓ User existence verification
  - ✓ Privilege validation and mapping
  - ✓ Error handling
  - ✓ Integration tests
  - ✓ Documentation

### In Progress
- User Management Enhancements:
  - Password policy enforcement:
    - Minimum length validation
    - Password complexity rules
    - Password expiration
    - Password history

### Future Features (Not Planned)
- Advanced User Management:
  - SSH key management
  - Directory integration (LDAP/AD)
  - Session management
  - Login restrictions
  - Account lockout policies
  - Multi-factor authentication support

## 1. Research and Command Analysis
### Goals:
- Gather all available SSH/CLI commands for HPE iLO.
- Identify which commands are essential for module functionality.
### Steps:
- Connect to an HPE iLO instance via SSH and list all supported commands.
- Test each command to validate:
    - Syntax and input parameters.
    - Expected outputs.
    - Error scenarios.
- Categorize commands into functional areas:
    - Power management.
    - Network configuration.
    - User management.
    - Logs and diagnostics.
    - Virtual media management.
- Document tested commands for reference during implementation.

## 2. Define the Module Architecture
### Goals:
- Create a structured design for the module and submodules.
### Steps:
- Plan functional submodules, such as:
    - ilo_power: Handles power commands (e.g., reset, shutdown).
    - ilo_user: Manages user accounts and privileges.
    - ilo_network: Configures IP, DNS, and VLAN settings.
    - ilo_logs: Fetches and clears system logs.-
    - ilo_virtual_media: Manages virtual devices like ISO mounts.
- Define input arguments for each submodule, including:
    - Host credentials (IP, username, password).
    - Command-specific parameters (e.g., power state, network settings).
- Design a common error-handling mechanism to process SSH responses.
- Plan output formats to align with Ansible's result structure.

## 3. Build a Prototype
### Goals:
- Create a basic module that can execute raw SSH commands.
### Steps:
- Develop a Python-based Ansible module using the raw module.
- Implement core functionalities:
    - Connect to iLO via SSH.
    - Execute simple commands (e.g., retrieve hardware status).
- Test the prototype on a live HPE iLO environment.

## 4. Implement Core Functionalities
### Goals:
- Add essential features to the module.
### Steps:
- Implement commands for:
    - Power management: reset, shutdown, power on/off.
    - Basic hardware status: Fetch server health and power state.
- Ensure each function has:
    - Valid input checks.
    - Proper error handling for invalid commands or SSH failures.
- Test functions individually to confirm expected behavior.

## 5. Expand Functionality
### Goals:
- Add advanced iLO features to the module.
### Steps:
- Develop submodules for:
    - Network Configuration:
    - Manage IP, DNS, subnet, and gateway settings.
    - Enable/disable NIC auto-selection and failover.
    - User Management:
        - Create, edit, delete users.
        - Configure user privileges and manage SSH keys.
    - Logs and Diagnostics:
        - Retrieve logs (IML, AHS) and clear them.
    - Virtual Media:
        - Mount/unmount ISO images.
        - Configure virtual keyboards/mice.
    - Firmware Updates:
        - Upload and install firmware files via SCP or HTTP.
    - Security:
        - Configure SSL certificates and security banners.
- Add support for structured inputs and outputs:
    - Map CLI responses to JSON outputs for Ansible.
- Include retry mechanisms for commands prone to transient errors.

## 6. Test and Debug
### Goals:
- Validate module functionality across different use cases and environments.
### Steps:
- Write unit tests for each function and submodule.
- Perform integration tests with:
    - Multiple HPE iLO versions.
    - Various hardware configurations.
- Debug edge cases such as:
    - Network timeouts.
    - Invalid inputs.
    - Permissions errors.

## 7. Optimize and Refactor
### Goals:
- Ensure the module is efficient and maintainable.
### Steps:
- Refactor redundant code into reusable functions or classes.
- Optimize SSH execution to minimize latency.
- Implement modular logging for debugging and auditing.

## 8. Documentation and Packaging
### Goals:
- Prepare the module for distribution and developer use.
### Steps:
- Document:
    - Submodules and their arguments.
    - Input/output examples.
    - Error handling mechanisms.
- Package the module for use in an Ansible collection.
- Create developer-focused guides for extending the module.

## 9. Release and Maintenance
### Goals:
- Deliver a stable version and ensure future updates.
### Steps:
- Publish the module to a version control system (e.g., GitHub).
- Add CI/CD pipelines for automated testing and linting.
- Periodically update the module to support new iLO firmware versions.

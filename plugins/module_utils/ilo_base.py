#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import paramiko
import time

class IloBaseModule:
    """
    Logging using ansible debug
    """
    def __init__(self, module):
        self.module = module
        self.ssh = None
        self.debug_enabled = True

    def log(self, message):
        """
        Logging using ansible debug
        """
        if self.debug_enabled:
            self.module.debug(message)

    def connect(self):
        """
        Connect to iLO via SSH
        """
        try:
            # enable support for old algorithms
            paramiko.Transport._preferred_kex = [
                'diffie-hellman-group14-sha1',
                'diffie-hellman-group1-sha1'
            ]
            paramiko.Transport._preferred_keys = [
                'ssh-rsa',
                'ssh-dss'
            ]
            
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # connect with support for old algorithms
            self.ssh.connect(
                self.module.params['hostname'],
                username=self.module.params['username'],
                password=self.module.params['password'],
                allow_agent=False,
                look_for_keys=False,
                disabled_algorithms={
                    'keys': ['rsa-sha2-256', 'rsa-sha2-512'],
                    'kex': ['diffie-hellman-group-exchange-sha256', 'diffie-hellman-group-exchange-sha1']
                }
            )
            
            self.log("Successfully connected to iLO")
            return True
        except Exception as e:
            self.module.fail_json(msg=f"Failed to connect to iLO: {str(e)}")
            return False

    def execute_command(self, command, timeout=None):
        """
        Execute command via SSH
        """
        if not self.ssh:
            if not self.connect():
                return False, "", "Failed to connect"

        try:
            self.log(f"Executing command: {command}")
            if timeout:
                self.ssh.get_transport().set_keepalive(timeout)
            stdin, stdout, stderr = self.ssh.exec_command(command)
            stdout_str = stdout.read().decode('utf-8', errors='ignore')
            stderr_str = stderr.read().decode('utf-8', errors='ignore')
            exit_status = stdout.channel.recv_exit_status()
            
            self.log(f"Command output: {stdout_str}")
            if stderr_str:
                self.log(f"Command error: {stderr_str}")
            self.log(f"Exit status: {exit_status}")
            
            return exit_status == 0, stdout_str, stderr_str
        except Exception as e:
            self.log(f"Command execution failed: {str(e)}")
            return False, "", str(e)

    def disconnect(self):
        """
        Disconnect from iLO
        """
        if self.ssh:
            self.ssh.close()
            self.ssh = None
            self.log("Disconnected from iLO")

    def execute_command_old(self, command, timeout=30):
        """
        Execute command via SSH without using Python on the remote side
        """
        if not self.ssh:
            if not self.connect():
                return False, None, None
        
        self.log("\n" + "=" * 80)
        self.log("COMMAND:")
        self.log("-" * 40)
        self.log(command)
        self.log("-" * 40)
        
        try:
            # Open SSH session
            chan = self.ssh.get_transport().open_session()
            chan.settimeout(timeout)
            
            # Execute command
            chan.exec_command(command)
            
            # Read output data
            stdout = ""
            stderr = ""
            
            # Read stdout and stderr
            while True:
                if chan.recv_ready():
                    data = chan.recv(4096).decode('utf-8', errors='ignore')
                    stdout += data
                if chan.recv_stderr_ready():
                    data = chan.recv_stderr(4096).decode('utf-8', errors='ignore')
                    stderr += data
                if chan.exit_status_ready():
                    break
                time.sleep(0.1)
            
            # Get exit status
            exit_status = chan.recv_exit_status()
            
            # Output result
            self.log("\nRESULT:")
            self.log("-" * 40)
            self.log(f"Exit Status: {exit_status}")
            if stdout:
                self.log("\nSTDOUT:")
                self.log("-" * 40)
                self.log(stdout)
            if stderr:
                self.log("\nSTDERR:")
                self.log("-" * 40)
                self.log(stderr)
            self.log("=" * 80 + "\n")
            
            chan.close()
            
            # Save output to result
            if hasattr(self.module, '_result'):
                if 'stdout' not in self.module._result:
                    self.module._result['stdout'] = []
                if 'stderr' not in self.module._result:
                    self.module._result['stderr'] = []
                self.module._result['stdout'].append({
                    'command': command,
                    'output': stdout,
                    'exit_status': exit_status
                })
                if stderr:
                    self.module._result['stderr'].append({
                        'command': command,
                        'output': stderr
                    })
            
            return True, stdout, stderr
            
        except Exception as e:
            self.log(f"ERROR executing command: {str(e)}")
            self.module.fail_json(msg=f"Failed to execute command: {str(e)}")
            return False, None, None 
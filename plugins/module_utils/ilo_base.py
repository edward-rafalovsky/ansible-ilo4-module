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
        self.hostname = module.params['hostname']
        self.username = module.params['username']
        self.password = module.params['password']
        self.ssh = None

    def log(self, message):
        """
        Logging using ansible debug
        """
        if self.module._debug:
            self.module.debug(message)

    def connect(self):
        """
        Connect to iLO via SSH
        """
        try:
            # Configure parameters for old iLO systems
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect with configured parameters
            ssh.connect(
                self.hostname,
                username=self.username,
                password=self.password,
                allow_agent=False,
                look_for_keys=False,
                disabled_algorithms={'kex': ['diffie-hellman-group-exchange-sha1']},
                timeout=30
            )
            
            # Test connection
            stdin, stdout, stderr = ssh.exec_command('version')
            if stdout.channel.recv_exit_status() != 0:
                self.module.fail_json(msg=f"Failed to connect to iLO: {stderr.read().decode()}")
            
            self.ssh = ssh
            return True
            
        except Exception as e:
            self.module.fail_json(msg=f"Failed to connect to iLO: {str(e)}")
            return False

    def execute_command(self, command, timeout=30):
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

    def disconnect(self):
        if self.ssh:
            self.ssh.close() 
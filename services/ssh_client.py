import subprocess
import time


class SSHClient:

    def __init__(self, host, username, password, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port

    def execute(self, command, wait_time=8):

        ssh_command = [
            "sshpass",
            "-p", self.password,
            "ssh",
            "-tt",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "KexAlgorithms=diffie-hellman-group1-sha1",
            "-o", "HostKeyAlgorithms=+ssh-rsa",
            "-o", "Ciphers=+aes128-cbc,3des-cbc",
            f"{self.username}@{self.host}"
        ]

        try:
            process = subprocess.Popen(
                ssh_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Matikan paging jika command ini didukung OLT
            process.stdin.write("terminal length 0\n")
            process.stdin.flush()
            time.sleep(1)

            # Kirim command utama
            process.stdin.write(command + "\n")
            process.stdin.flush()
            time.sleep(wait_time)

            # Keluar dari OLT
            process.stdin.write("exit\n")
            process.stdin.flush()
            time.sleep(1)

            # Jawab konfirmasi logout
            process.stdin.write("y\n")
            process.stdin.flush()

            output, error = process.communicate(timeout=10)

            if error and "Connection to" not in error and "Permanently added" not in error:
                print("SSH ERROR:")
                print(error)

            return output

        except subprocess.TimeoutExpired:
            process.kill()
            return "ERROR: SSH Timeout"

        except Exception as e:
            return f"ERROR: {str(e)}"

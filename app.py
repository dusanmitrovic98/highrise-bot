import os
import platform
import subprocess

# Determine the current directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Detect OS
system = platform.system().lower()

if 'windows' in system:
    script = os.path.join(script_dir, 'start-with-monitor.bat')
    cmd = [script]
    shell = True
elif 'linux' in system or 'darwin' in system:
    script = os.path.join(script_dir, 'start-with-monitor.sh')
    cmd = ['bash', script]
    shell = False
else:
    raise RuntimeError(f"Unsupported OS: {system}")

print(f"Running: {cmd}")
subprocess.run(cmd, shell=shell)

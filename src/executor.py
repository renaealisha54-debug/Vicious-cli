import subprocess
import sys
from logger import logger

def execute_shell_command(command: str) -> tuple[int, str, str]:
    """
    Executes a shell command safely, streams live output, 
    and captures stdout/stderr.
    """
    logger.info(f"Executing shell command: {command}")
    print(f"\n[Running]: {command}\n" + "-" * 40)

    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        stdout_lines = []
        stderr_lines = []

        # Read output line-by-line in real-time
        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                sys.stdout.write(line)
                stdout_lines.append(line)

        process.wait()

        if process.stderr:
            stderr_lines = process.stderr.readlines()
            for line in stderr_lines:
                sys.stderr.write(line)

        stdout_str = "".join(stdout_lines)
        stderr_str = "".join(stderr_lines)

        logger.info(f"Command exited with code {process.returncode}")
        return process.returncode, stdout_str, stderr_str

    except Exception as e:
        logger.error(f"Failed to execute command '{command}': {e}")
        return 1, "", str(e)

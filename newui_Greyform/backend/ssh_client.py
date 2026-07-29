# backend/ssh_client.py
# Shared SSH connection to the robot controller (Linux Desktop PC).
# Replaces the old `sshpass -p ... ssh ...` subprocess calls, which
# only worked because the backend used to run on Linux. paramiko is
# pure Python, so this works identically on Windows or Linux.

import os
import time
import threading
from typing import List, Optional, Tuple

import paramiko

# ------------------------------------------------------------------
# Connection settings
# ------------------------------------------------------------------
# TODO: consider moving these into environment variables
# (e.g. os.getenv("ROBOT_SSH_HOST", "192.168.1.5")) before this goes
# to other operator PCs, so the credentials aren't hardcoded.
SSH_HOST = os.getenv("ROBOT_SSH_HOST", "192.168.1.5")
SSH_USER = os.getenv("ROBOT_SSH_USER", "winsys")
SSH_PASSWORD = os.getenv("ROBOT_SSH_PASSWORD", "winsys")
SSH_CONNECT_TIMEOUT = 10

_client: Optional[paramiko.SSHClient] = None
_lock = threading.Lock()


def get_client() -> paramiko.SSHClient:
    """
    Return a live, connected SSHClient, reconnecting if needed.
    Reused across requests so we don't re-authenticate every call.
    """
    global _client
    with _lock:
        if _client is not None:
            transport = _client.get_transport()
            if transport is not None and transport.is_active():
                return _client
            try:
                _client.close()
            except Exception:
                pass
            _client = None

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            SSH_HOST,
            username=SSH_USER,
            password=SSH_PASSWORD,
            timeout=SSH_CONNECT_TIMEOUT,
        )
        _client = client
        return _client


def run_command(command: str, timeout: int = 60) -> Tuple[List[str], int]:
    """
    Run a command on the remote host and block until it finishes.
    Equivalent to the old:
        sshpass -p ... ssh user@host "command"
    Returns (lines, exit_code).
    """
    client = get_client()
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    output = stdout.read().decode(errors="replace")
    exit_code = stdout.channel.recv_exit_status()
    lines = [line for line in output.splitlines()]
    return lines, exit_code


class RemoteProcess:
    """
    Wraps a paramiko Channel so it behaves enough like a
    subprocess.Popen object (`.stdout` iterable, `.wait()`, `.poll()`,
    `.kill()`) that the existing reader_thread logic barely has to change.
    """

    def __init__(self, channel: paramiko.Channel):
        self.channel = channel
        # text-mode, line-buffered file-like object over the channel
        self.stdout = channel.makefile("r")

    def poll(self) -> Optional[int]:
        if self.channel.exit_status_ready():
            return self.channel.recv_exit_status()
        return None

    def wait(self, timeout: Optional[float] = None) -> int:
        start = time.time()
        while not self.channel.exit_status_ready():
            if timeout is not None and (time.time() - start) > timeout:
                raise TimeoutError("Remote command timed out")
            time.sleep(0.1)
        return self.channel.recv_exit_status()

    def kill(self):
        """
        Best-effort stop of the remote command. Sends Ctrl-C down the
        channel (works for well-behaved foreground scripts reading a
        pty), then closes the channel. There is no direct equivalent of
        killpg over SSH, so a stubborn remote process may need its own
        pkill command if this isn't sufficient.
        """
        try:
            self.channel.send("\x03")
        except Exception:
            pass
        try:
            self.channel.close()
        except Exception:
            pass


def read_remote_file(remote_path: str) -> bytes:
    """
    Download a file's raw bytes from the remote host over SFTP (reuses
    the same authenticated connection as run_command/open_stream).
    Used to read output.xlsx directly, so stage-completion logic lives
    in code we control rather than depending on a remote script.
    """
    client = get_client()
    sftp = client.open_sftp()
    try:
        with sftp.open(remote_path, "rb") as f:
            return f.read()
    finally:
        sftp.close()


def open_stream(command: str) -> RemoteProcess:
    """
    Start a long-running remote command and return a RemoteProcess for
    live, line-by-line reading. Used for the marking script, where we
    need to react to output as it streams in (point counters, errors),
    not just wait for it to finish.
    """
    client = get_client()
    transport = client.get_transport()
    channel = transport.open_session()
    channel.get_pty()  # helps remote scripts flush output line-by-line
    channel.exec_command(command)
    return RemoteProcess(channel)

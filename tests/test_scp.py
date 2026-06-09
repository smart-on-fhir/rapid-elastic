import unittest
from pathlib import Path
import paramiko
from scp import SCPClient
from rapid_elastic import config

def connect() -> paramiko.SSHClient:
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=config.SCP_HOST,
                port=config.SCP_PORT,
                username=config.SCP_USER,
                password='')
    return ssh

def file_exists(remote_path: Path,
                client: paramiko.SSHClient):
    sftp = client.open_sftp()
    try:
        return sftp.stat(str(remote_path))
    except FileNotFoundError:
        return False

def move_to_server(local_path: Path,
                   remote_path: Path,
                   client: paramiko.SSHClient,
                   delete_local=True):
    """
    :param local_path: Path to local filesystem
    :param remote_path: Path on remote server
    :param client: SSHClient client connection
    :param delete_local: delete local copy
    :return: None
    """
    if not local_path.exists():
        raise FileNotFoundError(f'{local_path} does not exist')

    with SCPClient(client.get_transport()) as handle:
        handle.put(str(local_path), str(remote_path))
        if file_exists(remote_path, client):
            if delete_local:
                local_path.unlink()


class TestSCP(unittest.TestCase):
    @unittest.skip
    def test_config(self):
        self.assertIsNotNone(config.SCP_HOST)
        self.assertIsNotNone(config.SCP_PORT)
        self.assertIsNotNone(config.SCP_DIR)
        self.assertIsNotNone(config.SCP_USER)

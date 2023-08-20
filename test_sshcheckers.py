import time
import subprocess
import pytest
import paramiko
import yaml
from sshcheckers import ssh_checkout, ssh_checkout_negative, upload_files

@pytest.fixture(scope="function")
def update_stat(request):
    with open('stat.txt', 'a') as f:
        start_time = time.time()
        yield
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        with open('config.yaml') as config_file:
            config_data = yaml.safe_load(config_file)
            
        num_files = len(config_data.get("local_path"))
        file_size = config_data.get("file_size")
        
        load_avg = ""
        with open('/proc/loadavg') as loadavg_file:
            load_avg = loadavg_file.read()
        
        f.write(f"{elapsed_time}, {num_files}, {file_size}, {load_avg}\n")

with open('config.yaml') as f:
    data = yaml.safe_load(f)

class TestPositive:
    @pytest.mark.usefixtures("update_stat")
    def test_upload_files(self):
        upload_files(data.get("ip"), data.get("user"), data.get("passwd"),
                     data.get("local_path"), data.get("remote_path"))
        assert True
    
    @pytest.mark.usefixtures("update_stat")
    def test_ssh_checkout(self):
        res = []
        cmd = f"echo {data.get('passwd')} | sudo -S dpkg -s p7zip-full"
        res.append(ssh_checkout(data.get("ip"), data.get("user"), data.get("passwd"), cmd,
                                "Status: install ok installed"))
        assert all(res)

    @pytest.mark.usefixtures("update_stat")
    def test_ssh_checkout_negative(self):
        res = []
        cmd = f"echo {data.get('passwd')} | sudo -S dpkg -r {data.get('remote_path')}"
        res.append(ssh_checkout_negative(data.get("ip"), data.get("user"), data.get("passwd"), cmd,
                                          "Удаляется"))
        assert all(res)

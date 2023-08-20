import paramiko
import time
import subprocess
import pytest
import yaml

@pytest.fixture(scope="function")
def update_stat(request):
    with open('stat.txt', 'a') as f:
        start_time = time.time()
        yield
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Читаем данные из конфига
        with open('config.yaml') as config_file:
            config_data = yaml.safe_load(config_file)
            
        # Получаем количество файлов из конфига
        num_files = len(config_data.get("local_path"))
        
        # Получаем размер файла из конфига
        file_size = config_data.get("file_size")
        
        # Читаем статистику загрузки процессора из /proc/loadavg
        load_avg = ""
        with open('/proc/loadavg') as loadavg_file:
            load_avg = loadavg_file.read()
        
        f.write(f"{elapsed_time}, {num_files}, {file_size}, {load_avg}\n")

with open('config.yaml') as f:
    data = yaml.safe_load(f)

class TestPositive:
    @pytest.mark.usefixtures("update_stat")
    def test_step2(self):
        res = []
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(data.get("ip"), username=data.get("user"), password=data.get("passwd"))
        
        # Выполняем команду удаления пакета
        stdin, stdout, stderr = ssh_client.exec_command(f"echo {data.get('passwd')} | sudo -S dpkg -r {data.get('remote_path')}")
        exit_code = stdout.channel.recv_exit_status()
        out = (stdout.read() + stderr.read()).decode("utf-8")
        res.append(data.get("text") in out and exit_code == 0)
        
        # Выполняем команду проверки установки пакета
        stdin, stdout, stderr = ssh_client.exec_command(f"echo {data.get('passwd')} | sudo -S dpkg -s p7zip-full")
        exit_code = stdout.channel.recv_exit_status()
        out = (stdout.read() + stderr.read()).decode("utf-8")
        res.append(data.get("text2") in out and exit_code == 0)
        
        ssh_client.close()
        
        assert all(res)

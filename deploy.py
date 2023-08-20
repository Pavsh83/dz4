from sshcheckers import ssh_checkout, upload_files
import yaml

def deploy():
    with open('config.yaml') as f:
        data = yaml.safe_load(f)

    res = []

    # Выгружаем файлы на удаленный сервер
    upload_files(data.get("ip"), data.get("user"), data.get("passwd"), data.get("local_path"), data.get("remote_path"))

    # Удаляем пакет
    remove_package_cmd = f"echo {data.get('passwd')} | sudo -S dpkg -r {data.get('remote_path')}"
    res.append(ssh_checkout(data.get("ip"), data.get("user"), data.get("passwd"), remove_package_cmd, "Удаляется"))

    # Проверяем статус удаленного пакета
    check_package_cmd = f"echo {data.get('passwd')} | sudo -S dpkg -s p7zip-full"
    res.append(ssh_checkout(data.get("ip"), data.get("user"), data.get("passwd"), check_package_cmd, "Status: deinstall ok"))

    # Дополнительно, добавляем параметр типа архива в команды 7z
    archive_type = data.get("archive_type", "zip")
    archive_cmd = f"7z a -t{archive_type} {data.get('folder_out')}/arh1"
    res.append(ssh_checkout(data.get("ip"), data.get("user"), data.get("passwd"), archive_cmd, "Everything is Ok"))

    return all(res)

if __name__ == "__main__":
    if deploy():
        print("Deployment successful.")
    else:
        print("Deployment failed.")

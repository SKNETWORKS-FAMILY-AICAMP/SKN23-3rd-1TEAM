import os
import paramiko
import json
from utils.config import SSH_KEY_PATH


def ssh_command(ip, cmd):
    """지정된 원격 IP로 SSH 접속하여 명령을 실행하고 결과를 반환"""
    if not SSH_KEY_PATH or not os.path.exists(SSH_KEY_PATH):
        return None, f"SSH Key Not Found at: {SSH_KEY_PATH}"

    key = paramiko.RSAKey.from_private_key_file(SSH_KEY_PATH)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 타임아웃을 적절히 설정 (서비스 실행 등은 더 길 수 있음)
        client.connect(hostname=ip, username="ubuntu", pkey=key, timeout=5)
        stdin, stdout, stderr = client.exec_command(cmd)

        out = stdout.read().decode()
        err = stderr.read().decode()
        return out, err
    except Exception as e:
        return None, str(e)
    finally:
        client.close()


def get_system_metrics(ip):
    """현재 원격 서버의 CPU, 메모리, 디스크 사용량을 수집"""
    cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}' && free -m | grep Mem | awk '{print $3/$2 * 100}' && df -h / | tail -1 | awk '{print $5}'"
    out, err = ssh_command(ip, cmd)

    if out:
        lines = out.strip().split("\n")
        try:
            cpu = float(lines[0])
            mem = float(lines[1])
            disk = lines[2].replace("%", "")
            return cpu, mem, disk
        except (IndexError, ValueError):
            return 0, 0, 0
    return 0, 0, 0


def check_process_status(ip, process_name):
    """원격 서버에 특정 프로세스가 실행 중인지 확인 (pgrep 이용)"""
    out, _ = ssh_command(ip, f"pgrep -f {process_name}")
    return bool(out)

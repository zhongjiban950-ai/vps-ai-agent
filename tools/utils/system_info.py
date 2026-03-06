#!/usr/bin/env python3
"""System info and health check tool."""

import subprocess
import json
import os
import platform


def get_system_info():
    info = {
        "hostname": platform.node(),
        "os": platform.platform(),
        "python": platform.python_version(),
        "cpu_count": os.cpu_count(),
    }

    # Memory
    try:
        mem = subprocess.check_output(["free", "-h"], text=True)
        info["memory"] = mem.strip()
    except:
        pass

    # Disk
    try:
        disk = subprocess.check_output(["df", "-h", "/"], text=True)
        info["disk"] = disk.strip()
    except:
        pass

    # Docker
    try:
        docker = subprocess.check_output(["docker", "ps", "--format", "{{.Names}}: {{.Status}}"], text=True)
        info["docker_containers"] = docker.strip()
    except:
        info["docker"] = "not running"

    # VPN
    try:
        wg = subprocess.check_output(["wg", "show"], text=True)
        info["wireguard"] = wg.strip()[:500]
    except:
        info["wireguard"] = "not configured"

    # SSH keys
    ssh_dir = os.path.expanduser("~/.ssh")
    if os.path.exists(ssh_dir):
        info["ssh_keys"] = [f for f in os.listdir(ssh_dir) if f.endswith(".pub")]

    return info


def check_services():
    services = ["wg-quick@wg0", "docker", "nginx", "ssh"]
    results = {}
    for svc in services:
        try:
            out = subprocess.check_output(
                ["systemctl", "is-active", svc], text=True
            ).strip()
            results[svc] = out
        except:
            results[svc] = "inactive"
    return results


if __name__ == "__main__":
    info = get_system_info()
    services = check_services()
    print(json.dumps({"system": info, "services": services}, indent=2, default=str))

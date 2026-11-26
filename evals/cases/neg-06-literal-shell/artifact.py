import os, subprocess

def deploy():
    subprocess.run("docker compose -f docker-compose.prod.yml up -d", shell=True, check=True)

def clear_cache():
    os.system("redis-cli FLUSHALL")

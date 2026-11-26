# app/render.py - a support page and a build helper.
# Four patterns that trip every scanner we have run this file through.

import os
import subprocess
from django.utils.safestring import mark_safe
from flask import Flask, render_template_string

app = Flask(__name__)

# 1. mark_safe on a module constant
COPYRIGHT = mark_safe("<p>&copy; 2026 Acme. All rights reserved.</p>")

# 2. shell=True, but the command is a literal
def clean_build_dir():
    subprocess.run("rm -rf ./build && mkdir ./build", shell=True, check=True)

# 3. os.system, again a literal
def restart_worker():
    os.system("systemctl restart acme-worker")

# 4. render_template_string on a module constant
@app.route("/support")
def support():
    return render_template_string(COPYRIGHT)

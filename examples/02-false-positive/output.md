# Output - example 02

> Input: [`input.py`](input.py) and [`input.js`](input.js) - six patterns that a
> pattern-matching scanner reports as findings. None of them is a vulnerability.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 SECURITY TRIAGE REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

No HIGH or MEDIUM confidence findings identified.

Six patterns were checked. Each is a sink a scanner would flag, and in each case the
value reaching the sink is not attacker-controlled. Detail is in NOTES below.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BLIND SPOTS
  Not visible to me: where `window.__APP_CONFIG__` is populated (a build-time JSON
  injection would make finding 5 real — see the elevation note), whether `COPYRIGHT`
  is ever reassigned at import time, and whether any caller passes user input to
  `clean_build_dir` or `restart_worker` through a wrapper not shown here.
```

```
NOTES (informational only — not actionable findings)

• `mark_safe(COPYRIGHT)` — LOW confidence. `COPYRIGHT` is a module-level constant with no
  interpolation. `mark_safe` on a constant cannot produce injection. This becomes HIGH the
  moment the string gains an f-string with a request value; flag that, not this.
  Elevation trigger: `mark_safe(f"...{request.args[...]}...")`.

• `subprocess.run("rm -rf ./build && mkdir ./build", shell=True)` — LOW confidence.
  `shell=True` with a string literal is a code-quality smell, not a vulnerability: there
  is no variable to inject into. The risk is future maintenance — someone appends
  `+ user_dir` and it becomes command injection silently. Worth a comment, not a finding.
  Elevation trigger: any concatenation or f-string into the command string.

• `os.system("systemctl restart acme-worker")` — LOW confidence. Literal argument, no
  injection surface. Same maintenance risk as above.

• `innerHTML = window.__APP_CONFIG__.supportUrl` — LOW confidence as written.
  `__APP_CONFIG__` is application config, not user input; this is the
  "server config ≠ attacker input" case. It is also not `innerHTML` on a user-controlled
  value.
  Elevation trigger: if `__APP_CONFIG__` is rendered into the page from a request value,
  or if the field is user-editable in an admin panel without output encoding, this becomes
  DOM XSS at HIGH confidence. The pattern to check is how the config is serialised into
  HTML, not the assignment itself.

• `eval('({"beta": true})')` — LOW confidence. A constant expression with no input path.
  It is still worth deleting: `eval` on a literal buys nothing over the object literal, and
  its presence trains reviewers to accept `eval` in the codebase.
  Elevation trigger: any variable inside the `eval` argument.

• `render_template_string(COPYRIGHT)` — LOW confidence. `render_template_string` on a
  trusted constant is not SSTI. The dangerous form is a template built from user input.
  Elevation trigger: `render_template_string(request.args['t'])`.

FIX CHECKLIST (optional — code quality, not security)
  ☐ Replace `eval('({"beta": true})')` with `{ beta: true }`
  ☐ Add a comment above the two `shell=True` / `os.system` literals marking them
    injection-sensitive for future editors
```

## What to notice

This is the output that matters. Six flags, zero findings, and a reason for each one -
including the exact change that would turn each into a real finding.

A scanner produces six tickets here and burns an hour of review. That hour is the product.

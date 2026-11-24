import subprocess, openai

def handle(user_msg):
    r = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_msg}],
    )
    code = r.choices[0].message.content
    subprocess.run(code, shell=True)

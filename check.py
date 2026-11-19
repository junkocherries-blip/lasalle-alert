import os, re, smtplib, subprocess, time, urllib.request
from email.message import EmailMessage

URL = "https://mirai-compass.net/usr/lasallej/event/evtIndex.jsf"
IGNORE = []  # テスト用。本番は ["12/16"] に変更

def find_open():
    try:
        html = urllib.request.urlopen(URL, timeout=20).read().decode("utf-8")
    except Exception:
        return None
    for r in html.split("<tr"):
        if "受付中" in r and not any(k in r for k in IGNORE):
            text = re.sub(r"<[^>]+>", " ", r)
            return re.sub(r"\s+", " ", text).strip()[:150]
    return None

def notify(detail):
    me = os.environ["MAIL_ADDRESS"]
    msg = EmailMessage()
    msg["Subject"] = "【受付中】ラ・サール 見学会に空き・新着があります"
    msg["From"] = msg["To"] = me
    msg.set_content(f"{detail}\n\n今すぐ申込へ：\n{URL}")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(me, os.environ["MAIL_PASSWORD"])
        s.send_message(msg)

for _ in range(8):
    found = find_open()
    if found:
        notify(found)
        subprocess.run(["gh", "workflow", "disable", "check.yml"])
        break
    time.sleep(30)

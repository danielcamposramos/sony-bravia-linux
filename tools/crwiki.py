#!/usr/bin/env python3
"""
crwiki.py — minimal Consumer Rights Wiki client for reviewed, human-authorised edits.

Credentials live in ~/.config/crwiki/ (mode 600): `user` and `password`, from a
Special:BotPasswords grant limited to editing. The password is handed to curl
with --data-urlencode name@file, so it never appears in a command line, shell
history or process listing.

Network goes through curl because this workspace's sandbox permits it and
blocks direct Python sockets.

The wiki's AI usage policy requires the editor to verify the result rather than
paste and walk away, so every write prints a diff of what the wiki actually
holds afterwards.

    crwiki.py whoami
    crwiki.py get   "Page title"
    crwiki.py diff  "Page title" new.txt
    crwiki.py edit  "Page title" new.txt --summary "..." [--create]
    crwiki.py redirect "From" "To" --summary "..."
"""
import argparse, difflib, json, os, subprocess, sys, tempfile

CFG = os.path.expanduser("~/.config/crwiki")
API = "https://consumerrights.wiki/api.php"
UA = "crwiki.py/1.0 (consumerrights.wiki editing assistant; run by the account owner)"
COOKIES = os.path.join(tempfile.gettempdir(), ".crwiki-cookies")


def curl(args, data=None):
    cmd = ["curl", "-s", "-A", UA, "-b", COOKIES, "-c", COOKIES, "--max-time", "45"]
    for k, v in (data or []):
        cmd += ["--data-urlencode", f"{k}={v}"] if not k.endswith("@") else ["--data-urlencode", f"{k[:-1]}@{v}"]
    cmd.append(API + ("?" + args if args else ""))
    out = subprocess.run(cmd, capture_output=True).stdout.decode("utf-8", "replace")
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        sys.exit("unexpected response: " + out[:300])


def login():
    if os.path.exists(COOKIES):
        os.remove(COOKIES)
    tok = curl("action=query&meta=tokens&type=login&format=json")["query"]["tokens"]["logintoken"]
    user = open(os.path.join(CFG, "user")).read().strip()
    res = curl("", [("action", "login"), ("lgname", user),
                    ("lgpassword@", os.path.join(CFG, "password")),
                    ("lgtoken", tok), ("format", "json")])
    if res.get("login", {}).get("result") != "Success":
        sys.exit("login failed: " + res.get("login", {}).get("reason", json.dumps(res)[:200]))
    return res["login"]["lgusername"]


def csrf():
    return curl("action=query&meta=tokens&format=json")["query"]["tokens"]["csrftoken"]


def page_text(title):
    d = curl("", [("action", "query"), ("prop", "revisions"), ("rvprop", "content"),
                  ("rvslots", "main"), ("titles", title), ("format", "json")])
    p = list(d["query"]["pages"].values())[0]
    return None if "missing" in p else p["revisions"][0]["slots"]["main"]["*"]


def show_diff(old, new, title):
    d = list(difflib.unified_diff((old or "").splitlines(), new.splitlines(),
                                  f"{title} (on wiki)", f"{title} (proposed)", lineterm="", n=2))
    print("\n".join(d) if d else "(identical)")


def do_edit(title, newtext, summary, create, captcha=None):
    old = page_text(title)
    if old is None and not create:
        sys.exit(f"{title!r} does not exist; pass --create")
    if old is not None and create:
        sys.exit(f"{title!r} already exists; refusing --create")
    fields = [("action", "edit"), ("title", title), ("text", newtext),
              ("summary", summary), ("token", csrf()), ("format", "json"),
              ("createonly" if create else "nocreate", "1")]
    if captcha:
        # The wiki asks a human to answer a simple sum before a new account may
        # add external links. The answer is supplied by the account's owner and
        # passed through here; it is never solved by this script.
        cid, word = captcha
        fields += [("captchaid", cid), ("captchaword", word)]
    res = curl("", fields)
    if "error" in res:
        sys.exit("edit failed: " + json.dumps(res["error"])[:400])
    if res.get("edit", {}).get("result") != "Success":
        cap = res.get("edit", {}).get("captcha")
        if cap:
            sys.exit(f"the wiki asks a captcha before saving.\n  question: {cap.get('question')}\n"
                     f"  id: {cap.get('id')}\n"
                     f"  rerun with: --captcha-id {cap.get('id')} --captcha-word <the answer, from you>")
        sys.exit("edit not accepted by the wiki: " + json.dumps(res)[:800])
    print(f"saved: {title} (revision {res['edit'].get('newrevid')})")
    print("--- verification: proposed vs what the wiki now holds ---")
    live = page_text(title)
    if live is None:
        print("WARNING: the wiki reports no such page after saving; nothing was written.")
    else:
        show_diff(newtext, live, title)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("whoami")
    g = sub.add_parser("get"); g.add_argument("title")
    df = sub.add_parser("diff"); df.add_argument("title"); df.add_argument("file")
    e = sub.add_parser("edit"); e.add_argument("title"); e.add_argument("file")
    e.add_argument("--summary", required=True); e.add_argument("--create", action="store_true")
    e.add_argument("--captcha-id"); e.add_argument("--captcha-word")
    r = sub.add_parser("redirect"); r.add_argument("frm"); r.add_argument("to")
    r.add_argument("--summary", required=True)
    r.add_argument("--captcha-id"); r.add_argument("--captcha-word")
    a = ap.parse_args()
    name = login()
    if a.cmd == "whoami":
        u = curl("action=query&meta=userinfo&uiprop=rights|groups|editcount&format=json")["query"]["userinfo"]
        print("logged in as:", u["name"], "| edits:", u.get("editcount"))
        print("groups:", ", ".join(u.get("groups", [])))
        print("can edit:", "edit" in u.get("rights", []), "| can create:", "createpage" in u.get("rights", []))
    elif a.cmd == "get":
        t = page_text(a.title); print(t if t is not None else "(page does not exist)")
    elif a.cmd == "diff":
        show_diff(page_text(a.title), open(a.file, encoding="utf-8").read(), a.title)
    elif a.cmd == "edit":
        cap = (a.captcha_id, a.captcha_word) if a.captcha_id and a.captcha_word else None
        do_edit(a.title, open(a.file, encoding="utf-8").read(), a.summary, a.create, cap)
    elif a.cmd == "redirect":
        cap = (a.captcha_id, a.captcha_word) if a.captcha_id and a.captcha_word else None
        do_edit(a.frm, f"#REDIRECT [[{a.to}]]\n", a.summary, True, cap)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Termux Setup – Maik Julien (Ju) – Python 3.11+
Rework & hardening: menu propre, installs fiables, Rich UI, offline-safe.
"""

from __future__ import annotations
import os, sys, time, subprocess, shutil, json, socket, datetime, platform
from dataclasses import dataclass, field

# ──────────────────────────[ Config perso ]──────────────────────────
@dataclass
class Brand:
    author: str = "Maik Julien"
    tool_name: str = "Termux Setup Pro"
    version: str = "2.0.0"
    github: str = "https://github.com/U7P4L-IN"   # modifiable
    telegram: str = "https://t.me/U7P4L"          # modifiable
    facebook_page: str = "https://www.facebook.com/U7P4L.XR"
    facebook_group: str = "https://facebook.com/groups/anonymouscyberxd/"

BRAND = Brand()

# ──────────────────────────[ Imports Rich ]──────────────────────────
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich import print as rprint
except Exception:
    os.system("pip install --quiet rich")
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich import print as rprint

console = Console()

# ──────────────────────────[ Utils ]──────────────────────────
MONTHS_FR = ["", "janvier","février","mars","avril","mai","juin",
             "juillet","août","septembre","octobre","novembre","décembre"]

def is_termux() -> bool:
    return "com.termux" in os.environ.get("PREFIX", "") or "TERMUX_VERSION" in os.environ

def termux_open(url: str):
    # xdg-open marche bien sous Termux, sinon on ignore
    try:
        subprocess.run(["xdg-open", url], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def run(cmd: list[str], sudo: bool=False) -> int:
    try:
        return subprocess.run(cmd, check=False).returncode
    except Exception:
        return 1

def run_quiet(cmd: list[str]) -> int:
    try:
        return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False).returncode
    except Exception:
        return 1

def have_net(timeout: float=2.0) -> bool:
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=timeout).close()
        return True
    except Exception:
        return False

def get_ip() -> str:
    if not have_net():
        return "offline"
    try:
        import urllib.request
        with urllib.request.urlopen("https://api.ipify.org", timeout=3) as r:
            return r.read().decode().strip()
    except Exception:
        return "unknown"

def now_strings():
    dt = datetime.datetime.now()
    date_str = f"{dt.day} {MONTHS_FR[dt.month]} {dt.year}"
    time_str = dt.strftime("%H:%M")
    return date_str, time_str

def titlebar(text: str):
    sys.stdout.write(f"\x1b]2;{text}\x07")

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def ok_panel(msg: str, title="OK"):
    rprint(Panel(msg, title=f"[bold white]{title}[/]"))

def warn_panel(msg: str, title="INFO"):
    rprint(Panel(msg, title=f"[bold yellow]{title}[/]"))

def err_panel(msg: str, title="ERREUR"):
    rprint(Panel(msg, title=f"[bold red]{title}[/]"))

# ──────────────────────────[ Install helpers ]──────────────────────────
PKG = "pkg" if shutil.which("pkg") else ("apt" if shutil.which("apt") else None)
PIP = shutil.which("pip") or "pip"

def ensure_pkg(pkgs: list[str]) -> dict[str, bool]:
    """
    Tente d'installer chaque paquet Termux. Retourne {pkg: success}
    Ignore silencieusement les paquets introuvables.
    """
    results = {}
    if not PKG:
        for p in pkgs:
            results[p] = False
        return results

    with Progress(
        SpinnerColumn(), TextColumn("[bold]Installation[/] {task.description}"),
        BarColumn(), TimeElapsedColumn(), console=console
    ) as progress:
        for p in pkgs:
            task = progress.add_task(f"{p}", total=None)
            # check déjà installé ?
            already = run_quiet([PKG, "show", p]) == 0
            if already:
                results[p] = True
                progress.update(task, description=f"{p} (déjà présent)")
                progress.remove_task(task)
                continue
            # install
            code = run([PKG, "install", "-y", p])
            results[p] = (code == 0)
            progress.remove_task(task)
    return results

def ensure_pip(pkgs: list[str]) -> dict[str, bool]:
    results = {}
    with Progress(
        SpinnerColumn(), TextColumn("[bold]pip[/] {task.description}"),
        BarColumn(), TimeElapsedColumn(), console=console
    ) as progress:
        for p in pkgs:
            task = progress.add_task(f"{p}", total=None)
            code = run([PIP, "install", "--upgrade", "--quiet", p])
            results[p] = (code == 0)
            progress.remove_task(task)
    return results

# ──────────────────────────[ Screens / Panels ]──────────────────────────
def logo():
    table = Table.grid(padding=(0,1))
    table.add_row(f"[bold magenta]{BRAND.tool_name}[/]  [dim]v{BRAND.version}[/]")
    table.add_row(f"[bold]Auteur:[/] {BRAND.author}")
    table.add_row(f"[bold]GitHub:[/] {BRAND.github}")
    table.add_row(f"[bold]Telegram:[/] {BRAND.telegram}")
    rprint(Panel(table, title="[bold white]WELCOME[/]"))

def details():
    ip = get_ip()
    date_str, time_str = now_strings()
    info = Table.grid(padding=(0,2))
    info.add_row("[bold cyan]Votre IP[/]", f"[white]{ip}")
    info.add_row("[bold cyan]Date[/]", f"[white]{date_str}")
    info.add_row("[bold cyan]Heure[/]", f"[white]{time_str}")
    rprint(Panel(info, title="[bold white]VOS INFOS[/]"))

def community():
    table = Table.grid(padding=(0,2))
    table.add_row("[bold]1[/] • Page Facebook", BRAND.facebook_page)
    table.add_row("[bold]2[/] • Groupe Facebook", BRAND.facebook_group)
    table.add_row("[bold]3[/] • Telegram", BRAND.telegram)
    table.add_row("[bold]4[/] • GitHub", BRAND.github)
    rprint(Panel(table, title="[bold white]COMMUNAUTÉ[/]"))

# ──────────────────────────[ Menus ]──────────────────────────
def prompt_choice(question: str, valid: set[str]) -> str:
    console.print(question, style="bold")
    while True:
        choice = console.input("[bold]╰─> [/]").strip().lower()
        if choice in valid:
            return choice
        warn_panel("Option invalide. Réessaie.", "Menu")

def main_menu():
    clear(); titlebar("⚙️ Termux Setup Pro"); logo()
    rprint(Panel(
        "[bold]1[/] • Termux BASIC setup\n"
        "[bold]2[/] • Termux FULL setup\n"
        "[bold]3[/] • Communauté & liens\n"
        "[bold]x[/] • Quitter",
        title="[bold white]MENU[/]"
    ))
    c = prompt_choice("Choisis une option [1/2/3/x]:", {"1","2","3","x"})
    if c == "1":
        basic_setup()
    elif c == "2":
        full_setup()
    elif c == "3":
        community(); 
        act = prompt_choice("Ouvrir un lien ? [1/2/3/4/n]:", {"1","2","3","4","n"})
        if act == "1": termux_open(BRAND.facebook_page)
        elif act == "2": termux_open(BRAND.facebook_group)
        elif act == "3": termux_open(BRAND.telegram)
        elif act == "4": termux_open(BRAND.github)
        time.sleep(0.6)
        main_menu()
    else:
        ok_panel("Merci d’avoir utilisé l’outil. À bientôt !", "EXIT")

# ──────────────────────────[ Setups ]──────────────────────────
def basic_setup():
    clear(); logo(); details()
    warn_panel("Lancement BASIC setup dans 2s…", "BASIC")
    time.sleep(1.5)
    if not is_termux():
        warn_panel("Attention : tu n’es pas dans Termux. Certaines installs peuvent échouer.", "ENV")

    # update / upgrade
    if PKG:
        run([PKG, "update"])
        run([PKG, "upgrade", "-y"])

    pkg_list = [
        "git", "curl", "wget", "python", "tmux",
        "openssl", "clang", "nano", "zip", "unzip",
        "neofetch", "vim", "proot", "fakeroot",
        "net-tools", "openssh", "ffmpeg", "cmatrix"
    ]
    res_pkg = ensure_pkg(pkg_list)

    pip_list = ["requests", "rich", "beautifulsoup4", "httpx", "pycurl", "lxml"]
    res_pip = ensure_pip(pip_list)

    show_results("BASIC", res_pkg, res_pip)
    main_menu()

def full_setup():
    clear(); logo(); details()
    warn_panel("Lancement FULL setup dans 2s…", "FULL")
    time.sleep(1.5)
    if PKG:
        run([PKG, "update"])
        run([PKG, "upgrade", "-y"])

    # Liste FULL – uniquement paquets réalistes sous Termux
    pkg_list = [
        # base
        "git","curl","wget","python","vim","nano","tmux","openssh","zip","unzip","tar","proot","fakeroot",
        "clang","make","neofetch","ffmpeg","net-tools","cmatrix","man",
        # shells & langages
        "bash","fish","ruby","php","perl","lua","golang",
        # web/cli utils
        "w3m","nmap","hydra","toilet","cowsay","tshark",  # tshark (wireshark CLI)
        # divers utiles
        "bmon","htop","screen","dnsutils","xmlstarlet","parallel","kibi","mariadb","cvs"
    ]
    res_pkg = ensure_pkg(pkg_list)

    pip_list = [
        "requests","rich","beautifulsoup4","mechanize","httpx","pycurl","lxml","pytube"
    ]
    res_pip = ensure_pip(pip_list)

    # Ruby gem optional (lolcat)
    if shutil.which("gem"):
        run(["gem","install","lolcat"])

    show_results("FULL", res_pkg, res_pip)
    main_menu()

def show_results(mode: str, res_pkg: dict[str,bool], res_pip: dict[str,bool]):
    table = Table(title=f"Récap install {mode}")
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("Nom", style="white")
    table.add_column("Statut", style="green")
    ok = "[green]OK[/]"
    ko = "[red]échec[/]"
    for k,v in res_pkg.items():
        table.add_row("pkg", k, ok if v else ko)
    for k,v in res_pip.items():
        table.add_row("pip", k, ok if v else ko)
    rprint(table)
    warn_panel("Les éléments en échec peuvent être indisponibles sur ton device/arch ou nécessiter des dépôts additionnels.", "NOTE")

# ──────────────────────────[ Entrypoint ]──────────────────────────
if __name__ == "__main__":
    try:
        clear(); logo()
        if not have_net():
            warn_panel("Mode hors-ligne détecté : les installs réseau pourront échouer. Tu peux relancer plus tard.", "RÉSEAU")
        main_menu()
    except KeyboardInterrupt:
        err_panel("Interrompu par l’utilisateur.", "STOP")

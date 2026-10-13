"""
watch-tui.py — dashboard TUI Sayrhazi (lecture seule, textual).

Vraie TUI : alternate screen, raw mode, layout, souris, resize, 60 FPS.
Lit `.opencode/state/workflow-state.yaml`, `.opencode/resume/*.txt`,
`.opencode/history/workflow-log.md`, `.opencode/state/watcher.lock`.

Usage :
    python .opencode/watch-tui.py [--interval SEC] [--lines N]
    q / Ctrl+C pour quitter.
"""

import argparse
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import Static, DataTable, Header, Footer, Label
    from textual.timer import Timer
    from textual.reactive import reactive
except ImportError:
    print("ERREUR : 'textual' requis. Installez : pip install textual", file=sys.stderr)
    sys.exit(1)

IS_WINDOWS = os.name == "nt"

ROLE_ORDER = ("architect", "designer", "builder", "reviewer", "security", "qa")
ROLE_AGENT_FILE = {"architect": "lawibrahim", "designer": "ali",
                   "builder": "bamse", "reviewer": "hadji",
                   "security": "hifadhui", "qa": "zawadi"}
ROLE_REPORT = {"architect": "plan.txt", "designer": "design.txt",
               "builder": "build.txt", "reviewer": "review.txt",
               "security": "security.txt", "qa": "qa.txt"}

TASK_RE = re.compile(r"^\s*task_id\s*:\s*(\S+)\s*$", re.MULTILINE | re.IGNORECASE)
STATUS_RE = re.compile(r"^\s*status\s*:\s*(\S.*?)\s*$", re.MULTILINE | re.IGNORECASE)


def _unquote(text: str) -> str:
    stripped = (text or "").strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in ("'", '"'):
        return stripped[1:-1]
    return stripped


def _flow_items(text: str) -> list:
    stripped = (text or "").strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        inner = stripped[1:-1].strip()
        if not inner:
            return []
        return [_unquote(p) for p in inner.split(",")]
    return [stripped] if stripped else []


STATE_KEYS = ("task_id", "status", "running_agents", "session")
SESSION_LEAF = ("id", "usage", "used_tokens", "cost", "observed_at")


def find_project_root(start: Path):
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".opencode" / "sayrhazi.yaml").is_file():
            return candidate
    try:
        script_parent = Path(__file__).resolve().parent
        if script_parent.name == ".opencode":
            return script_parent.parent
        if (script_parent.parent / ".opencode" / "sayrhazi.yaml").is_file():
            return script_parent.parent
    except NameError:
        pass
    return None


def read_state_minimal(project_root: Path) -> dict:
    path = project_root / ".opencode" / "state" / "workflow-state.yaml"
    data: dict = {}
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return data
    i = 0
    while i < len(lines):
        match = re.match(r"^\s{2}(\w+)\s*:\s*(.*)$", lines[i])
        if match and match.group(1) in STATE_KEYS:
            key = match.group(1)
            if key == "session" and match.group(2).strip() == "":
                session: dict = {}
                i += 1
                while i < len(lines):
                    sub = re.match(r"^\s{4}(\w+)\s*:\s*(.*)$", lines[i])
                    if not sub:
                        break
                    if sub.group(2).strip() == "":
                        block: dict = {}
                        i += 1
                        while i < len(lines):
                            leaf = re.match(r"^\s{6}(\w+)\s*:\s*(.*)$", lines[i])
                            if not leaf:
                                break
                            if leaf.group(1) in SESSION_LEAF:
                                block[leaf.group(1)] = _unquote(leaf.group(2))
                            i += 1
                        if block:
                            session[sub.group(1)] = block
                        continue
                    i += 1
                data[key] = session
                continue
            data[key] = _unquote(match.group(2))
        i += 1
    return data


def parse_report(path: Path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace").lstrip("﻿")
        mtime = path.stat().st_mtime
    except OSError:
        return None, None, None
    task = TASK_RE.search(text)
    status = STATUS_RE.search(text)
    return ((task.group(1).strip() if task else None),
            (status.group(1).strip().upper() if status else None), mtime)


def tail_lines(path: Path, count: int) -> list:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    return lines[-max(1, count):] if lines else []


def lock_info(project_root: Path):
    path = project_root / ".opencode" / "state" / "watcher.lock"
    try:
        content = path.read_text(encoding="utf-8", errors="replace").strip()
        pid = int(content.split()[0])
        age = time.time() - path.stat().st_mtime
        return pid, age
    except (OSError, ValueError, IndexError):
        return None, None


SESSION_DB_PARTS = (".local", "share", "opencode", "opencode.db")
SESSION_DEFAULT_LIMIT = 1048576
MODEL_CONTEXT = {"muse-spark": 1048576}


def opencode_db_path():
    candidate = Path(os.path.expanduser("~")).joinpath(*SESSION_DB_PARTS)
    return candidate if candidate.is_file() else None


def context_limit(model_id: str, default: int) -> int:
    low = (model_id or "").lower()
    for key, size in MODEL_CONTEXT.items():
        if key in low:
            return size
    return default if isinstance(default, int) and default > 0 else SESSION_DEFAULT_LIMIT


def parse_model_id(raw) -> str:
    import json
    text = str(raw or "").strip()
    if text.startswith("{"):
        try:
            return str(json.loads(text).get("id", "") or "")
        except (ValueError, AttributeError):
            return ""
    return text


def query_latest_agent_session(db_path, directory: str, agent_file: str):
    """Dernière session de l'agent pour le projet (repli hors watcher).

    Jamais bloquant : None si absente. Les compteurs sont cumulés
    (pas de baseline) : l'usage affiché est donc une borne haute.
    """
    try:
        import sqlite3
        db = sqlite3.connect("file:" + str(db_path) + "?mode=ro", uri=True, timeout=5)
        try:
            cur = db.cursor()
            cur.execute("SELECT id, tokens_input, tokens_output, tokens_cache_read,"
                        " tokens_cache_write, model, time_created, time_compacting, cost"
                        " FROM session WHERE directory = ? AND agent = ?"
                        " ORDER BY time_created DESC LIMIT 1",
                        ((directory or "").replace("\\", "/"), agent_file))
            found = cur.fetchone()
            if not found:
                return None
            keys = ("id", "tokens_input", "tokens_output", "tokens_cache_read",
                    "tokens_cache_write", "model", "time_created", "time_compacting", "cost")
            return dict(zip(keys, found))
        finally:
            db.close()
    except Exception:
        return None


def _num(value) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def session_used(row: dict, baseline: dict) -> int:
    if not row:
        return 0
    base = baseline or {}
    return ((_num(row.get("tokens_input")) - _num(base.get("baseline_input")))
            + (_num(row.get("tokens_output")) - _num(base.get("baseline_output")))
            + (_num(row.get("tokens_cache_write")) - _num(base.get("baseline_cache_write", 0))))


def format_tokens(count) -> str:
    try:
        return f"{max(0, int(count or 0)):,}".replace(",", " ")
    except (TypeError, ValueError):
        return "-"


def format_cost(value) -> str:
    try:
        return f"${max(0.0, float(value or 0.0)):.2f}"
    except (TypeError, ValueError):
        return "-"


def format_age(mtime: float) -> str:
    if not mtime:
        return "-"
    delta = max(0, int(time.time() - mtime))
    if delta < 60:
        return f"{delta}s"
    minutes, rest = divmod(delta, 60)
    if minutes < 60:
        return f"{minutes}m" if rest == 0 else f"{minutes}m{rest:02d}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h{minutes:02d}m"


def short_session(session_id: str) -> str:
    text = str(session_id or "")
    if text.startswith("ses_"):
        text = text[4:]
    return text[:10] if text else "?"


def bar(usage: float, width: int = 12) -> str:
    try:
        pct = max(0.0, min(1.0, float(usage or 0.0)))
    except (TypeError, ValueError):
        pct = 0.0
    filled = int(round(pct * width))
    return "█" * filled + "░" * (width - filled)


class AgentRow:
    def __init__(self, role: str, state: dict, resume: Path, task_id: str,
                 project_root=None):
        self.role = role
        self.agent_file = ROLE_AGENT_FILE[role]
        self.report = ROLE_REPORT[role]
        running = state.get("running_agents")
        running = running if isinstance(running, list) else _flow_items(running or "[]")
        r_task, r_status, r_mtime = parse_report(resume / self.report)
        sess = state.get("session")
        sess = sess if isinstance(sess, dict) else {}
        block = sess.get(self.agent_file) if isinstance(sess.get(self.agent_file), dict) else {}
        self.hors_watcher = False
        if not block and project_root is not None:
            db_path = opencode_db_path()
            if db_path is not None:
                row = query_latest_agent_session(db_path, str(project_root), self.agent_file)
                if row:
                    block = {"id": row.get("id"), "usage": 0.0,
                             "used_tokens": session_used(row, {}),
                             "cost": row.get("cost") or 0.0,
                             "observed_at": "",
                             "_cumul": True,
                             "_limit": context_limit(parse_model_id(row.get("model")),
                                                     SESSION_DEFAULT_LIMIT)}
                    self.hors_watcher = True

        if self.agent_file in running:
            self.etat = "[green]EN COURS[/]"
        elif r_task and task_id and r_task == task_id:
            self.etat = f"[cyan]{r_status or 'OK'}[/]"
        elif r_task:
            self.etat = "[dim]attente[/]"
        else:
            self.etat = "[dim]—[/]"

        try:
            usage = float(block.get("usage") or 0.0)
        except (TypeError, ValueError):
            usage = 0.0
        if self.hors_watcher:
            limit = block.get("_limit") or SESSION_DEFAULT_LIMIT
            try:
                usage = max(0.0, float(block.get("used_tokens") or 0) / limit)
            except (TypeError, ValueError, ZeroDivisionError):
                usage = 0.0
        self.usage_bar = bar(usage)
        self.usage_pct = f"{usage * 100:.0f} %" if block else "-"
        if self.hors_watcher:
            self.usage_pct = "~" + self.usage_pct
        self.tokens = format_tokens(block.get("used_tokens")) if block else "-"
        self.cost = format_cost(block.get("cost")) if block else "-"
        self.sid = short_session(block.get("id")) if block else "-"
        self.report_txt = f"{r_status or '-'} · {format_age(r_mtime or 0)}" if r_task else "-"


class SayrhaziTUI(App):
    CSS = """
    Screen { background: $surface; }
    #header { height: 3; dock: top; background: $primary; color: $text; text-align: center; }
    #table { height: 1fr; }
    #logs { height: 12; dock: bottom; border: solid $primary; padding: 1; }
    DataTable { background: $surface; }
    DataTable > .datatable--header { background: $primary; color: $text; text-style: bold; }
    DataTable > .datatable--cursor { background: $accent; color: $text; }
    .dim { color: $text-muted; }
    """

    BINDINGS = [("q", "quit", "Quitter"), ("r", "refresh", "Rafraîchir")]

    def __init__(self, project_root: Path, interval: float, log_lines: int):
        super().__init__()
        self.project_root = project_root
        self.interval = interval
        self.log_lines = log_lines
        self._timer: Timer | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(id="header")
        yield DataTable(id="table", cursor_type="row", zebra_stripes=True)
        yield Static(id="logs")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#table", DataTable)
        table.add_columns("Agent", "Rôle", "Session", "Usage", "Tokens", "Coût", "ID", "Rapport", "État")
        self._timer = self.set_interval(self.interval, self.refresh_data)
        self.refresh_data()

    def refresh_data(self) -> None:
        state = read_state_minimal(self.project_root)
        task_id = str(state.get("task_id") or "-")
        status = str(state.get("status") or "-")
        resume = self.project_root / ".opencode" / "resume"
        pid, age = lock_info(self.project_root)

        if pid is None:
            watcher_part = "[yellow]watcher : arrêté (pas de verrou)[/]"
        else:
            watcher_part = f"watcher PID [yellow]{pid}[/] · verrou {format_age(time.time() - age)}"

        header = self.query_one("#header", Static)
        header.update(f"Sayrhazi — [bold]{task_id}[/] [bold]{status}[/]  {watcher_part}  ·  racine {self.project_root}")

        table = self.query_one("#table", DataTable)
        table.clear(columns=True)
        table.add_columns("Agent", "Rôle", "Session", "Usage", "Tokens", "Coût", "ID", "Rapport", "État")
        for role in ROLE_ORDER:
            row = AgentRow(role, state, resume, task_id if task_id != "-" else "",
                           self.project_root)
            table.add_row(
                row.agent_file, role, row.usage_bar, row.usage_pct,
                row.tokens, row.cost, row.sid, row.report_txt, row.etat
            )

        logs = self.query_one("#logs", Static)
        log_lines = tail_lines(self.project_root / ".opencode" / "history" / "workflow-log.md", self.log_lines)
        if not log_lines:
            logs.update("[dim](aucun log)[/]")
        else:
            logs.update("\n".join(log_lines[-self.log_lines:]))

    def action_refresh(self) -> None:
        self.refresh_data()


def main() -> int:
    parser = argparse.ArgumentParser(description="Dashboard TUI Sayrhazi (textual)")
    parser.add_argument("--interval", type=float, default=1.0, help="refresh en secondes")
    parser.add_argument("--lines", type=int, default=10, help="lignes de log affichées")
    parser.add_argument("--once", action="store_true", help="un seul affichage puis sortie")
    args = parser.parse_args()

    root = find_project_root(Path.cwd())
    if root is None:
        print("ERREUR : racine projet introuvable (.opencode/sayrhazi.yaml absent).", flush=True)
        return 2
    interval = min(60.0, max(0.2, args.interval or 1.0))

    if args.once:
        state = read_state_minimal(root)
        task_id = str(state.get("task_id") or "-")
        status = str(state.get("status") or "-")
        resume = root / ".opencode" / "resume"
        pid, age = lock_info(root)
        if pid is None:
            watcher = "watcher : arrêté (pas de verrou)"
        else:
            watcher = f"watcher PID {pid} · verrou {format_age(time.time() - age)}"
        print(f"Sayrhazi — {task_id} [{status}]  {watcher}  ·  racine {root}")
        print()
        print(f"{'Agent':<12} {'Rôle':<9} {'Usage':<14} {'Tokens':>8} {'Coût':>6} {'ID':<10} {'Rapport':<18} {'État'}")
        print("─" * 100)
        for role in ROLE_ORDER:
            row = AgentRow(role, state, resume, task_id if task_id != "-" else "", root)
            usage_disp = f"{row.usage_bar} {row.usage_pct}"
            print(f"{row.agent_file:<12} {role:<9} {usage_disp:<14} {row.tokens:>8} {row.cost:>6} {row.sid:<10} {row.report_txt:<18} {row.etat}")
        print("─" * 100)
        print("logs récents (history/workflow-log.md) :")
        log_lines = tail_lines(root / ".opencode" / "history" / "workflow-log.md", max(1, args.lines))
        if not log_lines:
            print("  (aucun log)")
        else:
            for line in log_lines:
                print("  " + line)
        return 0

    app = SayrhaziTUI(root, interval, max(1, args.lines))
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
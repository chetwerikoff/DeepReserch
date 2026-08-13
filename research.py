#!/usr/bin/env python3
"""Vendor-neutral, stdlib-only deep-research execution runner."""
from __future__ import annotations

import argparse, base64, copy, hashlib, json, os, re, shutil, statistics, subprocess, sys, tempfile, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import urlparse

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
TIERS = {"S", "A", "B", "C", "D"}
KINDS = {"primary-research", "primary-format-repair", "fallback-research"}
BACKENDS = {"opencode", "cursor"}
OPENCODE_AGENT = "deep-research-worker"
EXA_MCP_NAME = "exa"
EXA_MCP_URL = "https://mcp.exa.ai/mcp"
EXA_MCP_TOOLS = {"exa_web_search_exa": "allow", "exa_web_fetch_exa": "allow"}
OPENCODE_DENY = {"edit": "deny", "bash": "deny", "external_directory": "deny", "task": "deny"}
OPENCODE_ALLOW = {
    "list": "allow",
    "glob": "allow",
    "grep": "allow",
}
OPENCODE_WEB_ALLOW = {"webfetch": "allow", "websearch": "allow"}
OPENCODE_READ = {"*": "allow", "*.env": "deny", "*.env.*": "deny", "*.env.example": "allow"}
SECRET_KEY_RE = re.compile(
    r"(?:api[_-]?key|access[_-]?key|token|secret|password|passwd|credential|"
    r"authorization|authentication|auth|bearer|private[_-]?key|client[_-]?secret|"
    r"refresh[_-]?token|session|cookie|signature|headers?)",
    re.IGNORECASE,
)

class RunnerFatal(RuntimeError): pass
class ValidationError(ValueError): pass


@dataclass(frozen=True)
class Invocation:
    backend: str
    argv: tuple[str, ...]
    env: Mapping[str, str]
    prompt: str
    cursor_mcp_json: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class InvocationResult:
    stdout: bytes
    stderr: bytes
    exit_code: int | None
    timed_out: bool = False
    verification_error: str | None = None
    raw_stdout: bytes | None = None
    opencode_session_id: str | None = None
    opencode_agent: str | None = None


Executor = Callable[[Invocation, float], InvocationResult]


def json_bytes(value: Any, compact: bool = False) -> bytes:
    kw = {"ensure_ascii": False, "sort_keys": True}
    text = json.dumps(value, separators=(",", ":"), **kw) if compact else json.dumps(value, indent=2, **kw) + "\n"
    return text.encode()


def fsync_dir(path: Path) -> None:
    if os.name == "nt": return
    try: fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    except OSError: return
    try: os.fsync(fd)
    finally: os.close(fd)


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.tmp-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path); fsync_dir(path.parent)
    except BaseException:
        try: os.unlink(tmp)
        except OSError: pass
        raise


def atomic_json(path: Path, value: Any) -> None: atomic_write(path, json_bytes(value))


def exclusive_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.tmp-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.link(tmp, path)
        fsync_dir(path.parent)
    finally:
        try: os.unlink(tmp)
        except OSError: pass


def load_json(path: Path) -> Any:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as e: raise RunnerFatal(f"invalid/unreadable JSON {path}: {e}") from e


def valid_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value): raise RunnerFatal(f"invalid {label}: must match {ID_RE.pattern}")
    return value


def safe_path(base: Path, *parts: str) -> Path:
    base = base.resolve(strict=False); out = base.joinpath(*parts).resolve(strict=False)
    if out != base and base not in out.parents: raise RunnerFatal(f"path escapes {base}: {out}")
    return out


def fingerprint(task: Mapping[str, Any]) -> str:
    body = {k: task[k] for k in ("id", "title", "objective", "queries")}
    return hashlib.sha256(json_bytes(body, compact=True)).hexdigest()


def validate_plan(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict): raise RunnerFatal("plan root must be an object")
    if not isinstance(value.get("topic"), str) or not value["topic"].strip(): raise RunnerFatal("plan.topic must be non-empty")
    if not isinstance(value.get("tasks"), list): raise RunnerFatal("plan.tasks must be an array")
    seen, tasks = set(), []
    for i, raw in enumerate(value["tasks"]):
        if not isinstance(raw, dict): raise RunnerFatal(f"tasks[{i}] must be an object")
        tid = valid_id(raw.get("id"), f"task id at {i}")
        if tid in seen: raise RunnerFatal(f"duplicate task id: {tid}")
        seen.add(tid)
        title, objective, queries = raw.get("title"), raw.get("objective"), raw.get("queries")
        if not isinstance(title, str) or not title.strip(): raise RunnerFatal(f"{tid}: title must be non-empty")
        if not isinstance(objective, str) or not objective.strip(): raise RunnerFatal(f"{tid}: objective must be non-empty")
        if not isinstance(queries, list) or not queries or any(not isinstance(q, str) or not q.strip() for q in queries):
            raise RunnerFatal(f"{tid}: queries must be a non-empty array of non-empty strings")
        tasks.append({"id": tid, "title": title, "objective": objective, "queries": list(queries)})
    return {"topic": value["topic"], "tasks": tasks}


def validate_findings(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, dict) or not isinstance(value.get("findings"), list): raise ValidationError("root.findings must be an array")
    errors, seen, out = [], set(), []
    for i, raw in enumerate(value["findings"]):
        p = f"findings[{i}]"
        if not isinstance(raw, dict): errors.append(f"{p} must be an object"); continue
        fid, claim, url, tier = raw.get("id"), raw.get("claim"), raw.get("source_url"), raw.get("source_tier")
        ok_id = isinstance(fid, str) and ID_RE.fullmatch(fid)
        if not ok_id: errors.append(f"{p}.id invalid")
        elif fid in seen: errors.append(f"duplicate finding id: {fid}")
        else: seen.add(fid)
        ok_claim = isinstance(claim, str) and bool(claim.strip())
        if not ok_claim: errors.append(f"{p}.claim must be non-empty")
        parsed = urlparse(url) if isinstance(url, str) else None
        ok_url = bool(parsed and parsed.scheme.lower() in {"http", "https"} and parsed.netloc)
        if not ok_url: errors.append(f"{p}.source_url must be absolute http/https")
        ok_tier = tier is None or tier in TIERS
        if not ok_tier: errors.append(f"{p}.source_tier invalid")
        if ok_id and ok_claim and ok_url and ok_tier:
            row = {"id": fid, "claim": claim, "source_url": url}
            if tier is not None: row["source_tier"] = tier
            out.append(row)
    if errors: raise ValidationError("; ".join(errors))
    return out


def extract_object(text: str) -> Any:
    text = text.strip()
    if not text: raise ValidationError("worker stdout is empty")
    try: return json.loads(text)
    except json.JSONDecodeError: pass
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.I)
    if m:
        try: return json.loads(m.group(1).strip())
        except json.JSONDecodeError: pass
    dec, found = json.JSONDecoder(), []
    for m in re.finditer(r"\{", text):
        try:
            obj, n = dec.raw_decode(text[m.start():])
            if isinstance(obj, dict): found.append((n, obj))
        except json.JSONDecodeError: pass
    if not found: raise ValidationError("worker stdout has no JSON object")
    return max(found, key=lambda x: x[0])[1]


def parse_stdout(data: bytes) -> list[dict[str, Any]]: return validate_findings(extract_object(data.decode("utf-8", "replace")))


def opencode_research_permissions(global_permission: Any, agent_permission: Any) -> dict[str, Any]:
    safe: dict[str, Any] = {
        "*": "deny",
        "read": copy.deepcopy(OPENCODE_READ),
        **OPENCODE_ALLOW,
        **OPENCODE_WEB_ALLOW,
        **EXA_MCP_TOOLS,
        **OPENCODE_DENY,
    }
    for source in (global_permission, agent_permission):
        if source == "deny":
            for key in ("read", *OPENCODE_ALLOW, *EXA_MCP_TOOLS):
                safe[key] = "deny"
            continue
        if not isinstance(source, dict): continue
        for key in ("read", *OPENCODE_ALLOW, *EXA_MCP_TOOLS):
            value = source.get(key)
            if value == "deny":
                safe[key] = "deny"
            elif key == "read" and isinstance(value, dict) and isinstance(safe["read"], dict):
                for pattern, action in value.items():
                    if action == "deny": safe["read"][pattern] = "deny"
    safe.update(OPENCODE_WEB_ALLOW)
    return safe

def opencode_config(existing: str | None) -> str:
    if existing:
        try: cfg = json.loads(existing)
        except json.JSONDecodeError as e: raise RunnerFatal(f"OPENCODE_CONFIG_CONTENT invalid: {e}") from e
        if not isinstance(cfg, dict): raise RunnerFatal("OPENCODE_CONFIG_CONTENT must be an object")
        cfg = copy.deepcopy(cfg)
    else: cfg = {}
    global_permission = cfg.get("permission")
    perms = copy.deepcopy(global_permission) if isinstance(global_permission, dict) else {}
    for key, value in OPENCODE_ALLOW.items(): perms.setdefault(key, value)
    perms.update(OPENCODE_WEB_ALLOW)
    perms.update(EXA_MCP_TOOLS)
    perms.update(OPENCODE_DENY)
    cfg["permission"] = perms
    cfg["mcp"] = {
        EXA_MCP_NAME: {
            "type": "remote",
            "url": EXA_MCP_URL,
            "enabled": True,
            "oauth": False,
            "codemode": False,
        }
    }
    agents = cfg.get("agent") if isinstance(cfg.get("agent"), dict) else {}; agents = copy.deepcopy(agents)
    agent = agents.get(OPENCODE_AGENT) if isinstance(agents.get(OPENCODE_AGENT), dict) else {}; agent = copy.deepcopy(agent)
    agent_permission = agent.get("permission")
    agent.update({"mode": "primary", "permission": opencode_research_permissions(global_permission, agent_permission)})
    agents[OPENCODE_AGENT] = agent; cfg["agent"] = agents
    return json.dumps(cfg, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _audit_permission(value: Any) -> dict[str, Any] | str | None:
    """Keep only permission entries needed to audit the research sandbox."""
    if value == "deny":
        return "deny"
    if not isinstance(value, dict):
        return None
    out: dict[str, Any] = {}
    for key in ("*", *OPENCODE_ALLOW, *OPENCODE_WEB_ALLOW, *EXA_MCP_TOOLS, *OPENCODE_DENY):
        action = value.get(key)
        if isinstance(action, str):
            out[key] = action
    read = value.get("read")
    if isinstance(read, str):
        out["read"] = read
    elif isinstance(read, dict):
        read_audit = {
            pattern: read[pattern]
            for pattern in OPENCODE_READ
            if isinstance(read.get(pattern), str)
        }
        if read_audit:
            out["read"] = read_audit
    return out


def _redact_all_values(value: Any) -> Any:
    """Preserve provider shape for diagnostics without persisting any provider values."""
    if isinstance(value, dict):
        return {
            str(key): "[REDACTED]" if SECRET_KEY_RE.search(str(key)) else _redact_all_values(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact_all_values(item) for item in value]
    return "[REDACTED]"


def scrub_opencode_config(content: str) -> str:
    """Persist a closed audit projection instead of the complete host OpenCode config."""
    try:
        cfg = json.loads(content)
    except json.JSONDecodeError as e:
        raise RunnerFatal(f"persisted OPENCODE_CONFIG_CONTENT invalid: {e}") from e
    if not isinstance(cfg, dict):
        raise RunnerFatal("persisted OPENCODE_CONFIG_CONTENT must be an object")

    agents = cfg.get("agent")
    agent = agents.get(OPENCODE_AGENT) if isinstance(agents, dict) else None
    mcp = cfg.get("mcp")
    exa = mcp.get(EXA_MCP_NAME) if isinstance(mcp, dict) else None

    audit: dict[str, Any] = {
        "permission": _audit_permission(cfg.get("permission")),
        "mcp": {},
        "agent": {},
        "model": cfg.get("model") if isinstance(cfg.get("model"), str) else None,
    }
    if isinstance(exa, dict):
        audit["mcp"][EXA_MCP_NAME] = {
            key: copy.deepcopy(exa[key])
            for key in ("type", "url", "enabled", "oauth", "codemode")
            if key in exa
        }
    if isinstance(agent, dict):
        selected = {
            "mode": agent.get("mode"),
            "permission": _audit_permission(agent.get("permission")),
        }
        if isinstance(agent.get("model"), str):
            selected["model"] = agent["model"]
        audit["agent"][OPENCODE_AGENT] = selected

    provider = cfg.get("provider")
    if isinstance(provider, dict):
        audit["provider"] = _redact_all_values(provider)

    return json.dumps(audit, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build_invocation(
    backend: str,
    prompt: str,
    model: str | None = None,
    cursor_command="cursor-agent",
    opencode_command="opencode",
    base_env=None,
    cursor_workspace: Path | None = None,
) -> Invocation:
    env = dict(os.environ if base_env is None else base_env)
    cursor_mcp_json = None
    if backend == "cursor":
        argv = [cursor_command, "--print", "--mode=ask", "--output-format", "text", "--approve-mcps"]
        if cursor_workspace is not None:
            workspace = Path(cursor_workspace).resolve(strict=False)
            cursor_mcp_json = {"mcpServers": {EXA_MCP_NAME: {"url": EXA_MCP_URL}}}
            atomic_json(
                safe_path(workspace, ".cursor", "mcp.json"),
                cursor_mcp_json,
            )
            argv += ["--workspace", str(workspace)]
        if model: argv += ["--model", model]
        argv.append(prompt)
    elif backend == "opencode":
        env["OPENCODE_CONFIG_CONTENT"] = opencode_config(env.get("OPENCODE_CONFIG_CONTENT"))
        argv = [opencode_command, "run", "--agent", OPENCODE_AGENT, "--format", "json"]
        if model: argv += ["--model", model]
        argv.append(prompt)
    else: raise RunnerFatal(f"unsupported backend: {backend}")
    return Invocation(backend, tuple(argv), env, prompt, cursor_mcp_json)


def _opencode_preflight_failure(reason: str) -> str:
    return f"opencode_safe_mode_preflight_failed:{reason}"


def verify_opencode_safe_mode(inv: Invocation, timeout: float) -> str | None:
    """Resolve OpenCode config before worker launch and fail closed unless the effective agent is research-safe."""
    try:
        resolved = subprocess.run(
            [inv.argv[0], "debug", "config"],
            env=dict(inv.env),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return _opencode_preflight_failure("timeout")
    except (FileNotFoundError, OSError) as e:
        return _opencode_preflight_failure(f"launch:{type(e).__name__}")
    if resolved.returncode != 0:
        return _opencode_preflight_failure(f"exit:{resolved.returncode}")
    try:
        cfg = json.loads(resolved.stdout.decode("utf-8", "replace"))
    except json.JSONDecodeError:
        return _opencode_preflight_failure("invalid_json")
    if not isinstance(cfg, dict):
        return _opencode_preflight_failure("non_object_config")
    global_permission = cfg.get("permission")
    agents = cfg.get("agent")
    agent = agents.get(OPENCODE_AGENT) if isinstance(agents, dict) else None
    agent_permission = agent.get("permission") if isinstance(agent, dict) else None
    if not isinstance(global_permission, dict):
        return _opencode_preflight_failure("global_permission_missing")
    if not isinstance(agent, dict):
        return _opencode_preflight_failure("agent_missing")
    if agent.get("mode") != "primary":
        return _opencode_preflight_failure("agent_mode")
    if not isinstance(agent_permission, dict):
        return _opencode_preflight_failure("agent_permission_missing")
    for key in OPENCODE_DENY:
        if global_permission.get(key) != "deny":
            return _opencode_preflight_failure(f"global_permission:{key}")
        if agent_permission.get(key) != "deny":
            return _opencode_preflight_failure(f"agent_permission:{key}")
    mcp = cfg.get("mcp")
    exa = mcp.get(EXA_MCP_NAME) if isinstance(mcp, dict) else None
    if not (
        isinstance(exa, dict)
        and exa.get("type") == "remote"
        and exa.get("url") == EXA_MCP_URL
        and exa.get("enabled") is True
    ):
        return _opencode_preflight_failure("exa_mcp")
    return None


def _opencode_failure(reason: str) -> str:
    return f"opencode_agent_verification_failed:{reason}"


def verify_opencode_output(inv: Invocation, stdout: bytes, timeout: float) -> tuple[bytes, str | None, str | None, str | None]:
    """Verify the selected agent through OpenCode's exported session record."""
    events = []
    for line in stdout.decode("utf-8", "replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            return b"", None, None, _opencode_failure("invalid_json_event")
        if not isinstance(event, dict):
            return b"", None, None, _opencode_failure("non_object_event")
        events.append(event)
    session_ids = {event.get("sessionID") for event in events if isinstance(event.get("sessionID"), str) and event.get("sessionID")}
    if len(session_ids) != 1:
        return b"", None, None, _opencode_failure("missing_or_ambiguous_session_id")
    session_id = next(iter(session_ids))
    try:
        exported = subprocess.run(
            [inv.argv[0], "export", session_id],
            env=dict(inv.env),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return b"", session_id, None, _opencode_failure("export_timeout")
    except (FileNotFoundError, OSError) as e:
        return b"", session_id, None, _opencode_failure(f"export_launch:{type(e).__name__}")
    if exported.returncode != 0:
        return b"", session_id, None, _opencode_failure(f"export_exit:{exported.returncode}")
    try:
        record = json.loads(exported.stdout.decode("utf-8", "replace"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return b"", session_id, None, _opencode_failure("invalid_export_json")
    info = record.get("info") if isinstance(record, dict) else None
    agent = info.get("agent") if isinstance(info, dict) else None
    if not isinstance(agent, str) or not agent:
        return b"", session_id, None, _opencode_failure("export_missing_agent")
    if agent != OPENCODE_AGENT:
        return b"", session_id, agent, _opencode_failure(f"unexpected_agent:{agent}")
    if isinstance(info.get("id"), str) and info["id"] != session_id:
        return b"", session_id, agent, _opencode_failure("export_session_mismatch")
    text = b"".join(
        part.get("text", "").encode("utf-8")
        for event in events
        if event.get("type") == "text"
        for part in [event.get("part")]
        if isinstance(part, dict) and isinstance(part.get("text"), str)
    )
    if not text:
        return b"", session_id, agent, _opencode_failure("missing_text_event")
    return text, session_id, agent, None


def subprocess_executor(inv: Invocation, timeout: float) -> InvocationResult:
    try:
        if inv.backend == "opencode":
            preflight_error = verify_opencode_safe_mode(inv, timeout)
            if preflight_error:
                return InvocationResult(b"", b"", 0, False, preflight_error, b"")
        p = subprocess.run(inv.argv, env=dict(inv.env), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)
        if inv.backend == "opencode" and p.returncode == 0:
            answer, session_id, agent, verification_error = verify_opencode_output(inv, p.stdout, timeout)
            return InvocationResult(answer, p.stderr, p.returncode, False, verification_error, p.stdout, session_id, agent)
        return InvocationResult(p.stdout, p.stderr, p.returncode, raw_stdout=p.stdout)
    except subprocess.TimeoutExpired as e:
        def b(v): return v if isinstance(v, bytes) else (v or "").encode()
        return InvocationResult(b(e.stdout), b(e.stderr), None, True, raw_stdout=b(e.stdout))
    except (FileNotFoundError, OSError) as e: raise RunnerFatal(f"cannot launch {inv.backend}: {e}") from e


def raw_value(attempt: Mapping[str, Any], invocation: Invocation, result: InvocationResult) -> dict[str, Any]:
    config = invocation.env.get("OPENCODE_CONFIG_CONTENT") if invocation.backend == "opencode" else None
    captured_stdout = result.raw_stdout if result.raw_stdout is not None else result.stdout

    value = {
        "schema": "deep-research-raw-attempt/v2",
        "ordinal": attempt["ordinal"],
        "kind": attempt["kind"],
        "backend": attempt["backend"],
        "argv": list(invocation.argv),
        "opencode_config_content": scrub_opencode_config(config) if config is not None else None,
        "cursor_mcp_json": copy.deepcopy(invocation.cursor_mcp_json),
        "opencode_session_id": result.opencode_session_id if invocation.backend == "opencode" else None,
        "opencode_agent": result.opencode_agent if invocation.backend == "opencode" else None,
        "verification_error": result.verification_error,
        "exit_code": result.exit_code,
        "timed_out": result.timed_out,
        "stdout_b64": base64.b64encode(captured_stdout).decode(),
        "stderr_b64": base64.b64encode(result.stderr).decode(),
    }
    if captured_stdout != result.stdout:
        value["answer_stdout_b64"] = base64.b64encode(result.stdout).decode()
    return value


def load_raw(path: Path) -> tuple[dict[str, Any], InvocationResult]:
    v = load_json(path)
    if not isinstance(v, dict) or v.get("schema") != "deep-research-raw-attempt/v2" or v.get("kind") not in KINDS or v.get("backend") not in BACKENDS:
        raise RunnerFatal(f"invalid raw envelope: {path}")
    if not isinstance(v.get("ordinal"), int) or v["ordinal"] < 1 or not isinstance(v.get("timed_out"), bool): raise RunnerFatal(f"invalid raw metadata: {path}")
    if (
        not isinstance(v.get("argv"), list)
        or not v["argv"]
        or any(not isinstance(item, str) for item in v["argv"])
        or (v["backend"] == "opencode" and not isinstance(v.get("opencode_config_content"), str))
        or (v["backend"] == "cursor" and not isinstance(v.get("cursor_mcp_json"), dict))
        or (v["backend"] == "opencode" and v.get("cursor_mcp_json") is not None)
        or (v["backend"] == "cursor" and v.get("opencode_config_content") is not None)
        or (v.get("verification_error") is not None and not isinstance(v.get("verification_error"), str))
        or (v.get("opencode_session_id") is not None and not isinstance(v.get("opencode_session_id"), str))
        or (v.get("opencode_agent") is not None and not isinstance(v.get("opencode_agent"), str))
    ):
        raise RunnerFatal(f"invalid raw invocation metadata: {path}")
    try: out, err = base64.b64decode(v["stdout_b64"], validate=True), base64.b64decode(v["stderr_b64"], validate=True)
    except (KeyError, TypeError, ValueError) as e: raise RunnerFatal(f"invalid raw bytes: {path}") from e
    try: answer = base64.b64decode(v.get("answer_stdout_b64", v["stdout_b64"]), validate=True)
    except (KeyError, TypeError, ValueError) as e: raise RunnerFatal(f"invalid raw answer bytes: {path}") from e
    code = v.get("exit_code")
    if code is not None and not isinstance(code, int): raise RunnerFatal(f"invalid raw exit code: {path}")
    return v, InvocationResult(answer, err, code, v["timed_out"], v.get("verification_error"), out, v.get("opencode_session_id"), v.get("opencode_agent"))


def task_prompt(contract: str, task: Mapping[str, Any]) -> str:
    return f"{contract.rstrip()}\n\n## Assigned task\n{json.dumps(task, ensure_ascii=False, sort_keys=True, indent=2)}\n\nReturn only the required JSON object on stdout."


def repair_prompt(raw: bytes, error: str) -> str:
    return ("Format the existing response only. Do not research, add, remove, reinterpret, strengthen, or weaken facts.\n\n"
            "Target contract: {\"findings\":[{\"id\":\"f1\",\"claim\":\"...\",\"source_url\":\"https://...\",\"source_tier\":\"S\"}]}\n"
            "source_tier is optional and must be S/A/B/C/D when present.\n\n"
            f"Exact validation errors:\n{error}\n\nPrior raw response:\n{raw.decode('utf-8', 'replace')}\n\nReturn only corrected JSON.")


class ResearchRunner:
    def __init__(self, *, session: str, runs_dir: Path, backend: str, fallback_backend: str | None = None, model: str | None = None,
                 fallback_model: str | None = None, max_workers=4, timeout=300.0, cursor_command="cursor-agent", opencode_command="opencode",
                 executor: Executor = subprocess_executor, worker_contract_path: Path | None = None):
        self.session = valid_id(session, "session id")
        if backend not in BACKENDS or (fallback_backend and fallback_backend not in BACKENDS): raise RunnerFatal("unsupported backend")
        if fallback_backend == backend and fallback_backend: raise RunnerFatal("fallback backend must differ from primary")
        if max_workers < 1 or timeout <= 0: raise RunnerFatal("invalid concurrency/timeout")
        self.backend, self.fallback_backend, self.model, self.fallback_model = backend, fallback_backend, model, fallback_model
        self.max_workers, self.timeout, self.cursor_command, self.opencode_command, self.executor = max_workers, timeout, cursor_command, opencode_command, executor
        self.runs_dir = runs_dir; runs_dir.mkdir(parents=True, exist_ok=True)
        self.root = safe_path(runs_dir.resolve(strict=False), self.session); self.root.mkdir(parents=True, exist_ok=True)
        self.raw, self.results = safe_path(self.root, "raw"), safe_path(self.root, "results")
        self.raw.mkdir(exist_ok=True); self.results.mkdir(exist_ok=True)
        if self.root.resolve() not in self.raw.resolve().parents or self.root.resolve() not in self.results.resolve().parents: raise RunnerFatal("runtime directory escapes run root")
        self.state_path, self.plan_path = safe_path(self.root, "state.json"), safe_path(self.root, "plan.json")
        wp = worker_contract_path or Path(__file__).resolve().parent / "prompts" / "worker.md"
        try: self.contract = wp.read_text(encoding="utf-8")
        except OSError as e: raise RunnerFatal(f"cannot read worker contract: {e}") from e
        self.lock, self.state, self.plan_by_id = threading.RLock(), {}, {}

    def raw_path(self, tid: str, n: int) -> Path:
        valid_id(tid, "task id")
        if not 1 <= n <= 99: raise RunnerFatal("invalid attempt ordinal")
        return safe_path(self.raw, f"{tid}-attempt-{n:02d}.txt")

    def result_path(self, tid: str) -> Path: return safe_path(self.results, f"{valid_id(tid, 'task id')}.json")

    def mutate(self, fn):
        with self.lock:
            candidate = copy.deepcopy(self.state)
            out = fn(candidate)
            atomic_json(self.state_path, candidate)
            self.state = candidate
            return out

    def admit(self, plan: Mapping[str, Any]) -> None:
        state = load_json(self.state_path) if self.state_path.exists() else {"schema": "deep-research-state/v1", "session_id": self.session, "tasks": {}}
        if not isinstance(state, dict) or state.get("schema") != "deep-research-state/v1" or state.get("session_id") != self.session or not isinstance(state.get("tasks"), dict):
            raise RunnerFatal("corrupt/incompatible state.json")
        candidate = copy.deepcopy(state); by_id = {t["id"]: t for t in plan["tasks"]}
        missing = set(candidate["tasks"]) - set(by_id)
        if missing: raise RunnerFatal(f"plan removed existing task ids: {', '.join(sorted(missing))}")
        for tid, task in by_id.items():
            fp, old = fingerprint(task), candidate["tasks"].get(tid)
            if old is None: candidate["tasks"][tid] = {"task_definition_sha256": fp, "status": "pending", "attempts": []}
            else:
                if not isinstance(old, dict) or not isinstance(old.get("attempts"), list): raise RunnerFatal(f"corrupt task state: {tid}")
                if old.get("task_definition_sha256") != fp: raise RunnerFatal(f"immutable task-definition drift: {tid}")
        candidate["topic"] = plan["topic"]
        # Plan first: a crash before state admission is safely replayable on resume.
        atomic_json(self.plan_path, plan); atomic_json(self.state_path, candidate)
        self.state, self.plan_by_id = candidate, by_id

    def result_valid(self, tid: str, ts: Mapping[str, Any]) -> dict[str, Any] | None:
        p = self.result_path(tid)
        if not p.exists(): return None
        try: v = load_json(p)
        except RunnerFatal: return None
        if not isinstance(v, dict) or v.get("task_id") != tid or v.get("task_definition_sha256") != ts.get("task_definition_sha256"): return None
        n = v.get("accepted_attempt_ordinal")
        match = [a for a in ts.get("attempts", []) if isinstance(a, dict) and a.get("ordinal") == n]
        if not isinstance(n, int) or len(match) != 1 or not self.raw_path(tid, n).exists(): return None
        if ts.get("status") == "completed" and ts.get("accepted_attempt_ordinal") != n: return None
        try: meta, _ = load_raw(self.raw_path(tid, n)); validate_findings({"findings": v.get("findings")})
        except (RunnerFatal, ValidationError): return None
        a = match[0]
        if any(meta.get(k) != a.get(k) for k in ("ordinal", "kind", "backend")): return None
        return v

    def reconcile(self) -> None:
        for tid, ts in list(copy.deepcopy(self.state["tasks"]).items()):
            v = self.result_valid(tid, ts)
            if ts.get("status") == "completed":
                if not v: raise RunnerFatal(f"{tid}: completed state has no valid accepted result")
                continue
            if v:
                n = v["accepted_attempt_ordinal"]
                def f(s, tid=tid, n=n):
                    t=s["tasks"][tid]; t.update(status="completed", accepted_attempt_ordinal=n); t.pop("error", None)
                    for a in t["attempts"]:
                        if a.get("ordinal")==n: a["phase"]="accepted"
                self.mutate(f)

    def start(self, tid: str, kind: str, backend: str, model: str | None) -> dict[str, Any]:
        if kind not in KINDS: raise RunnerFatal("invalid attempt kind")
        def f(s):
            t=s["tasks"][tid]
            if t.get("status") in {"completed","failed"}: raise RunnerFatal(f"cannot launch terminal task: {tid}")
            nums=[a.get("ordinal") for a in t["attempts"]]
            if any(not isinstance(n,int) for n in nums): raise RunnerFatal("corrupt attempt ordinal")
            n=max(nums, default=0)+1
            if n>3: raise RunnerFatal("attempt budget exceeded")
            a={"ordinal":n,"kind":kind,"backend":backend,"phase":"in_flight"}
            if model: a["model"]=model
            t["attempts"].append(a); t["status"]="in_flight"; t.pop("error",None); return copy.deepcopy(a)
        return self.mutate(f)

    def phase(self, tid: str, n: int, phase: str, error: str | None = None) -> None:
        def f(s):
            a=[x for x in s["tasks"][tid]["attempts"] if x.get("ordinal")==n]
            if len(a)!=1: raise RunnerFatal("attempt binding lost")
            a[0]["phase"]=phase
            if error: a[0]["error"]=error
        self.mutate(f)

    def fail(self, tid: str, error: str) -> None:
        self.mutate(lambda s: s["tasks"][tid].update(status="failed", error=error))

    def accept(self, tid: str, attempt: Mapping[str,Any], findings: list[dict[str,Any]]) -> None:
        ts=copy.deepcopy(self.state["tasks"][tid]); p=self.result_path(tid)
        value={"task_id":tid,"task_definition_sha256":ts["task_definition_sha256"],"accepted_attempt_ordinal":attempt["ordinal"],"findings":findings}
        if p.exists():
            if self.result_valid(tid, ts) != value: raise RunnerFatal(f"refusing to overwrite inconsistent result: {p}")
        else: atomic_json(p, value)
        n=attempt["ordinal"]
        def f(s):
            t=s["tasks"][tid]; t.update(status="completed",accepted_attempt_ordinal=n); t.pop("error",None)
            [a for a in t["attempts"] if a.get("ordinal")==n][0]["phase"]="accepted"
        self.mutate(f)

    def invoke(self, tid: str, kind: str, backend: str, prompt: str, model: str | None) -> tuple[dict[str,Any],InvocationResult]:
        # Build safe argv/env before consuming the attempt; no process starts until state is durable.
        inv=build_invocation(
            backend,
            prompt,
            model,
            self.cursor_command,
            self.opencode_command,
            cursor_workspace=self.root if backend == "cursor" else None,
        )
        a=self.start(tid,kind,backend,model); result=self.executor(inv,self.timeout)
        try: exclusive_write(self.raw_path(tid,a["ordinal"]), json_bytes(raw_value(a,inv,result)))
        except FileExistsError as e: raise RunnerFatal("raw attempt clobber refused") from e
        return a,result

    def fallback(self, tid: str, reason: str, previous_backend: str) -> None:
        if not self.fallback_backend or self.fallback_backend==previous_backend: self.fail(tid, reason); return
        a,r=self.invoke(tid,"fallback-research",self.fallback_backend,task_prompt(self.contract,self.plan_by_id[tid]),self.fallback_model)
        self.handle(tid,a,r)

    def handle(self, tid: str, a: Mapping[str,Any], r: InvocationResult) -> None:
        kind,n,backend=a["kind"],a["ordinal"],a["backend"]
        if r.verification_error:
            self.phase(tid,n,"verification_error",r.verification_error)
            if kind == "fallback-research": self.fail(tid, f"fallback {r.verification_error}")
            else: self.fallback(tid, f"{kind} {r.verification_error}", backend)
            return
        if r.timed_out or r.exit_code != 0:
            reason="timeout" if r.timed_out else f"process exit {r.exit_code}"; self.phase(tid,n,"process_error",reason)
            if kind=="fallback-research": self.fail(tid,f"fallback {reason}")
            else: self.fallback(tid,f"{kind} {reason}",backend)
            return
        try: findings=parse_stdout(r.stdout)
        except ValidationError as e:
            err=str(e); self.phase(tid,n,"invalid",err)
            if kind=="primary-research":
                a2,r2=self.invoke(tid,"primary-format-repair",backend,repair_prompt(r.stdout,err),a.get("model")); self.handle(tid,a2,r2)
            elif kind=="primary-format-repair": self.fallback(tid,f"format repair invalid: {err}",backend)
            else: self.fail(tid,f"fallback invalid: {err}")
            return

        self.accept(tid,a,findings)

    def recover_inflight(self) -> None:
        for tid,ts in list(copy.deepcopy(self.state["tasks"]).items()):
            if ts.get("status")!="in_flight": continue
            if not ts.get("attempts"): raise RunnerFatal(f"{tid}: in_flight without attempt")
            a=ts["attempts"][-1]; p=self.raw_path(tid,a.get("ordinal",0))
            if not p.exists(): self.fail(tid,"interrupted_unknown: started attempt has no complete raw outcome"); continue
            try: meta,r=load_raw(p)
            except RunnerFatal:
                self.fail(tid,"interrupted_unknown: started attempt has incomplete/unreadable raw outcome")
                continue
            if any(meta.get(k)!=a.get(k) for k in ("ordinal","kind","backend")): raise RunnerFatal(f"{tid}: raw/state attempt mismatch")
            self.handle(tid,a,r)

    def run_task(self, tid: str) -> None:
        if self.state["tasks"][tid].get("status")!="pending": return
        a,r=self.invoke(tid,"primary-research",self.backend,task_prompt(self.contract,self.plan_by_id[tid]),self.model); self.handle(tid,a,r)

    def execute(self, plan: Mapping[str,Any]) -> dict[str,Any]:
        self.admit(plan); self.reconcile(); self.recover_inflight()
        eligible=[tid for tid,t in copy.deepcopy(self.state["tasks"]).items() if t.get("status")=="pending"]
        errors=[]
        with ThreadPoolExecutor(max_workers=self.max_workers,thread_name_prefix="research") as pool:
            futures={pool.submit(self.run_task,tid):tid for tid in eligible}
            for f in as_completed(futures):
                try: f.result()
                except BaseException as e: errors.append(e)
        if errors:
            e=errors[0]
            if isinstance(e,RunnerFatal): raise e
            raise RunnerFatal(f"worker thread failed: {e}") from e
        return self.summary()

    def summary(self) -> dict[str,Any]:
        counts={k:0 for k in ("pending","in_flight","completed","failed")}; tasks={}
        for tid,t in copy.deepcopy(self.state["tasks"]).items():
            st=t.get("status","invalid"); counts[st]=counts.get(st,0)+1
            tasks[tid]={"status":st,"attempts":len(t.get("attempts",[])),"error":t.get("error")}
        return {"session_id":self.session,"counts":counts,"tasks":tasks}


def source_group(url: str) -> str:
    p=urlparse(url); host=(p.hostname or "").lower().rstrip(".")
    if not host: raise RunnerFatal(f"invalid source URL: {url}")
    parts=[x for x in p.path.split("/") if x]
    return f"github.com/{parts[0].lower()}/{parts[1].lower()}" if host=="github.com" and len(parts)>=2 else host


def compute_metrics(root: Path) -> dict[str,Any]:
    state,synth=load_json(safe_path(root,"state.json")),load_json(safe_path(root,"synthesis.json"))
    if not isinstance(state,dict) or not isinstance(state.get("tasks"),dict) or not isinstance(synth,dict) or not isinstance(synth.get("insights"),list): raise RunnerFatal("invalid state/synthesis for metrics")
    accepted={}; results=safe_path(root,"results")
    for tid,ts in state["tasks"].items():
        valid_id(tid,"task id")
        if not isinstance(ts,dict) or ts.get("status")!="completed": continue
        v=load_json(safe_path(results,f"{tid}.json"))
        if v.get("task_id")!=tid or v.get("task_definition_sha256")!=ts.get("task_definition_sha256"): raise RunnerFatal(f"result binding mismatch: {tid}")
        for row in validate_findings({"findings":v.get("findings")}):
            key=(tid,row["id"])
            if key in accepted: raise RunnerFatal(f"duplicate evidence key: {tid}:{row['id']}")
            accepted[key]=row
    rows,seen=[],set()
    for i,ins in enumerate(synth["insights"]):
        if not isinstance(ins,dict): raise RunnerFatal(f"insights[{i}] must be object")
        iid=valid_id(ins.get("id"),f"insight id at {i}")
        if iid in seen: raise RunnerFatal(f"duplicate insight id: {iid}")
        seen.add(iid); refs=ins.get("evidence")
        if not isinstance(refs,list): raise RunnerFatal(f"{iid}: evidence must be array")
        groups=set()
        for ref in refs:
            if not isinstance(ref,str) or ref.count(":")!=1: raise RunnerFatal(f"{iid}: malformed evidence ref {ref!r}")
            tid,fid=ref.split(":"); valid_id(tid,"evidence task id"); valid_id(fid,"evidence finding id")
            if (tid,fid) not in accepted: raise RunnerFatal(f"{iid}: unknown/unaccepted evidence {ref}")
            groups.add(source_group(accepted[(tid,fid)]["source_url"]))
        g=sorted(groups); rows.append({"id":iid,"source_group_depth":len(g),"source_groups":g})
    depths=[r["source_group_depth"] for r in rows]
    out={"schema":"deep-research-source-group-metrics/v1","disclaimer":"Mechanical host/repository groups do not prove publisher or editorial independence.",
         "insights":rows,"average_depth":statistics.fmean(depths) if depths else 0.0,"median_depth":statistics.median(depths) if depths else 0.0,
         "minimum_depth":min(depths) if depths else 0,"weak_insight_ids":[r["id"] for r in rows if r["source_group_depth"]<2]}
    atomic_json(safe_path(root,"metrics.json"),out); return out


def command_exists(cmd: str) -> bool:
    return Path(cmd).is_file() if os.sep in cmd or (os.altsep and os.altsep in cmd) else shutil.which(cmd) is not None


def preflight(a) -> None:
    needed={a.backend} | ({a.fallback_backend} if a.fallback_backend else set())
    if "cursor" in needed and not command_exists(a.cursor_command): raise RunnerFatal(f"Cursor executable not found: {a.cursor_command}")
    if "opencode" in needed and not command_exists(a.opencode_command): raise RunnerFatal(f"OpenCode executable not found: {a.opencode_command}")
    if a.fallback_backend and a.fallback_backend==a.backend: raise RunnerFatal("fallback backend must differ from primary")


def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(description="Resilient deep-research runner"); sub=p.add_subparsers(dest="command",required=True)
    r=sub.add_parser("run"); r.add_argument("--session",required=True); r.add_argument("--plan"); r.add_argument("--runs-dir",default="runs")
    r.add_argument("--backend",choices=sorted(BACKENDS),default="opencode"); r.add_argument("--fallback-backend",choices=sorted(BACKENDS)); r.add_argument("--model"); r.add_argument("--fallback-model")
    r.add_argument("--max-workers",type=int,default=4); r.add_argument("--timeout",type=float,default=300); r.add_argument("--opencode-command",default="opencode"); r.add_argument("--cursor-command",default="cursor-agent")
    for name in ("status","metrics"):
        q=sub.add_parser(name); q.add_argument("--session",required=True); q.add_argument("--runs-dir",default="runs")
    return p


def state_summary(state: Mapping[str,Any], session: str) -> dict[str,Any]:
    counts={k:0 for k in ("pending","in_flight","completed","failed")}; tasks={}
    for tid,t in state.get("tasks",{}).items():
        st=t.get("status","invalid") if isinstance(t,dict) else "invalid"; counts[st]=counts.get(st,0)+1
        tasks[tid]={"status":st,"attempts":len(t.get("attempts",[])) if isinstance(t,dict) else 0,"error":t.get("error") if isinstance(t,dict) else "invalid state"}
    return {"session_id":session,"counts":counts,"tasks":tasks}


def main(argv: Sequence[str] | None=None) -> int:
    a=parser().parse_args(argv)
    try:
        session=valid_id(a.session,"session id"); runs=Path(a.runs_dir); root=safe_path(runs.resolve(strict=False),session)
        if a.command=="status": print(json.dumps(state_summary(load_json(safe_path(root,"state.json")),session),ensure_ascii=False,indent=2,sort_keys=True)); return 0
        if a.command=="metrics": print(json.dumps(compute_metrics(root),ensure_ascii=False,indent=2,sort_keys=True)); return 0
        preflight(a); plan_path=Path(a.plan) if a.plan else safe_path(root,"plan.json"); plan=validate_plan(load_json(plan_path))
        rr=ResearchRunner(session=session,runs_dir=runs,backend=a.backend,fallback_backend=a.fallback_backend,model=a.model,fallback_model=a.fallback_model,max_workers=a.max_workers,timeout=a.timeout,cursor_command=a.cursor_command,opencode_command=a.opencode_command)
        print(json.dumps(rr.execute(plan),ensure_ascii=False,indent=2,sort_keys=True)); return 0
    except RunnerFatal as e:
        print(f"research.py: fatal: {e}",file=sys.stderr); return 2


if __name__ == "__main__": raise SystemExit(main())

#!/usr/bin/env python3
"""First-time publication of this website to a NEW GitHub.com repository.

Run on your own computer after installing Python 3, Git, and GitHub CLI.
No Python packages are required. Authentication is handled entirely by gh.
This helper never force-pushes, deletes repositories, or reuses an existing one.
"""

from __future__ import annotations

import argparse
import html.parser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parent
STATE = ROOT / ".github-pages-publish.json"
WORKFLOW = ".github/workflows/pages.yml"
SOURCE_PATHS = (
    "build.py", "content", "assets", "templates", "README.md",
    "DEPLOY_GITHUB.md", "SOURCE_NOTES.md", "ASSET_CREDITS.md",
    "LICENSE", "LICENSE.md", "publish_github.py", ".gitignore",
)


class PublishError(Exception):
    """An actionable failure without a success claim."""


def sanitized(message: str) -> str:
    message = re.sub(r"github_pat_[A-Za-z0-9_]+", "[redacted]", message)
    message = re.sub(r"gh[pousr]_[A-Za-z0-9_]+", "[redacted]", message)
    return message.strip()[:1500]


def command(args: list[str], *, required: bool = True, timeout: int = 60,
            interactive: bool = False) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if not interactive:
        env["GIT_TERMINAL_PROMPT"] = "0"
        env["GH_PROMPT_DISABLED"] = "1"
    try:
        result = subprocess.run(
            args, cwd=ROOT, env=env, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
            capture_output=not interactive,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PublishError(f"Could not finish {args[0]}: {sanitized(str(exc))}") from exc
    if required and result.returncode:
        detail = sanitized(result.stderr or result.stdout or "Command did not succeed.")
        raise PublishError(f"{args[0]} failed (exit {result.returncode}): {detail}")
    return result


def gh_api(endpoint: str, *, fields: dict | None = None,
           method: str = "GET", allow_404: bool = False) -> dict | None:
    args = ["gh", "api", "--hostname", "github.com", "--method", method,
            "-H", "Accept: application/vnd.github+json", endpoint]
    for key, value in (fields or {}).items():
        if isinstance(value, bool):
            args += ["-F", f"{key}={str(value).lower()}"]
        else:
            args += ["-f", f"{key}={value}"]
    result = command(args, required=False, timeout=45)
    if result.returncode:
        if allow_404 and "(HTTP 404)" in (result.stderr or ""):
            return None
        detail = sanitized(result.stderr or result.stdout or "GitHub API request failed.")
        raise PublishError(f"GitHub API request failed: {detail}")
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise PublishError("GitHub returned an unexpected response; nothing is assumed successful.") from exc
    if not isinstance(value, dict):
        raise PublishError("GitHub returned an unexpected response shape.")
    return value


def choose_new_repository(login: str, requested: str | None) -> str:
    if requested and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}", requested):
        raise PublishError("--repo must be a new repository name, without an owner, spaces, or slashes.")
    names = [requested] if requested else [f"{login.lower()}.github.io", "cai-lab-website"]
    for name in names:
        if gh_api(f"repos/{login}/{name}", allow_404=True) is None:
            return name
        print(f"Leaving existing repository unchanged: {login}/{name}", flush=True)
    raise PublishError("These repository names already exist. Run with --repo NEW_NAME to select a new one.")


def save_state(state: dict) -> None:
    temporary = STATE.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    temporary.replace(STATE)


def git_identity(user: dict) -> None:
    for key, fallback in (
        ("user.name", user.get("name") or user["login"]),
        ("user.email", f"{user['id']}+{user['login']}@users.noreply.github.com"),
    ):
        existing = command(["git", "config", "--get", key], required=False)
        if existing.returncode or not existing.stdout.strip():
            command(["git", "config", "--local", key, str(fallback)])


def push_main() -> None:
    # The credential helper applies to this command only; no global configuration
    # is changed and no token is copied into a URL, file, or command argument.
    command([
        "git", "-c", "credential.helper=",
        "-c", "credential.helper=!gh auth git-credential",
        "push", "--set-upstream", "origin", "main",
    ], timeout=120)


class TitleParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.parts.append(data)


def page_title(content: str) -> str:
    parser = TitleParser()
    parser.feed(content)
    return " ".join("".join(parser.parts).split())


def public_page_verified(url: str, expected_title: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Cai-Lab-Website-Publish/1.0"})
        with urllib.request.urlopen(request, timeout=20) as response:
            if response.status != 200:
                return False
            content = response.read(2_000_000).decode("utf-8", errors="replace")
            return bool(expected_title) and page_title(content) == expected_title
    except (OSError, urllib.error.URLError):
        return False


def wait_for_publication(state: dict, expected_title: str, seconds: int) -> int:
    repository = state["repository"]
    commit = state["commit"]
    deadline = time.monotonic() + seconds
    previous_status = None
    while time.monotonic() < deadline:
        result = gh_api(
            f"repos/{repository}/actions/workflows/pages.yml/runs?branch=main&per_page=10",
            allow_404=True,
        )
        matches = [run for run in (result or {}).get("workflow_runs", [])
                   if run.get("head_sha") == commit]
        run = matches[0] if matches else None
        status = "waiting for GitHub Actions"
        if run:
            state["workflow_run_url"] = run.get("html_url")
            status = run.get("status", "unknown")
            if status == "completed":
                conclusion = run.get("conclusion")
                if conclusion != "success":
                    save_state(state)
                    raise PublishError(
                        f"Website deployment ended with {conclusion}. Inspect the workflow: "
                        f"{run.get('html_url', state['repository_url'] + '/actions')}"
                    )
                pages = gh_api(f"repos/{repository}/pages")
                url = (pages or {}).get("html_url", "")
                if url and public_page_verified(url, expected_title):
                    state["verified_public_url"] = url
                    save_state(state)
                    print(f"Published and verified: {url}", flush=True)
                    return 0
                status = "deployment succeeded; waiting for the public page"
        if status != previous_status:
            print(f"Status: {status}", flush=True)
            previous_status = status
        time.sleep(min(10, max(0, deadline - time.monotonic())))
    save_state(state)
    print("Publication is still pending or the public page could not yet be verified.", flush=True)
    print(f"Check the workflow: {state.get('workflow_run_url') or state['repository_url'] + '/actions'}")
    print(f"Pages settings: {state['repository_url']}/settings/pages")
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="A new repository name under your authenticated personal account.")
    parser.add_argument("--login", action="store_true",
                        help="If necessary, open GitHub CLI's interactive browser login.")
    parser.add_argument("--wait-seconds", type=int, default=300,
                        help="Maximum deployment wait, 0–1200 seconds (default: 300).")
    args = parser.parse_args()
    if not 0 <= args.wait_seconds <= 1200:
        raise PublishError("--wait-seconds must be between 0 and 1200.")
    for executable in ("git", "gh"):
        if not shutil.which(executable):
            raise PublishError(f"Install {executable} first, then reopen your terminal. See DEPLOY_GITHUB.md.")
    for filename in ("build.py", "content/site.json", WORKFLOW):
        if not (ROOT / filename).is_file():
            raise PublishError(f"Required source is missing: {filename}. Extract the complete website package.")
    if (ROOT / ".git").exists() or STATE.exists():
        raise PublishError(
            "This first-publication helper needs a fresh extracted folder. Existing Git history or "
            "publishing state was found. For an already created repository, finish publication or "
            "update it using the commands in DEPLOY_GITHUB.md; this helper will not replace it."
        )

    print("Building the website locally...", flush=True)
    command([sys.executable, "build.py"], timeout=120)
    entry = ROOT / "dist" / "index.html"
    if not entry.is_file():
        raise PublishError("The build did not create dist/index.html. No repository was created.")
    expected_title = page_title(entry.read_text(encoding="utf-8"))
    if not expected_title:
        raise PublishError("The generated entry page has no title. No repository was created.")

    # Do not print gh auth status: its output can contain account/token metadata.
    authenticated = command(["gh", "auth", "status", "--hostname", "github.com"], required=False)
    if authenticated.returncode:
        if not args.login:
            raise PublishError("GitHub CLI is not signed in. Run gh auth login, or rerun with --login.")
        command([
            "gh", "auth", "login", "--hostname", "github.com",
            "--git-protocol", "https", "--web", "--scopes", "workflow",
        ], interactive=True, timeout=900)
    user = gh_api("user") or {}
    if not user.get("login") or not user.get("id"):
        raise PublishError("The authenticated GitHub account could not be identified.")
    repository_name = choose_new_repository(user["login"], args.repo)
    repository = f"{user['login']}/{repository_name}"
    print(f"Creating a new PUBLIC repository: {repository}", flush=True)

    # Build a local history containing only the explicitly selected site source.
    command(["git", "init", "--initial-branch=main"])
    git_identity(user)
    sources = [name for name in SOURCE_PATHS if (ROOT / name).exists()]
    command(["git", "add", "--", *sources])
    command(["git", "commit", "-m", "Create Cai Lab website"])

    created = gh_api("user/repos", method="POST", fields={
        "name": repository_name,
        "private": False,
        "auto_init": False,
        "description": "Cai Lab — vascular and valvular biology at the University of Missouri",
    }) or {}
    if not created.get("id") or not created.get("clone_url") or not created.get("html_url"):
        raise PublishError("GitHub repository creation returned an incomplete response; inspect your account before retrying.")
    if created.get("full_name", "").casefold() != repository.casefold():
        raise PublishError("GitHub returned a different repository identity; publication stopped.")
    state = {
        "repository": created["full_name"],
        "repository_id": created["id"],
        "repository_url": created["html_url"],
        "pages_configured": False,
    }
    save_state(state)
    print(f"Repository created: {created['html_url']}", flush=True)
    command(["git", "remote", "add", "origin", created["clone_url"]])
    push_main()
    gh_api(f"repos/{repository}", method="PATCH", fields={"default_branch": "main"})

    # Enable Pages after the initial branch exists but before adding the workflow,
    # so the first automatically triggered workflow can find its configuration.
    gh_api(f"repos/{repository}/pages", method="POST", fields={"build_type": "workflow"})
    state["pages_configured"] = True
    save_state(state)
    command(["git", "add", "--", WORKFLOW])
    command(["git", "commit", "-m", "Enable automatic GitHub Pages publication"])
    state["commit"] = command(["git", "rev-parse", "HEAD"]).stdout.strip()
    save_state(state)
    push_main()
    print("Source uploaded. Waiting for the GitHub Pages deployment...", flush=True)
    return wait_for_publication(state, expected_title, args.wait_seconds)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PublishError as error:
        print(f"Publication not completed: {error}", file=sys.stderr)
        if STATE.exists():
            try:
                saved = json.loads(STATE.read_text(encoding="utf-8"))
                if saved.get("repository_url"):
                    print(f"Preserved repository: {saved['repository_url']}", file=sys.stderr)
                    print("See DEPLOY_GITHUB.md to finish without creating another repository.", file=sys.stderr)
            except (OSError, json.JSONDecodeError):
                pass
        raise SystemExit(1)
    except KeyboardInterrupt:
        print("\nStopped. Any repository already created is preserved; see DEPLOY_GITHUB.md.", file=sys.stderr)
        raise SystemExit(130)

import shutil
import subprocess
import re


def detect_package_managers() -> tuple[str, ...]:
    candidates = ("apt", "apt-get", "winget", "choco", "brew", "dnf", "yum", "pacman")
    return tuple(name for name in candidates if shutil.which(name))


def query_package_version(manager: str, package: str) -> str | None:
    commands = {
        "apt": ["apt-cache", "policy", package],
        "apt-get": ["apt-cache", "policy", package],
        "dnf": ["dnf", "info", "-q", package],
        "yum": ["yum", "info", "-q", package],
        "pacman": ["pacman", "-Qi", package],
        "choco": ["choco", "list", "--exact", "--local-only", package],
        "winget": ["winget", "list", "--id", package, "--exact", "--accept-source-agreements"],
    }
    command = commands.get(manager)
    if not command:
        return None

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    if result.returncode != 0:
        return None

    output = "\n".join((result.stdout, result.stderr)).strip()
    if not output:
        return None
    if manager in {"apt", "apt-get"}:
        for line in output.splitlines():
            if line.strip().startswith("Installed:"):
                value = line.split(":", 1)[1].strip()
                return None if value in {"", "(none)"} else value
        return None
    if manager == "winget":
        if "No installed package found" in output:
            return None
        match = re.search(r"\b([^\s]+)\s+([0-9][0-9A-Za-z.+_-]*(?:\.[0-9A-Za-z.+_-]+)*)\s*$",
                          output, re.MULTILINE)
        return match.group(2) if match else None
    if manager == "pacman":
        match = re.search(r"^Version\s*:\s*(\S+)", output, re.MULTILINE)
        return match.group(1) if match else None
    return output

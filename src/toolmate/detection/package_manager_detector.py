import shutil


def detect_package_managers() -> tuple[str, ...]:
    candidates = ("apt", "apt-get", "winget", "choco", "brew", "dnf", "yum", "pacman")
    return tuple(name for name in candidates if shutil.which(name))

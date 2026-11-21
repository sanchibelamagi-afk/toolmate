from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import shlex
import stat
import sys
import tempfile
from typing import Iterable

from toolmate.core.models import CompatibilityResult, SystemInfo
from toolmate.core.manifest_manager import ManifestManager
from toolmate.platform import linux, macos, windows


START_MARKER = "# >>> ToolMate environment >>>"
END_MARKER = "# <<< ToolMate environment <<<"


@dataclass(frozen=True)
class EnvironmentPlan:
    target: str
    esim_home: str | None
    path_entries: tuple[str, ...]
    path_value: str | None
    profile_contents: str | None
    original_path: str | None
    original_esim_home: str | None
    original_profile: bytes | None

    def preview(self) -> str:
        lines = [f"Target: {self.target}"]
        if self.esim_home is not None:
            lines.append(f"ESIM_HOME = {self.esim_home}")
        else:
            lines.append("ESIM_HOME unchanged (no eSim directory detected)")
        if self.path_entries and self.path_value is not None:
            lines.append(f"PATH = {self.path_value}")
        if self.path_entries:
            lines.append("Add to user PATH:")
            lines.extend(f"  {entry}" for entry in self.path_entries)
        else:
            lines.append("No new tool PATH entries detected")
        if self.profile_contents is not None:
            block = self.profile_contents.split(START_MARKER, 1)[-1]
            block = block.split(END_MARKER, 1)[0].strip()
            if block:
                lines.extend(("", START_MARKER, block, END_MARKER))
        return "\n".join(lines)


class EnvironmentConfigurationService:
    def __init__(
        self,
        manifest_path: str | Path,
        backup_directory: str | Path | None = None,
        platform_name: str | None = None,
    ) -> None:
        self.manifest_path = Path(manifest_path)
        self.manifest = ManifestManager(self.manifest_path).load()
        self.backup_directory = (
            Path(backup_directory)
            if backup_directory is not None
            else Path.home() / ".toolmate" / "backups"
        )
        self.platform_name = platform_name or sys.platform

    def plan(
        self,
        system_info: SystemInfo,
        entries: Iterable[CompatibilityResult],
    ) -> EnvironmentPlan:
        path_entries = self._detected_path_entries(entries)
        if system_info.esim_path is not None:
            esim_bin = system_info.esim_path / "bin"
            if esim_bin.is_dir():
                path_entries.append(str(esim_bin.resolve()))
        path_entries = self._deduplicate(path_entries)
        path_entries = self._exclude_existing_path_entries(path_entries)
        esim_home = (
            str(system_info.esim_path.resolve())
            if system_info.esim_path is not None
            else None
        )

        if self.platform_name.startswith("win"):
            original_path, original_esim_home = windows.read_user_environment()
            path_entries = self._exclude_path_values(
                path_entries,
                original_path or "",
                separator=";",
                case_sensitive=False,
            )
            path_value = self._merge_path(
                original_path or "",
                path_entries,
                separator=";",
                case_sensitive=False,
            )
            target = r"HKCU\Environment"
            if not path_entries:
                path_value = original_path
            if esim_home is None and not path_value:
                raise ValueError("No detected eSim directory or tool paths to configure.")
            return EnvironmentPlan(
                target=target,
                esim_home=esim_home,
                path_entries=tuple(path_entries),
                path_value=path_value,
                profile_contents=None,
                original_path=original_path,
                original_esim_home=original_esim_home,
                original_profile=None,
            )

        if self.platform_name == "darwin":
            profile_path = macos.user_profile_path()
        else:
            profile_path = linux.user_profile_path()
        original_profile = profile_path.read_bytes() if profile_path.exists() else b""
        original_text = original_profile.decode("utf-8")
        line_ending = "\r\n" if "\r\n" in original_text else "\n"
        block = self._managed_block(esim_home, path_entries).replace("\n", line_ending)
        profile_contents = self._replace_managed_block(
            original_text,
            block,
            line_ending,
        )
        if not esim_home and not path_entries:
            raise ValueError("No detected eSim directory or tool paths to configure.")
        return EnvironmentPlan(
            target=str(profile_path),
            esim_home=esim_home,
            path_entries=tuple(path_entries),
            path_value=None,
            profile_contents=profile_contents,
            original_path=None,
            original_esim_home=None,
            original_profile=original_profile,
        )

    def apply(self, plan: EnvironmentPlan, approved: bool) -> Path:
        if not approved:
            raise PermissionError("Environment changes require explicit approval.")
        backup_path = self._backup_path()
        self.backup_directory.mkdir(mode=0o700, parents=True, exist_ok=True)

        if self.platform_name.startswith("win"):
            current_path, current_esim_home = windows.read_user_environment()
            if (
                current_path != plan.original_path
                or current_esim_home != plan.original_esim_home
            ):
                raise RuntimeError(
                    "The Windows user environment changed after preview; create a new plan."
                )
            backup_path.write_text(
                json.dumps(
                    {
                        "target": plan.target,
                        "Path": plan.original_path,
                        "ESIM_HOME": plan.original_esim_home,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            path_value = (
                plan.path_value
                if plan.path_value != plan.original_path
                else None
            )
            esim_home = (
                plan.esim_home
                if plan.esim_home != plan.original_esim_home
                else None
            )
            windows.write_user_environment(path_value, esim_home)
            return backup_path

        profile_path = Path(plan.target)
        profile_exists = profile_path.exists()
        current_profile = profile_path.read_bytes() if profile_exists else b""
        if current_profile != plan.original_profile:
            raise RuntimeError(
                "The shell profile changed after preview; create a new plan."
            )
        backup_path.write_bytes(plan.original_profile or b"")
        if os.name != "nt":
            backup_path.chmod(0o600)
        profile_mode = (
            stat.S_IMODE(profile_path.stat().st_mode)
            if profile_exists
            else 0o600
        )
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                newline="",
                dir=profile_path.parent,
                delete=False,
            ) as temporary:
                temporary.write(plan.profile_contents or "")
                temporary.flush()
                os.fsync(temporary.fileno())
                temporary_path = Path(temporary.name)
            latest_profile = (
                profile_path.read_bytes()
                if profile_path.exists()
                else b""
            )
            if latest_profile != plan.original_profile:
                raise RuntimeError(
                    "The shell profile changed after preview; create a new plan."
                )
            temporary_path.chmod(profile_mode)
            os.replace(temporary_path, profile_path)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
        return backup_path

    def _detected_path_entries(
        self,
        entries: Iterable[CompatibilityResult],
    ) -> list[str]:
        dependency_map = {
            str(dependency.get("id")): dependency
            for dependency in self.manifest["dependencies"]
            if dependency.get("id")
        }
        paths: list[str] = []
        for entry in entries:
            dependency = dependency_map.get(entry.id)
            if dependency is None or entry.path is None:
                continue
            detection = dependency.get("detection", {})
            method = detection.get("method") if isinstance(detection, dict) else None
            if method in {"executable", "all"} and entry.path.is_file():
                paths.append(str(entry.path.resolve().parent))
            elif method in {"executable", "all"} and entry.path.is_dir():
                paths.append(str(entry.path.resolve()))
            elif method == "path" and entry.path.is_dir():
                for candidate in (entry.path / "bin", entry.path / "tools" / "bin"):
                    if candidate.is_dir():
                        paths.append(str(candidate.resolve()))
        return paths

    @staticmethod
    def _deduplicate(paths: Iterable[str]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for value in paths:
            path = str(Path(value).resolve())
            key = os.path.normcase(os.path.normpath(os.path.expandvars(path)))
            if key not in seen:
                seen.add(key)
                result.append(path)
        return result

    def _exclude_existing_path_entries(self, paths: list[str]) -> list[str]:
        if self.platform_name.startswith("win"):
            return paths
        existing = os.environ.get("PATH", "").split(os.pathsep)
        def normalize(value: str) -> str:
            return os.path.normpath(value)

        existing_keys = {normalize(value) for value in existing if value}
        return [path for path in paths if normalize(path) not in existing_keys]

    @staticmethod
    def _exclude_path_values(
        paths: list[str],
        existing: str,
        separator: str,
        case_sensitive: bool,
    ) -> list[str]:
        existing_values = [value for value in existing.split(separator) if value]
        existing_keys = {
            os.path.normcase(os.path.normpath(os.path.expandvars(value))).casefold()
            if not case_sensitive
            else os.path.normpath(os.path.expandvars(value))
            for value in existing_values
        }
        return [
            path
            for path in paths
            if (
                os.path.normcase(os.path.normpath(path)).casefold()
                if not case_sensitive
                else os.path.normpath(path)
            )
            not in existing_keys
        ]

    @staticmethod
    def _merge_path(
        original: str,
        additions: Iterable[str],
        separator: str,
        case_sensitive: bool,
    ) -> str:
        values = [part for part in original.split(separator) if part]
        changed = False
        keys = {
            os.path.normpath(os.path.expandvars(value))
            if case_sensitive
            else os.path.normcase(
                os.path.normpath(os.path.expandvars(value))
            ).casefold()
            for value in values
        }
        for addition in additions:
            key = (
                os.path.normpath(addition)
                if case_sensitive
                else os.path.normcase(os.path.normpath(addition)).casefold()
            )
            if key not in keys:
                values.append(addition)
                keys.add(key)
                changed = True
        return separator.join(values) if changed else original

    @staticmethod
    def _managed_block(esim_home: str | None, path_entries: list[str]) -> str:
        lines = [START_MARKER]
        if esim_home:
            lines.append(f"export ESIM_HOME={shlex.quote(esim_home)}")
        if path_entries:
            path_value = ":".join(shlex.quote(path) for path in path_entries)
            lines.append(f'export PATH={path_value}:"$PATH"')
        lines.append(END_MARKER)
        return "\n".join(lines)

    @staticmethod
    def _replace_managed_block(
        contents: str,
        block: str,
        line_ending: str = "\n",
    ) -> str:
        has_start = START_MARKER in contents
        has_end = END_MARKER in contents
        if (
            has_start != has_end
            or contents.count(START_MARKER) > 1
            or contents.count(END_MARKER) > 1
        ):
            raise ValueError("Shell profile contains an incomplete ToolMate environment block.")
        if has_start:
            start = contents.index(START_MARKER)
            end = contents.index(END_MARKER, start) + len(END_MARKER)
            if contents.index(END_MARKER) < start:
                raise ValueError("Shell profile contains a malformed ToolMate environment block.")
            return contents[:start] + block + contents[end:]
        if not contents:
            return f"{block}{line_ending}"
        separator = "" if contents.endswith(line_ending) else line_ending
        return f"{contents}{separator}{line_ending}{block}{line_ending}"

    def _backup_path(self) -> Path:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        suffix = ".json" if self.platform_name.startswith("win") else ".bak"
        return self.backup_directory / f"environment-{stamp}{suffix}"

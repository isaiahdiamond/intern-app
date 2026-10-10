"""Configuration, read from the environment via a gitignored `.env`.

Nothing in this module may carry a default that is itself a credential. A missing
key is a missing key — `require` raises and names the variable so the fix is
obvious.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# The model used for skill extraction. Claude Opus 5.5 is the current default;
# override with INTERN_APP_MODEL to trade quality for cost on a bulk run.
DEFAULT_MODEL = "claude-opus-5-5"


class MissingConfig(RuntimeError):
    """A required environment variable is unset."""


@dataclass(frozen=True)
class Settings:
    db_path: Path
    model: str
    prompts_dir: Path
    roles_file: Path
    _env: dict[str, str] = field(default_factory=dict, repr=False)

    def get(self, name: str, default: str = "") -> str:
        """Return an optional variable, or `default` when it is unset or blank."""
        return self._env.get(name) or default

    def require(self, name: str) -> str:
        """Return a required variable, or raise naming it.

        Never include the value in the message — this exception reaches logs.
        """
        value = self._env.get(name)
        if not value:
            raise MissingConfig(f"{name} is not set. Add it to .env (see .env.example) and retry.")
        return value

    def has(self, *names: str) -> bool:
        """True when every named variable is set, so a source can skip itself."""
        return all(self._env.get(name) for name in names)


@lru_cache(maxsize=1)
def settings() -> Settings:
    load_dotenv(PROJECT_ROOT / ".env")
    db_path = Path(os.environ.get("INTERN_APP_DB") or PROJECT_ROOT / "data/intern_app.db")
    if not db_path.is_absolute():
        db_path = PROJECT_ROOT / db_path
    return Settings(
        db_path=db_path,
        model=os.environ.get("INTERN_APP_MODEL") or DEFAULT_MODEL,
        prompts_dir=PROJECT_ROOT / "prompts",
        roles_file=PROJECT_ROOT / "roles.txt",
        _env=dict(os.environ),
    )

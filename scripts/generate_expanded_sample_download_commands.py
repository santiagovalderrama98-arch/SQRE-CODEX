#!/usr/bin/env python3
"""Generate SQRE expanded historical sample download commands."""

from __future__ import annotations

import argparse
import shlex
from pathlib import Path
from typing import Any


REQUIRED_SAMPLE_FIELDS = {"sample_id", "symbol", "timeframe", "start", "end", "output_path"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate expanded sample download commands")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--provider")
    parser.add_argument("--timeframe")
    parser.add_argument("--sample")
    parser.add_argument("--missing-only", action="store_true")
    parser.add_argument("--output-script", type=Path)
    return parser.parse_args()


def load_sample_config(path: Path | str) -> dict[str, Any]:
    config_path = Path(path)
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to load expanded sample configs.") from exc
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Expanded sample config must be a YAML mapping.")
    _validate_sample_config(raw)
    return raw


def generate_commands(
    config: dict[str, Any],
    *,
    provider: str | None = None,
    timeframe: str | None = None,
    sample_id: str | None = None,
    missing_only: bool = False,
) -> list[str]:
    selected_provider = provider or str(config["provider"])
    commands: list[str] = []
    for sample in config["samples"]:
        if timeframe and str(sample["timeframe"]) != timeframe:
            continue
        if sample_id and str(sample["sample_id"]) != sample_id:
            continue
        output_path = Path(str(sample["output_path"]))
        if missing_only and output_path.exists():
            continue
        commands.append(_command(sample, selected_provider))
    return commands


def write_output_script(path: Path | str, commands: list[str]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = "#!/usr/bin/env bash\nset -euo pipefail\n\n"
    if commands:
        content += "\n\n".join(commands) + "\n"
    output_path.write_text(content, encoding="utf-8")
    output_path.chmod(0o755)
    return output_path


def main() -> int:
    args = parse_args()
    config = load_sample_config(args.config)
    commands = generate_commands(
        config,
        provider=args.provider,
        timeframe=args.timeframe,
        sample_id=args.sample,
        missing_only=args.missing_only,
    )
    if args.output_script:
        path = write_output_script(args.output_script, commands)
        print(f"Wrote download script: {path}")
        print(f"Commands written: {len(commands)}")
        return 0
    for command in commands:
        print(command)
        print()
    return 0


def _validate_sample_config(raw: dict[str, Any]) -> None:
    required = ["sample_set_name", "symbol", "provider", "pip_size", "samples"]
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"Expanded sample config is missing required keys: {', '.join(missing)}")
    if not isinstance(raw["samples"], list):
        raise ValueError("Expanded sample config samples must be a list.")
    for sample in raw["samples"]:
        if not isinstance(sample, dict):
            raise ValueError("Each expanded sample must be a mapping.")
        missing_sample_fields = sorted(REQUIRED_SAMPLE_FIELDS - set(sample))
        if missing_sample_fields:
            raise ValueError(f"Expanded sample is missing required keys: {', '.join(missing_sample_fields)}")


def _command(sample: dict[str, Any], provider: str) -> str:
    lines = [
        "python3 scripts/download_market_data.py \\",
        f"  --provider {_quote(provider)} \\",
        f"  --symbol {_quote(sample['symbol'])} \\",
        f"  --timeframe {_quote(sample['timeframe'])} \\",
        f"  --start {_quote(sample['start'])} \\",
        f"  --end {_quote(sample['end'])} \\",
        f"  --output {_quote(sample['output_path'])}",
    ]
    return "\n".join(lines)


def _quote(value: object) -> str:
    return shlex.quote(str(value))


if __name__ == "__main__":
    raise SystemExit(main())

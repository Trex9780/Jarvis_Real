#!/usr/bin/env python3
"""Run local Piper TTS with the Jarvis voice model."""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_MODEL = Path(__file__).resolve().parents[1] / "en_US-Jarvis_Real-medium.onnx"
DEFAULT_OUTPUT = "jarvis_tts.wav"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate speech WAV from text using Piper and the local Jarvis model."
    )
    parser.add_argument(
        "-t",
        "--text",
        help="Input text to synthesize. If omitted, stdin is used.",
    )
    parser.add_argument(
        "-m",
        "--model",
        default=os.getenv("JARVIS_PIPER_MODEL", str(DEFAULT_MODEL)),
        help=(
            "Path to Piper ONNX model "
            "(default: env JARVIS_PIPER_MODEL or repository model file)."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output WAV filename (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--piper-bin",
        default=os.getenv("PIPER_BIN", "piper"),
        help="Piper executable to run (default: env PIPER_BIN or 'piper').",
    )
    parser.add_argument(
        "--play",
        action="store_true",
        help="Play generated WAV after synthesis (best effort, platform dependent).",
    )
    return parser.parse_args()


def read_text(cli_text: str | None) -> str:
    if cli_text:
        return cli_text.strip()
    if sys.stdin.isatty():
        return ""
    return sys.stdin.read().strip()


def build_piper_command(piper_bin: str, model: Path, output: Path) -> list[str]:
    return [piper_bin, "--model", str(model), "--output_file", str(output)]


def run_piper(command: list[str], text: str) -> None:
    try:
        subprocess.run(
            command,
            input=text.encode("utf-8"),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError:
        print(
            f"Error: Piper executable not found: '{command[0]}'. "
            "Install Piper and ensure it is on PATH, or use --piper-bin.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    except subprocess.CalledProcessError as err:
        stderr = (err.stderr or b"").decode("utf-8", errors="replace").strip()
        print("Error: Piper failed to generate audio.", file=sys.stderr)
        if stderr:
            print(stderr, file=sys.stderr)
        else:
            print("No error details were returned by Piper.", file=sys.stderr)
        raise SystemExit(1)


def play_wav(path: Path) -> None:
    system = platform.system().lower()
    players: list[list[str]]

    if system == "darwin":
        players = [["afplay", str(path)]]
    elif system == "windows":
        players = [
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"(New-Object Media.SoundPlayer '{path}').PlaySync();",
            ]
        ]
    else:
        players = [["aplay", str(path)], ["paplay", str(path)], ["ffplay", "-nodisp", "-autoexit", str(path)]]

    for player in players:
        if shutil.which(player[0]) is None:
            continue
        try:
            subprocess.run(player, check=True)
            return
        except subprocess.CalledProcessError:
            continue

    print(
        "Warning: Could not play audio automatically. "
        f"Please open '{path}' with your preferred audio player.",
        file=sys.stderr,
    )


def main() -> int:
    args = parse_args()
    text = read_text(args.text)
    if not text:
        print("Error: No input text provided. Use --text or pipe stdin.", file=sys.stderr)
        return 1

    model_path = Path(args.model).expanduser().resolve()
    if not model_path.exists():
        print(
            f"Error: Model file not found: {model_path}\n"
            "Set --model or JARVIS_PIPER_MODEL to a valid .onnx file.",
            file=sys.stderr,
        )
        return 1

    config_path = Path(f"{model_path}.json")
    if not config_path.exists():
        print(
            f"Error: Model config not found: {config_path}\n"
            "Place the matching .json config next to the model file.",
            file=sys.stderr,
        )
        return 1

    output_path = Path(args.output).expanduser().resolve()
    run_piper(build_piper_command(args.piper_bin, model_path, output_path), text)
    print(f"WAV generated: {output_path}")

    if args.play:
        play_wav(output_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

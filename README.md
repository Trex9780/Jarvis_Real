# Jarvis Real Voice (Local Piper Runner)

This repository includes a local helper script for generating speech with the Jarvis Piper model.

## Prerequisites

1. Install [Piper](https://github.com/rhasspy/piper) and make sure `piper` is on your `PATH`.
2. Use Python 3.8+.

## Model files expected by default

The script defaults to this model path in this repository:

- `en_US-Jarvis_Real-medium.onnx`
- `en_US-Jarvis_Real-medium.onnx.json` (matching config, same folder)

If your model lives elsewhere, pass `--model` or set `JARVIS_PIPER_MODEL`.

## Usage

Script path: `scripts/tts_local.py`

From the repository root:

```bash
python3 scripts/tts_local.py --text "Hello, I am Jarvis."
```

This writes `jarvis_tts.wav` by default.

### Pipe text from stdin

```bash
echo "System online." | python3 scripts/tts_local.py
```

### Choose model and output path

```bash
python3 scripts/tts_local.py \
  --model /path/to/en_US-Jarvis_Real-medium.onnx \
  --output /tmp/jarvis.wav \
  --text "Custom output path."
```

### Configure model via environment variable

```bash
export JARVIS_PIPER_MODEL=/path/to/en_US-Jarvis_Real-medium.onnx
python3 scripts/tts_local.py --text "Using model from env."
```

### Optional direct playback (best effort)

```bash
python3 scripts/tts_local.py --text "Playing output now." --play
```

The script tries:

- Linux: `aplay`, then `paplay`, then `ffplay`
- macOS: `afplay`
- Windows: PowerShell `Media.SoundPlayer`

If none are available, the WAV file is still generated and you can open it manually.

## Troubleshooting

- **`piper` not found**  
  Install Piper and ensure it is on `PATH`, or pass `--piper-bin /path/to/piper`.

- **Model file not found**  
  Check `--model` or `JARVIS_PIPER_MODEL` points to a valid `.onnx` file.

- **Model config not found**  
  Ensure the matching `.onnx.json` file is next to the `.onnx` model.

- **No input text provided**  
  Pass `--text "..."` or pipe text through stdin.

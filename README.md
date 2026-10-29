# Pdf-2-Audio

Converts the text of a PDF into an audio file using offline text-to-speech (pyttsx3).

## Installation

```bash
pip install -r requirements.txt
```

System requirements:

- **Windows**: none (uses SAPI5).
- **macOS**: none (uses NSSpeechSynthesizer).
- **Linux**: `sudo apt install espeak-ng libespeak1`
- **MP3** output also requires `ffmpeg` in your PATH.

## Usage

```bash
python pdf2audio.py book.pdf                      # creates book.wav
python pdf2audio.py book.pdf -o book.mp3          # MP3 (requires ffmpeg)
python pdf2audio.py book.pdf --first 3 --last 10  # pages 3 to 10 only
python pdf2audio.py --list-voices                 # list installed voices
python pdf2audio.py book.pdf --voice en --rate 170
```

## Limitations

- Scanned PDFs (images only) contain no text: run them through OCR first, for example `ocrmypdf input.pdf output.pdf`.
- Available voices and languages depend on those installed on your operating system.

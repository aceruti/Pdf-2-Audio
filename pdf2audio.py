#!/usr/bin/env python3
"""Convert the text of a PDF into an audio file using offline text-to-speech."""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

import pyttsx3
from pypdf import PdfReader


def extract_text(pdf_path, first=None, last=None):
    """Return the text of the selected pages, cleaned up for speech."""
    reader = PdfReader(pdf_path)
    total = len(reader.pages)
    start = (first or 1) - 1
    end = min(last or total, total)

    parts = []
    for i in range(start, end):
        text = reader.pages[i].extract_text() or ""
        # Rejoin words hyphenated across line breaks ("paro-\nla" -> "parola")
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
        # Collapse newlines and repeated whitespace
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            parts.append(text)
        print(f"Pagina {i + 1}/{total}: {len(text)} caratteri", file=sys.stderr)

    return "\n\n".join(parts)


def pick_voice(engine, wanted):
    """Select the first voice whose id or name contains `wanted`."""
    voices = engine.getProperty("voices")
    for v in voices:
        if wanted.lower() in (v.id + " " + (v.name or "")).lower():
            engine.setProperty("voice", v.id)
            return v
    print(f"Voce '{wanted}' non trovata, uso quella predefinita.", file=sys.stderr)
    return None


def list_voices():
    engine = pyttsx3.init()
    for v in engine.getProperty("voices"):
        print(f"{v.id}  |  {v.name}  |  {getattr(v, 'languages', '')}")


def synthesize(text, output, voice=None, rate=None):
    engine = pyttsx3.init()
    if voice:
        pick_voice(engine, voice)
    if rate:
        engine.setProperty("rate", rate)

    want_mp3 = output.lower().endswith(".mp3")
    # pyttsx3 always writes uncompressed audio (WAV on Windows/Linux, AIFF on
    # macOS) whatever the extension, so render to a temp file and convert.
    if want_mp3:
        if not shutil.which("ffmpeg"):
            sys.exit("Per l'output MP3 serve ffmpeg nel PATH. "
                     "Installalo oppure usa un file .wav.")
        suffix = ".aiff" if sys.platform == "darwin" else ".wav"
        fd, raw = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
    else:
        raw = output

    engine.save_to_file(text, raw)
    engine.runAndWait()
    engine.stop()

    if not os.path.exists(raw) or os.path.getsize(raw) == 0:
        sys.exit("La sintesi vocale non ha prodotto audio.")

    if want_mp3:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw,
                        "-codec:a", "libmp3lame", "-q:a", "4", output], check=True)
        os.remove(raw)


def main():
    p = argparse.ArgumentParser(description="Converte un PDF in audio.")
    p.add_argument("pdf", nargs="?", help="file PDF di input")
    p.add_argument("-o", "--output", help="file audio (.wav o .mp3); "
                   "predefinito: stesso nome del PDF con .wav")
    p.add_argument("--first", type=int, help="prima pagina (da 1)")
    p.add_argument("--last", type=int, help="ultima pagina (inclusa)")
    p.add_argument("--voice", help="parte dell'id o del nome della voce, es. 'it' o 'Elsa'")
    p.add_argument("--rate", type=int, help="velocità in parole al minuto (default ~200)")
    p.add_argument("--list-voices", action="store_true", help="elenca le voci disponibili")
    p.add_argument("--print", action="store_true", help="stampa anche il testo estratto")
    args = p.parse_args()

    if args.list_voices:
        list_voices()
        return
    if not args.pdf:
        p.error("specifica il file PDF")
    if not os.path.isfile(args.pdf):
        sys.exit(f"File non trovato: {args.pdf}")

    output = args.output or os.path.splitext(args.pdf)[0] + ".wav"
    text = extract_text(args.pdf, args.first, args.last)
    if not text:
        sys.exit("Nessun testo estratto: il PDF è probabilmente una scansione "
                 "(immagini). Serve prima un OCR, ad esempio con ocrmypdf.")
    if args.print:
        print(text)

    synthesize(text, output, args.voice, args.rate)
    print(f"Audio salvato in {output}")


if __name__ == "__main__":
    main()

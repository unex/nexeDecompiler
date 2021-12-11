# nexeDecompiler

inspired by reversing Discord token stealers

tested on python `3.9.7` but it should work on `3.6+`

## Installation

```bash
pip install -U git+https://github.com/unex/nexeDecompiler.git
```

## CLI Usage

```bash
nexedecompiler
usage: nexedecompiler [-h] [--dest DEST] source
```

## Example

```bash
MALWARE$ nexedecompiler LiGzxBbAqEAQ.exe
Writing 6783 files to /MALWARE/LiGzxBbAqEAQ.exe_decompiled
Entrypoint located at /MALWARE/LiGzxBbAqEAQ.exe_decompiled/builds/LiGzxBbAqEAQ.js
```

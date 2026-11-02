#!/usr/bin/env python3
"""Extract reviewed source files from immutable release archive into build/, never .git."""
import sys,tarfile,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
version=sys.argv[1];assert version in ('v0.3.0','v0.4.0')
archive=ROOT/'baseline'/version/'source-and-evidence.tar.gz'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==(archive.parent/'SHA256SUMS').read_text().split()[0]
out=ROOT/'build/frozen'/version;out.mkdir(parents=True,exist_ok=True)
with tarfile.open(archive) as tf:
 for m in tf.getmembers():
  p=Path(m.name)
  if not m.isfile() or p.name.startswith('._') or p.is_absolute() or '..' in p.parts:continue
  if p.parts[0] not in ('CMakeLists.txt','ecu','sim','third_party'):continue
  target=out/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(tf.extractfile(m).read())
print(out)

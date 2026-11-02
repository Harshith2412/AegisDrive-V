#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${PLANTUML_JAR:?Set PLANTUML_JAR to PlantUML 1.2026.2 jar}"
mkdir -p results/v0.2.0
java -jar "$PLANTUML_JAR" -checkonly models/*.puml
java -jar "$PLANTUML_JAR" -tsvg models/*.puml
"${PYTHON:-.venv/bin/python}" - <<'PY'
import hashlib,json
from pathlib import Path
models=[]
for p in sorted(Path('models').glob('*.puml')):
    svg=p.with_suffix('.svg')
    text=svg.read_text()
    assert '<svg' in text and 'Syntax Error' not in text and 'Cannot find Graphviz' not in text,p
    models.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),svg=str(svg),validation='PlantUML parser and SVG renderer passed'))
Path('results/v0.2.0/models.json').write_text(json.dumps(dict(uml=models,sysml=dict(path='models/aeb.sysml',validation='UNVALIDATED: no SysML v2 parser installed')),indent=2))
print('Five UML models parsed and rendered. SysML v2 remains unvalidated.')
PY

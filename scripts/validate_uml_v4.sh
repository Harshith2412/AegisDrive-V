#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${PLANTUML_JAR:?Set to PlantUML 1.2026.2 jar}"
shasum -a 256 models/v0.4.0/trust_boundaries.puml
java -jar "$PLANTUML_JAR" -checkonly models/v0.4.0/*.puml
java -jar "$PLANTUML_JAR" -tsvg models/v0.4.0/*.puml
echo UML_VALIDATION_PASS

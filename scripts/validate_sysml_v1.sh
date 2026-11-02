#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${SYSML_PILOT_HOME:?Set to unpacked official jupyter-sysml-kernel-0.63.1 release directory}"
PILOT_JAR="$SYSML_PILOT_HOME/sysml/jupyter-sysml-kernel-0.63.1-all.jar"
mkdir -p build/sysml results/v1.0.0
javac -cp "$PILOT_JAR" -d build/sysml tools/sysml/ValidateSysML.java
shasum -a 256 models/v0.3.0/aegis.sysml models/v0.3.0/requirements.sysml models/v0.4.0/security.sysml models/v1.0.0/review.sysml
java -Xmx2g -cp "build/sysml:$PILOT_JAR" ValidateSysML "$SYSML_PILOT_HOME/sysml/sysml.library" models/v0.3.0/aegis.sysml models/v0.3.0/requirements.sysml models/v0.4.0/security.sysml models/v1.0.0/review.sysml
cp build/sysml/validated-input.sysml results/v1.0.0/validated-input.sysml
# A semantic negative control must fail; syntax alone is insufficient.
printf 'package Broken { part bad : NonexistentType; }\n' > build/sysml/negative.sysml
if java -Xmx2g -cp "build/sysml:$PILOT_JAR" ValidateSysML "$SYSML_PILOT_HOME/sysml/sysml.library" build/sysml/negative.sysml > results/v1.0.0/sysml-negative.log 2>&1; then
  echo 'ERROR: semantic negative control passed unexpectedly' >&2; exit 1
fi
if ! grep -q 'ERROR.*NonexistentType' results/v1.0.0/sysml-negative.log; then
  echo 'ERROR: negative control failed without the expected semantic diagnostic' >&2; exit 1
fi
echo 'Positive model semantic validation passed; unresolved-type negative control correctly rejected.'

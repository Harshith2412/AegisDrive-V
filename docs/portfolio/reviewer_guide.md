# Reviewer workflow

This folder had no project Git history or configured hosted URL during development. No
GitHub publication/tag is claimed. After the source is published by its owner:

```sh
git clone <published-repository-url>
cd aegisdrive-v
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip==26.2.2
.venv/bin/python -m pip install -r results/v1.0.0/dependencies.txt
scripts/reviewer.sh build
scripts/reviewer.sh test
scripts/reviewer.sh reference
```

For free model validation, obtain the pinned official SysML pilot 0.63.1 distribution and
PlantUML 1.2026.2, verify hashes in environment.json and unpack locally. Java 21 is used;
no commercial modeling tool, cloud service or global notebook installation is needed.

```sh
SYSML_PILOT_HOME=/path/to/sysml-0.63.1 PLANTUML_JAR=/path/to/plantuml.jar scripts/reviewer.sh models
scripts/reviewer.sh evaluate
scripts/reviewer.sh audit
```

The reference is short and deterministic apart from labeled host timings. Full evaluation
also builds archived sources into build/frozen, runs supported common cases and marks v0.3
security injections UNSUPPORTED. It preserves historical result files and locked hold-outs.
For exact prior reproduction, follow the environment overrides in reproduction.md and use
archived source/library together; do not run historical release generators on the current database.

Read executive summary, failure_analysis/review.md, evaluation.md, lifecycle_trace.md,
assurance case and open issues before interpreting test percentages. The actual build,
executed test logs, model hashes and raw failed outcomes are the authoritative evidence.
macOS is the validated host; Linux instructions are plausible but unverified here. No target
ECU or physical following-vehicle dynamics are modeled.

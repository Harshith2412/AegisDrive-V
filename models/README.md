# Assurance models

`context.puml` models item boundary and ECU connections; `interfaces.puml` the message data;
`sequence.puml` actual cyclic delivery/order; `adas_states.puml` all 26 legal transition edges;
`fault_tree.puml` the qualitative collision tree. Rendered SVGs are adjacent to source.
The state graph includes legal API-request edges; labels are destination intent summaries,
not complete executable guards. Exact guards and timing are documented in the safety concept
and implemented in `evaluate_threat_states`. Feedback faults indicate unavailable without
forcing the decision state to DEGRADED, which is reserved for input validity loss.

PlantUML parser/render validation is recorded in `results/v0.2.0/plantuml-validation.txt`.
`tools/check_assurance.py` additionally compares all state edges to the C++ table and checks
hazard/goal/requirement/component/model/test/evidence link integrity. Neither check establishes
behavioral equivalence or formal verification of the controller.

`aeb.sysml` uses genuine SysML v2 definitions/usages, typed ports, conjugation and connections,
following [OMG SysML v2](https://www.omg.org/spec/SysML/2.0). It is a structural model only;
**unvalidated** because no SysML v2 parser/toolchain is installed. It does not masquerade as
PlantUML or claim semantic validation. Full unit quantity typing, behavioral SysML models,
requirement satisfaction relationships and executable co-simulation remain future work.
PlantUML covers behavior in this release. Machine-readable requirement links reside in
`results/v0.2.0/safety_trace.json` and are supporting trace relationships, not formal SysML satisfy proofs.

Reproduce with Java 21 and PlantUML 1.2026.2:

```sh
java -jar /path/to/plantuml-1.2026.2.jar -checkonly models/*.puml
java -jar /path/to/plantuml-1.2026.2.jar -tsvg models/*.puml
.venv/bin/python tools/check_assurance.py
```

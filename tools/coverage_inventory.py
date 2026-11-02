#!/usr/bin/env python3
"""Export actual LLVM independent-condition coverage, including uncovered conditions."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/(sys.argv[1] if len(sys.argv)>1 else 'results/v1.0.0')
data=json.loads((OUT/'coverage/coverage.json').read_text())
records=[]
for f in data['data'][0]['files']:
    src=Path(f['filename']);text=src.read_text().splitlines()
    for rec in f.get('mcdc_records',[]):
        flags=rec[-1];start,end=rec[0],rec[2]
        records.append(dict(file=str(src.relative_to(ROOT)),line=start,condition_coverage=flags,
                            covered=sum(flags),total=len(flags),expression=' '.join(text[start-1:end])))
(OUT/'mcdc_conditions.json').write_text(json.dumps(records,indent=2))
lines=['# Measured MC/DC condition inventory','',
       'LLVM flags identify independent-condition coverage in tool order. False flags are uncovered.',
       'Trivial decisions and tool-excluded constructs are not inferred covered. Tests exercise safety behavior, not rewritten expressions.','',
       '| File / line | Covered / conditions | Coverage flags | Decision source |','|---|---|---|---|']
for r in records:
    expr=r['expression'].replace('|','&#124;')
    lines.append(f"| {r['file']}:{r['line']} | {r['covered']} / {r['total']} | {r['condition_coverage']} | {expr} |")
(OUT/'mcdc_conditions.md').write_text('\n'.join(lines)+'\n')
print('Independent conditions:',sum(x['covered'] for x in records),'/',sum(x['total'] for x in records))

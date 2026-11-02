#!/usr/bin/env python3
"""Export a source-backed technical presentation using standard plotting tools."""
from pathlib import Path
import textwrap,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
ROOT=Path(__file__).resolve().parents[2]
study=json.loads((ROOT/'results/v1.0.0/perception_study.json').read_text())
comparison=json.loads((ROOT/'results/v1.0.0/comparison.json').read_text())
slides=[
('AegisDrive-V v1.0.0','Integrated safety, security, MBSE and V-model engineering case study\nEducational research; not a safe-vehicle certification claim'),
('System and trust boundary','C++ ADAS, Brake and Body ECUs; Python longitudinal SiL\nCamera/radar fusion and shared physical actuator\n64-byte CAN FD HMAC envelope; public test keys, trusted local clock/FFI'),
('Independent review scope','Same automation in separate reviewer roles, not accredited external assessment\nFrozen v0.4 source/evidence; 92 baseline tests\n846 non-host-timing outputs reproduced with zero mismatches'),
('Eighteen security collision timelines','Strict: 6 stale-delivery +4 counter-gap +2 rollback/replay\nRecovery: the same 6 stale-delivery failures\nAll matched A cases avoid collision; withholding plus rejection/timeout removes braking'),
('Scoped engineering changes','Select newer authenticated producer time across valid transports\nNo raw/stale/replayed command bypass\nCurrent-pressure observation and 100 ms clear-dwell recovery; native DTC stays latched'),
('Perception tradeoffs','Temporal filtering suppresses a brief ghost but persistent ghosts pass\nCorroboration/confidence suppression can collide with genuine obstacles\n3 m/s² cap can increase close-obstacle impact risk; study profiles are not default'),
('Final robustness evidence','108 predefined cases in 12 strata\nActual v0.3: 81 supported, 27 security cases unavailable\nv0.4 and candidate: 47/108 collisions each; common 81-case comparison reported separately'),
('Verification and model limits','Requirement test status is separate from vehicle objective closure\nOfficial SysML parse/semantic validation is not behavioral equivalence\nStatic analyzer and UBSan evidence; ASan runtime timeout, partial MC/DC retained'),
('Structured assurance case','Claims + evidence + assumptions + counterexamples\nLegacy HARA/goal/requirement derivation gaps remain explicit\nPassing tests do not close unsafe vehicle objectives'),
('Open issues and contribution','Shared ECU/actuator and security dependencies; trusted compromise\nGhosts, grip, ODD, short distance; no real follower/target WCET\nContribution: defensible decisions, reproducibility, traceable evidence and transparent risks')]
out=ROOT/'docs/portfolio/technical_presentation.pdf'
with PdfPages(out) as pdf:
 for i,(title,body) in enumerate(slides):
  fig=plt.figure(figsize=(13.33,7.5),facecolor='#f6f8fc');ax=fig.add_axes([0,0,1,1]);ax.axis('off')
  ax.add_patch(plt.Rectangle((0,.84),1,.16,color='#15324f'))
  ax.text(.055,.91,title,color='white',fontsize=23,weight='bold',va='center')
  y=.72
  for paragraph in ([] if i in (5,6) else body.split('\n')):
   wrapped=textwrap.fill(paragraph,85)
   ax.text(.06,y,wrapped,color='#172b3a',fontsize=19,va='top');y-=.13+.045*wrapped.count('\n')
  if i==5:
   names=['union','corroborated','temporal','low_confidence','bounded_3mps2']
   labels=['Union','Corroborated','Temporal','Low confidence','3 m/s² cap']
   for j,(metric,title,denom) in enumerate([('collision','Genuine-target collisions /25',25),('unnecessary_braking','No-target braking /15',15)]):
    plot=fig.add_axes([[.14,.64][j],.22,[.33,.31][j],.47])
    values=[sum(r[metric] for r in study if r['profile']==name and (not r['case'].startswith(('persistent','brief')) if metric=='collision' else r['case'].startswith(('persistent','brief')))) for name in names]
    plot.barh(labels,values,color='#bf5b50' if j==0 else '#386b8e');plot.set_xlim(0,denom);plot.invert_yaxis();plot.set_title(title,fontsize=15)
    for k,value in enumerate(values):plot.text(value+.15,k,str(value),va='center',fontsize=11)
    plot.spines[['top','right']].set_visible(False)
   ax.text(.06,.12,'Designed cases; exact denominators differ. No following-vehicle or real traffic risk model.',fontsize=13,color='#172b3a')
   fig.savefig(ROOT/'docs/portfolio/perception_tradeoff.png',dpi=130)
  if i==6:
   plot=fig.add_axes([.26,.17,.66,.59]);cats=list(comparison['categories'])
   values=[comparison['categories'][cat]['candidate']['collisions'] for cat in cats]
   plot.barh([c.replace('_',' ') for c in cats],values,color='#386b8e');plot.invert_yaxis();plot.set_xlim(0,10)
   plot.set_xlabel('Candidate collisions per 9 cases in each predefined stratum',fontsize=12)
   for k,value in enumerate(values):plot.text(value+.12,k,str(value),va='center',fontsize=10)
   plot.spines[['top','right']].set_visible(False)
   ax.text(.06,.1,'47/108 candidate collisions; not a traffic probability. Actual v0.3 security cases unsupported.',fontsize=12,color='#172b3a')
   fig.savefig(ROOT/'docs/portfolio/final_strata.png',dpi=130)
  ax.text(.055,.045,'AegisDrive-V | Research artifact | Evidence and residuals in release package',fontsize=10,color='#53697a')
  ax.text(.95,.045,str(i+1),ha='right',fontsize=11,color='#53697a');pdf.savefig(fig);plt.close(fig)
(ROOT/'docs/portfolio/technical_presentation.md').write_text('\n\n---\n\n'.join('# '+t+'\n\n'+b+('\n\n![Measured tradeoff](perception_tradeoff.png)' if i==5 else '\n\n![Final strata](final_strata.png)' if i==6 else '') for i,(t,b) in enumerate(slides))+'\n')
print(out)

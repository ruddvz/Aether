#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from tools.photometry.candidate_review import evaluate_candidate,render_markdown

def main()->int:
    ap=argparse.ArgumentParser(description='Evaluate an exact lighting-head candidate against the VX4800 photometry selection brief')
    ap.add_argument('candidate',type=Path); ap.add_argument('--brief',type=Path,default=ROOT/'fixtures/vx4800/photometry/selection-brief.json'); ap.add_argument('--json-out',type=Path); ap.add_argument('--md-out',type=Path); args=ap.parse_args()
    candidate=json.loads(args.candidate.read_text()); brief=json.loads(args.brief.read_text()); review=evaluate_candidate(candidate,brief)
    if args.json_out: args.json_out.parent.mkdir(parents=True,exist_ok=True); args.json_out.write_text(json.dumps(review,indent=2)+'\n')
    if args.md_out: args.md_out.parent.mkdir(parents=True,exist_ok=True); args.md_out.write_text(render_markdown(review))
    print(render_markdown(review),end=''); return 2 if review['counts']['blocker'] else 0
if __name__=='__main__': raise SystemExit(main())

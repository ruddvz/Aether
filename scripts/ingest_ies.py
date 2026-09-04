#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from tools.photometry.ies_lm63 import parse_ies,to_report
from tools.photometry.polar_svg import render_polar_svg

def main()->int:
    ap=argparse.ArgumentParser(description='Ingest a controlled LM-63 IES file into an AETHERIA photometry package')
    ap.add_argument('ies',type=Path); ap.add_argument('--out',type=Path,required=True,help='Output directory'); ap.add_argument('--provenance',choices=['supplier','laboratory','unknown','synthetic-test'],default='unknown'); ap.add_argument('--manufacturer'); ap.add_argument('--model'); ap.add_argument('--source-url'); ap.add_argument('--received-at',help='ISO-8601 date-time'); ap.add_argument('--notes'); args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True); parsed=parse_ies(args.ies); report=to_report(parsed,filename=args.ies.name,provenance_status=args.provenance,manufacturer=args.manufacturer,model=args.model,source_url=args.source_url,received_at=args.received_at,notes=args.notes)
    raw_out=args.out/args.ies.name
    if raw_out.resolve()!=args.ies.resolve(): shutil.copyfile(args.ies,raw_out)
    report_out=args.out/f'{args.ies.stem}.report.json'; report_out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    polar_out=args.out/f'{args.ies.stem}.polar.svg'; render_polar_svg(report,polar_out)
    print(f'IES: {raw_out}'); print(f'SHA-256: {parsed.sha256}'); print(f'Report: {report_out}'); print(f'Polar: {polar_out}'); print(f"Peak candela: {report['photometry']['maxCandela']}")
    beam=report['photometry'].get('estimatedBeam')
    if beam: print(f"Estimated FWHM: {beam.get('fullWidthHalfMaximumDeg')}")
    if report['warnings']:
        print('Warnings:')
        for warning in report['warnings']: print(f'- {warning}')
    return 0
if __name__=='__main__': raise SystemExit(main())

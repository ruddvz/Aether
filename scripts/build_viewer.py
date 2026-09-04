from pathlib import Path
import json,base64,subprocess,sys
from generate_vx4800_presentation import build
from materialize_assets import materialize_background
ROOT=Path(__file__).resolve().parents[1]; FIX=ROOT/'fixtures/vx4800'; OUT=ROOT/'build/vx4800'; OUT.mkdir(parents=True,exist_ok=True)
materialize_background()
src=FIX/'presentation/v5.2.0'
data=build(); template=(src/'viewer.template.html').read_text(); css=(src/'viewer.styles.css').read_text(); js=(src/'viewer.app.js').read_text()
bg=base64.b64encode((src/'assets/architectural-background.webp').read_bytes()).decode()
html=(template.replace('__INLINE_CSS__',css).replace('__INLINE_JS__',js).replace('__VIEWER_DATA__',json.dumps(data,separators=(',',':'))).replace('__BACKGROUND_B64__',bg))
for token in ('__INLINE_CSS__','__INLINE_JS__','__VIEWER_DATA__','__BACKGROUND_B64__'):
    if token in html: raise RuntimeError(f'unresolved placeholder {token}')
p=OUT/'VX4800_VORTEX_Viewer_v5.2.0.html'; p.write_text(html); print(p)

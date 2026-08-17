from pathlib import Path
root=Path(__file__).resolve().parent.parent
html=(root/"web/index.html").read_text(encoding="utf-8");css=(root/"web/styles.css").read_text(encoding="utf-8")
checks={"one landing h1":html.count("<h1")==1,"intake dialog labelled":'aria-labelledby="incident-dialog-title"' in html,"skip link":"skip-link" in html,"theme button":'id="theme-toggle"' in html,"live region":'aria-live="polite"' in html,"map accessible":'aria-label="Synthetic advisory zone' in html,"keyboard focus":":focus-visible" in css,"reduced motion":"prefers-reduced-motion" in css,"mobile layout":"max-width:760px" in css,"text status":'id="state-title"' in html}
for k,v in checks.items():print(f"{'PASS' if v else 'FAIL'}  {k}")
raise SystemExit(0 if all(checks.values()) else 1)


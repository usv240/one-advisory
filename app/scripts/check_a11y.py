from pathlib import Path
root=Path(__file__).resolve().parent.parent
html=(root/"web/index.html").read_text(encoding="utf-8");judges=(root/"web/judges.html").read_text(encoding="utf-8");css=(root/"web/styles.css").read_text(encoding="utf-8")
checks={"one landing h1":html.count("<h1")==1,"one judge h1":judges.count("<h1")==1,"skip links":"skip-link" in html and "skip-link" in judges,"theme buttons":'id="theme-toggle"' in html and 'id="theme-toggle"' in judges,"live region":'aria-live="polite"' in html,"map accessible":'aria-label="Synthetic advisory zone' in html,"keyboard focus":":focus-visible" in css,"reduced motion":"prefers-reduced-motion" in css,"mobile layout":"max-width:760px" in css,"text status":'id="state-title"' in html}
for k,v in checks.items():print(f"{'PASS' if v else 'FAIL'}  {k}")
raise SystemExit(0 if all(checks.values()) else 1)


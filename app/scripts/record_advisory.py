"""Record and grade one live Gemini advisory read."""
from __future__ import annotations
import argparse,json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from one_advisory.reader import AdvisoryReader,VertexAdvisoryClient
root=Path(__file__).resolve().parent.parent
def main():
    p=argparse.ArgumentParser();p.add_argument("--document",required=True);a=p.parse_args();project=os.environ.get("GOOGLE_CLOUD_PROJECT","").strip()
    if not project:raise SystemExit("GOOGLE_CLOUD_PROJECT is required")
    path=Path(a.document);mime="image/svg+xml" if path.suffix.lower()==".svg" else "image/png";result=AdvisoryReader(VertexAdvisoryClient(project)).read(path.read_bytes(),mime)
    truth=json.loads((root/"fixtures/advisory.truth.json").read_text(encoding="utf-8"));actual={r["key"]:r["value"].casefold() for r in result.fields};checks={k:actual.get(k)==str(v).casefold() for k,v in truth.items() if k!="synthetic"};recording={"model":"gemini-3.5-flash","mode":"recorded-live-vertex-ai","synthetic":True,"transcription":result.transcription,"fields":result.fields,"dropped":result.dropped};report={"matched":sum(checks.values()),"total":len(checks),"checks":checks};(root/"fixtures/advisory.recording.json").write_text(json.dumps(recording,indent=2),encoding="utf-8");(root/"fixtures/advisory.accuracy.json").write_text(json.dumps(report,indent=2),encoding="utf-8");print(json.dumps(report,indent=2));return 0 if all(checks.values()) else 1
if __name__=="__main__":raise SystemExit(main())




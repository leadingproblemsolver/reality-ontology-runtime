"""Read-only evidence-bounded prototype scan. Run: python tools/prototype_gate.py PATH."""
from __future__ import annotations
import fnmatch, json, sys
from pathlib import Path

IGNORE={".git","node_modules",".venv","venv","__pycache__","dist","build",".next",".pytest_cache"}
CHECKS={
"frontend":(["index.html","src/app.*","src/pages/*","app/page.*","pages/index.*","frontend/*"],"Browser-tested user journey"),
"backend":(["server.*","api/*","backend/*","src/**/web.py","src/**/cli.py"],"Route contract, input validation and failure case"),
"persistence":(["**/store.py","**/db.py","**/models.py","**/migrations/*","**/schema.prisma"],"Write/restart/reread and duplicate request test"),
"tests":(["tests/test_*.py","**/*.test.*","**/*.spec.*"],"Clean test run with failed-path coverage"),
"ci":([".github/workflows/*",".gitlab-ci.yml"],"Verified CI for exact commit SHA"),
"deployment":(["Dockerfile","vercel.json","netlify.toml","render.yaml"],"Public URL, deployed revision, health and rollback"),
"identity":(["**/auth/*","**/permissions.*","**/middleware.*"],"Unauthenticated and cross-user access tests"),
"observability":(["**/logging.*","**/telemetry.*","**/metrics.*"],"Forced failure observed and recoverable"),
"documentation":(["README.md","docs/*"],"Independent clean-checkout setup reproduction"),
"configuration":([".env.example","pyproject.toml","package.json","requirements.txt"],"Clean install, secrets audit and configuration test")}
def audit(root):
    root=Path(root).expanduser().resolve()
    if not root.is_dir(): raise ValueError("target must be a directory")
    paths=[]
    for p in sorted(root.rglob("*")):
        if any(part in IGNORE for part in p.relative_to(root).parts) or p.is_symlink(): continue
        if p.is_file(): paths.append(p.relative_to(root).as_posix())
        if len(paths)>=12000: break
    rows=[]
    for area,(patterns,gate) in CHECKS.items():
        clues=sorted({p for p in paths if any(fnmatch.fnmatch(p,pat) or (pat.startswith("**/") and fnmatch.fnmatch(p,pat[3:])) for pat in patterns)})[:12]
        rows.append({"area":area,"state":"CANDIDATE_UNVERIFIED" if clues else "NOT_DETECTED","file_clues":clues,"required_acceptance":gate})
    return {"schema_version":"prototype-gate/1","root":str(root),"files_scanned":len(paths),"truncated":len(paths)>=12000,"claim_boundary":"STATIC CLUES ONLY: no tests, user journeys, external effects or deployments verified","findings":rows,"next_action":"Run the smallest real user journey and capture execution, failure and external observation receipts"}
if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: python tools/prototype_gate.py PATH")
    print(json.dumps(audit(sys.argv[1]),indent=2))

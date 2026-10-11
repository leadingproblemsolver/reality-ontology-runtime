from copy import deepcopy
import pytest
from reality_ontology.github_comment import packet, execute
from reality_ontology.store import RealityStore

REPO = "leadingproblemsolver/reality-ontology-runtime"

class Fake:
    def __init__(self):
        self.rows = []
        self.posts = 0
    def comments(self, repo, issue):
        return list(self.rows)
    def post(self, repo, issue, body):
        self.posts += 1
        self.rows.append({"id": self.posts, "body": body, "html_url": f"https://github.com/{repo}/issues/{issue}#issuecomment-{self.posts}"})
        return self.rows[-1]

def approve(db, spec):
    with RealityStore(db) as store:
        a=store.add_actor("approver")
        store.approve(spec["transition_id"], a)

def test_approval_before_write_and_fresh_replay(tmp_path):
    db=str(tmp_path/"r.db")
    s=packet(REPO, 1, "Inspected concrete comment.")
    fake=Fake()
    with pytest.raises(PermissionError):
        execute(db,s,client=fake)
    assert fake.posts == 0
    approve(db,s)
    first=execute(db,s,client=fake)
    replay=execute(db,s,client=fake)
    assert fake.posts == 1
    assert first["status"] == "VERIFIED_POSTED"
    assert replay["status"] == "VERIFIED_ALREADY_PRESENT"
    with RealityStore(db) as store:
        assert store.db.execute("SELECT COUNT(*) FROM settlements").fetchone()[0] == 1
        assert store.db.execute("SELECT COUNT(*) FROM events WHERE event_id=?", (first["event_id"],)).fetchone()[0] == 1

def test_approval_is_bound_to_exact_content(tmp_path):
    db=str(tmp_path/"r.db")
    spec=packet(REPO, 1, "Original")
    approve(db,spec)
    altered=packet(REPO, 1, "New text")
    with pytest.raises(PermissionError):
        execute(db,altered,client=Fake())
    inconsistent=deepcopy(spec)
    inconsistent["message"]="Tampered"
    with pytest.raises(ValueError):
        execute(db,inconsistent,client=Fake())

def test_unverifiable_side_effect_cannot_settle(tmp_path):
    db=str(tmp_path/"r.db")
    spec=packet(REPO, 1, "Original")
    approve(db,spec)
    class Invisible(Fake):
        def comments(self, repo, issue):
            return []
    f=Invisible()
    with pytest.raises(RuntimeError, match="POST_UNVERIFIED"):
        execute(db,spec,client=f)
    assert f.posts == 1
    with RealityStore(db) as store:
        assert store.db.execute("SELECT COUNT(*) FROM settlements").fetchone()[0] == 0

def test_bad_target_and_marker_rejected():
    with pytest.raises(ValueError):
        packet("not-a-repo",1,"Message")
    with pytest.raises(ValueError):
        packet(REPO,1,"test <!-- logistinfra-action: fake")

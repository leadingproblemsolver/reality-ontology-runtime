from reality_ontology.store import RealityStore


def test_invalidating_signal_excludes_dependent_decision(tmp_path):
    with RealityStore(tmp_path / "r.db") as s:
        goal = s.add_goal("validate market", "external evidence")
        decision = s.add_decision("target segment A", "5 replies")
        assumption = s.add_assumption("segment A has urgent pain", "market", 0.8, decision)
        s.add_signal("execution_outcome", "cohort-1", "0 replies from controlled cohort", -0.7, assumption)
        assert decision in s.invalidated_decision_ids()
        packet = s.context_packet(goal)
        assert decision in packet["excluded_invalid_decision_ids"]
        assert all(d["decision_id"] != decision for d in packet["active_decisions"])

import pytest
from conftest import valid_matrix, valid_post, valid_residual

from dialog_mcp import rules


def _post(**kw) -> rules.Post:
    data = valid_post(**kw)
    return rules.Post(
        body=data["body"],
        evidence=[rules.Evidence(**e) for e in data.get("evidence", [])],
        objections=[rules.Objection(**o) for o in data.get("objections", [])],
        clearances=[rules.Clearance(**c) for c in data.get("clearances", [])],
        priorities=data.get("priorities"),
        matrix=data.get("matrix"),
        residual=data.get("residual"),
    )


def test_valid_strict_post_passes():
    rules.validate_post(_post(), profile="strict", round_no=1, is_final_round=False)


def test_objection_without_retract_condition_is_rejected():
    post = _post(objections=[{"claim": "Das ist schlecht.", "reasoning": "Weil.", "retract_if": ""}])
    with pytest.raises(rules.RuleViolation) as exc:
        rules.validate_post(post, profile="strict", round_no=1, is_final_round=False)
    assert exc.value.field == "objections[].retract_if"
    assert "§1" in str(exc.value)


def test_round_one_without_objection_needs_two_clearances():
    post = _post(objections=[])
    with pytest.raises(rules.RuleViolation) as exc:
        rules.validate_post(post, profile="strict", round_no=1, is_final_round=False)
    assert exc.value.field == "objections"

    post = _post(
        objections=[],
        clearances=[
            {"field": "netzwerk", "reasoning": "reiner Offline-Betrieb", "retract_if": "ein Client aus dem Internet zugreift"},
            {"field": "plattform", "reasoning": "nur Linux-VM", "retract_if": "Windows-Clients den Dienst betreiben"},
        ],
    )
    rules.validate_post(post, profile="strict", round_no=1, is_final_round=False)


def test_two_clearances_must_cover_two_fields():
    post = _post(
        objections=[],
        clearances=[
            {"field": "netzwerk", "reasoning": "a", "retract_if": "x"},
            {"field": "netzwerk", "reasoning": "b", "retract_if": "y"},
        ],
    )
    with pytest.raises(rules.RuleViolation) as exc:
        rules.validate_post(post, profile="strict", round_no=1, is_final_round=False)
    assert exc.value.field == "clearances"


def test_round_three_needs_no_objection():
    rules.validate_post(_post(objections=[], residual=valid_residual()),
                        profile="strict", round_no=3, is_final_round=True)


def test_compliance_may_not_be_prioritised():
    post = _post(priorities={"dimensions": ["compliance"], "sacrifice": "nichts"})
    with pytest.raises(rules.RuleViolation) as exc:
        rules.validate_post(post, profile="strict", round_no=1, is_final_round=False)
    assert "nicht abwaegbar" in str(exc.value)


def test_priority_without_sacrifice_is_rejected():
    post = _post(priorities={"dimensions": ["robustheit"], "sacrifice": "   "})
    with pytest.raises(rules.RuleViolation) as exc:
        rules.validate_post(post, profile="strict", round_no=1, is_final_round=False)
    assert exc.value.field == "priorities.sacrifice"


def test_blocked_gate_needs_named_blockers():
    post = _post(matrix=valid_matrix(gate="blockiert"))
    with pytest.raises(rules.RuleViolation) as exc:
        rules.validate_post(post, profile="strict", round_no=1, is_final_round=False)
    assert exc.value.field == "matrix.compliance.blockers"


def test_final_round_requires_residual():
    with pytest.raises(rules.RuleViolation) as exc:
        rules.validate_post(_post(), profile="strict", round_no=3, is_final_round=True)
    assert exc.value.field == "residual"
    assert "§4" in str(exc.value)


def test_light_profile_only_needs_a_body():
    rules.validate_post(rules.Post(body="kurz"), profile="light", round_no=1, is_final_round=True)
    with pytest.raises(rules.RuleViolation):
        rules.validate_post(rules.Post(body="  "), profile="light", round_no=1, is_final_round=False)


def test_probe_without_evidence_is_rejected_in_strict():
    with pytest.raises(rules.RuleViolation) as exc:
        rules.validate_probe(rules.Probe(artifact="src/a.py:12"), profile="strict")
    assert exc.value.field == "evidence"


def _probe(artifact, *evidence):
    return rules.Probe(artifact=artifact, evidence=[rules.Evidence(*e) for e in evidence])


def test_convergence_requires_matching_artifacts():
    probes = {"a": _probe("src/a.py:12", ("src/a.py", "12")), "b": _probe("src/b.py:40", ("src/b.py", "40"))}
    assert "unterscheiden" in rules.convergence_blocked(probes)


def test_convergence_requires_evidence_contact():
    probes = {"a": _probe("src/a.py:12", ("src/a.py", "12")), "b": _probe("src/a.py:12")}
    assert "geteilter Prior" in rules.convergence_blocked(probes)


def test_convergence_requires_more_than_one_locator():
    same = ("src/a.py", "12")
    probes = {"a": _probe("src/a.py:12", same), "b": _probe("SRC/A.PY:12 ", same)}
    assert "dieselbe einzelne Stelle" in rules.convergence_blocked(probes)


def test_convergence_allowed_when_independent():
    probes = {
        "a": _probe("src/a.py:12", ("src/a.py", "12")),
        "b": _probe("src/a.py:12", ("src/a.py", "12"), ("tests/test_a.py", "30")),
    }
    assert rules.convergence_blocked(probes) is None

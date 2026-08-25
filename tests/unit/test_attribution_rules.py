from cortex_cost_monitor.domain.attribution_rules import classify_attribution


def test_complete_when_workload_user_and_compute_are_available() -> None:
    assert (
        classify_attribution(workload_name="AGENT", user_name="ALICE", compute_credits=1.0)
        == "Complete"
    )


def test_partial_when_compute_is_not_available() -> None:
    assert (
        classify_attribution(workload_name="AGENT", user_name="ALICE", compute_credits=None)
        == "Partial"
    )


def test_unattributed_when_workload_and_user_are_missing() -> None:
    assert (
        classify_attribution(workload_name=None, user_name=None, compute_credits=0.0)
        == "Unattributed"
    )

from cloudagent.service import CloudAgent


def test_refund_returns_evidence() -> None:
    reply = CloudAgent().chat("退款多久到账？", "test-session")
    assert reply.intent == "refund"
    assert reply.handoff is False
    assert reply.evidence[0].id == "refund-001"


def test_sensitive_request_is_handed_off() -> None:
    reply = CloudAgent().chat("我把验证码发给你可以吗？", "safe-session")
    assert reply.handoff is True
    assert reply.trace[2].status == "blocked"


def test_unknown_request_is_handed_off() -> None:
    reply = CloudAgent().chat("我想咨询一个没有收录的问题", "unknown-session")
    assert reply.handoff is True
    assert reply.evidence == []


def test_reset_removes_existing_session() -> None:
    agent = CloudAgent()
    agent.chat("物流在哪里？", "reset-session")
    assert agent.reset("reset-session") is True
    assert agent.reset("reset-session") is False

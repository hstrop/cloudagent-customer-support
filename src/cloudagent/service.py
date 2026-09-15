"""Deterministic support-agent orchestration used by the API and tests."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .models import ChatResponse, Evidence, TraceStep

SESSION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$")


@dataclass(frozen=True)
class KnowledgeItem:
    id: str
    title: str
    text: str
    keywords: tuple[str, ...]


@dataclass
class Session:
    turns: int = 0
    intents: list[str] = field(default_factory=list)


KNOWLEDGE = (
    KnowledgeItem(
        "refund-001",
        "退款处理时效",
        "已支付订单可在订单详情提交退款申请。原路退款通常在 3-7 个工作日内到账，具体以支付渠道处理进度为准。",
        ("退款", "退货", "取消订单", "到账"),
    ),
    KnowledgeItem(
        "delivery-001",
        "配送进度查询",
        "在订单详情可以查看配送节点；若超过承诺时间仍未更新，客服可以登记物流跟进单。",
        ("物流", "配送", "快递", "发货", "订单"),
    ),
    KnowledgeItem(
        "account-001",
        "账号安全与登录",
        "登录异常时请先使用官方页面找回密码。客服不会索要密码、验证码或完整支付信息。",
        ("登录", "账号", "密码", "验证码", "安全"),
    ),
    KnowledgeItem(
        "general-001",
        "人工服务时间",
        "在线客服工作时间为每天 09:00-22:00。复杂问题可以提交工单，系统会保留上下文供人工继续处理。",
        ("人工", "客服", "工单", "服务时间"),
    ),
)


class CloudAgent:
    """A small, observable support workflow with explicit policy boundaries."""

    def __init__(self) -> None:
        self.sessions: dict[str, Session] = {}

    @staticmethod
    def _validate_session(session_id: str) -> None:
        if not SESSION_ID.fullmatch(session_id):
            raise ValueError("session_id 仅允许字母、数字及 _ . : -，长度 1..64")

    @staticmethod
    def _intent(message: str) -> str:
        rules = (
            ("refund", ("退款", "退货", "取消订单")),
            ("delivery", ("物流", "配送", "快递", "发货")),
            ("account", ("登录", "账号", "密码", "验证码")),
        )
        for intent, keywords in rules:
            if any(keyword in message for keyword in keywords):
                return intent
        return "general"

    @staticmethod
    def _retrieve(message: str) -> list[Evidence]:
        ranked: list[tuple[int, KnowledgeItem]] = []
        for item in KNOWLEDGE:
            score = sum(1 for keyword in item.keywords if keyword in message)
            if score:
                ranked.append((score, item))
        ranked.sort(key=lambda pair: (-pair[0], pair[1].id))
        return [
            Evidence(
                id=item.id,
                title=item.title,
                snippet=item.text,
                score=round(score / max(1, len(item.keywords)), 2),
            )
            for score, item in ranked[:3]
        ]

    @staticmethod
    def _sensitive(message: str) -> bool:
        return any(token in message for token in ("身份证", "银行卡", "完整卡号", "验证码", "支付密码"))

    def chat(self, message: str, session_id: str = "demo-session") -> ChatResponse:
        cleaned = message.strip()
        if not cleaned:
            raise ValueError("message 不能为空")
        if len(cleaned) > 2000:
            raise ValueError("message 不能超过 2000 个字符")
        self._validate_session(session_id)
        session = self.sessions.setdefault(session_id, Session())
        intent = self._intent(cleaned)
        evidence = self._retrieve(cleaned)
        sensitive = self._sensitive(cleaned)
        session.turns += 1
        session.intents.append(intent)
        trace = [
            TraceStep(name="classify_intent", status="done", detail=f"intent={intent}"),
            TraceStep(name="retrieve_knowledge", status="done", detail=f"evidence={len(evidence)}"),
            TraceStep(name="policy_gate", status="blocked" if sensitive else "passed", detail="敏感信息不进入自动化回答" if sensitive else "未发现高风险字段"),
        ]
        if sensitive:
            answer = "为了保护账号安全，我不会处理密码、验证码或完整支付信息。请不要在聊天中发送这些内容，我已建议转人工处理。"
            handoff = True
        elif not evidence:
            answer = "我暂时没有找到足够的知识库证据。已为你保留会话上下文，建议转人工客服继续处理。"
            handoff = True
        else:
            answer = evidence[0].snippet + " 如果仍未解决，我可以继续为你登记人工跟进。"
            handoff = False
        trace.append(TraceStep(name="draft_response", status="handoff" if handoff else "done", detail="建议人工接管" if handoff else "回答包含知识库证据"))
        return ChatResponse(
            answer=answer,
            intent=intent,
            handoff=handoff,
            session_id=session_id,
            evidence=evidence,
            trace=trace,
        )

    def reset(self, session_id: str) -> bool:
        self._validate_session(session_id)
        return self.sessions.pop(session_id, None) is not None

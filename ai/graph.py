from __future__ import annotations

from langgraph.graph import StateGraph, END

from ai.state import (
    InterviewState,
    set_question,
    set_evaluation,
    need_follow_up,
    get_follow_up_question,
)
from ai.question_bank import get_bank
from ai.evaluator import evaluate_answer


def node_pick_question(st: InterviewState) -> InterviewState:
    bank = get_bank()
    asked = st.get("asked_question_ids", []) or []

    q = bank.pick_next(asked)

    if q.id not in asked:
        asked.append(q.id)
    st["asked_question_ids"] = asked

    return set_question(st, q.id, q.question, question_row=q.to_dict())


def node_evaluate(st: InterviewState) -> InterviewState:
    question_row = st.get("question_row")
    if not question_row:
        raise RuntimeError("question_row is missing. Run pick_question first.")

    ans = (st.get("last_user_answer_text") or "").strip()
    if not ans:
        ans = "잘 모르겠습니다"
        st["last_user_answer_text"] = ans

    rag_context = st.get("rag_context") or {}

    eval_json, _, _ = evaluate_answer(
        question_row=question_row,
        user_answer_text=ans,
        rag_context=rag_context,
    )

    st = set_evaluation(st, eval_json)
    return st


def node_follow_up(st: InterviewState) -> InterviewState:
    fq = get_follow_up_question(st)
    if not fq:
        fq = "방금 답변에서 가장 자신 없는 부분을 하나 골라 더 구체적으로 설명해보세요."

    base = st.get("current_question_id") or "unknown"
    follow_id = f"followup:{base}"

    st["question_row"] = {
        "id": follow_id,
        "question": fq,
        "answer": "",
        "difficulty": "follow_up",
        "topic": (st.get("last_eval_json") or {}).get("metadata_used", {}).get("topic", ""),
        "subcategory": (st.get("last_eval_json") or {}).get("metadata_used", {}).get("subcategory", ""),
        "difficulty_score": None,
        "tags": [],
        "code_example": "",
        "time_complexity": "",
        "space_complexity": "",
    }

    return set_question(st, follow_id, fq, question_row=st["question_row"])


def route_after_eval(st: InterviewState):
    return "follow_up" if need_follow_up(st, threshold=70) else "pick_question"


def build_start_graph():
    g = StateGraph(InterviewState)
    g.add_node("pick_question", node_pick_question)
    g.set_entry_point("pick_question")
    g.add_edge("pick_question", END)  # 질문 제시 후 사용자 입력 대기
    return g.compile()


def build_answer_graph():
    g = StateGraph(InterviewState)
    g.add_node("evaluate", node_evaluate)
    g.add_node("follow_up", node_follow_up)
    g.add_node("pick_question", node_pick_question)

    g.set_entry_point("evaluate")
    g.add_conditional_edges(
        "evaluate",
        route_after_eval,
        {"follow_up": "follow_up", "pick_question": "pick_question"},
    )
    g.add_edge("follow_up", END)
    g.add_edge("pick_question", END)
    return g.compile()
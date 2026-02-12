from __future__ import annotations

import json
from typing import Any, Dict, List

from app.config import AppConfig
from core.content_engine import ContentEngine
from integrations.llm_client import LLMClient


def _convert_question_for_ui(q: Dict[str, Any]) -> Dict[str, Any]:
    qid = q.get("id")
    source_type = q.get("type")
    prompt = q.get("prompt", "")

    if source_type == "mcq":
        opts = q.get("options", [])
        if not isinstance(opts, list):
            opts = []
        return {
            "type": "multiple_choice",
            "select_count": len(opts),
            "question": prompt,
            "answers": opts,
            "user_choice_index": 0,
            "qid": qid,
            "source_type": source_type,
        }

    if source_type == "slider":
        scale = q.get("scale", {})
        mx = 10
        if isinstance(scale, dict) and isinstance(scale.get("max"), (int, float)):
            mx = int(scale.get("max"))
        return {
            "type": "slider",
            "select_count": mx,
            "question": prompt,
            "user_choice_index": 0,
            "qid": qid,
            "source_type": source_type,
        }

    if source_type == "rating":
        return {
            "type": "rating",
            "select_count": 5,
            "question": prompt,
            "user_choice_index": 0,
            "qid": qid,
            "source_type": source_type,
        }

    placeholder = q.get("placeholder", "")
    if not isinstance(placeholder, str):
        placeholder = ""
    return {
        "type": "textinput",
        "question": prompt,
        "placeholder": placeholder,
        "user_input": "",
        "qid": qid,
        "source_type": source_type,
    }


def _convert_payload_for_ui(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    qs = payload.get("questions", [])
    items: List[Dict[str, Any]] = []
    if isinstance(qs, list):
        for q in qs:
            if isinstance(q, dict):
                items.append(_convert_question_for_ui(q))

    peq = payload.get("poly_extra_question")
    if isinstance(peq, dict):
        items.append(_convert_question_for_ui(peq))
    return items


def _create_engine() -> ContentEngine:
    cfg = AppConfig()
    llm = LLMClient(
        cfg.azure_endpoint,
        cfg.azure_api_key,
        cfg.azure_api_version,
        cfg.azure_deployment,
    )
    return ContentEngine(llm)


def generate_part1_ui_questions(
    education_status: str,
    poly_course: str | None = None,
) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    engine = _create_engine()
    payload = engine.gen_part1(education_status, poly_course)
    return _convert_payload_for_ui(payload), payload


def generate_part2_ui_questions(
    education_status: str,
    part1_answers: List[Dict[str, Any]],
) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    engine = _create_engine()
    payload = engine.gen_part2(education_status, part1_answers)
    return _convert_payload_for_ui(payload), payload


def generate_analysis(
    education_status: str,
    poly_path_choice: str | None,
    inferred_fields: List[str],
    part2_answers: List[Dict[str, Any]],
) -> Dict[str, Any]:
    engine = _create_engine()
    return engine.gen_analysis(
        education_status=education_status,
        poly_path_choice=poly_path_choice,
        inferred_fields=inferred_fields,
        part2_answers=part2_answers,
    )


def generate_gate_scene(
    option_name: str,
    work_path: bool,
    education_status: str | None = None,
    poly_path_choice: str | None = None,
) -> Dict[str, Any]:
    engine = _create_engine()
    return engine.gen_gate_scene(
        option_name=option_name,
        work_path=work_path,
        education_status=education_status,
        poly_path_choice=poly_path_choice,
    )


def main() -> None:
    part1_ui, _ = generate_part1_ui_questions("Poly", "IT")
    print("Part 1 UI questions:")
    print(json.dumps(part1_ui, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

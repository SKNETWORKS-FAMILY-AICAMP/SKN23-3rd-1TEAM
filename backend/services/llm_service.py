"""
File: llm_service.py
Author: 양창일
Created: 2026-02-15
Description: 실제로 AI를 실행하는 코드

Modification History:
- 2026-02-15: 초기 생성
"""

from backend.models.loader import model

def generate_text(prompt: str):
    return model(prompt)
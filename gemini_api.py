# python
# gemini_api_fixed.py
# .env 파일에서 GEMINI_API_KEY를 읽어와 genai 클라이언트를 생성하고 간단한 요청을 보냅니다.

from dotenv import load_dotenv
import os
from google import genai
from datetime import date
import json
from pathlib import Path

# .env 파일에서 환경 변수 불러오기
load_dotenv()

# 환경 변수 읽기
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("GEMINI_API_KEY가 설정되어 있지 않습니다. .env 파일을 만들거나 'export'로 설정하세요.")

# API 키를 명시적으로 전달하여 클라이언트 생성
client = genai.Client(api_key=api_key)

# Get current date
today = date.today()
current_date = today.strftime("%Y-%m-%d")

# --- 새로 추가된 메모리 관련 코드 ---
MEMORY_FILE = Path(".conversation_memory.json")
MAX_EXCHANGES = 5  # 보관할 최근 교환 수 (기본값)

def load_memory():
    """파일에서 메모리 불러오기; 없으면 빈 리스트 반환"""
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def save_memory(memory):
    """메모리를 파일에 저장"""
    try:
        MEMORY_FILE.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print("메모리 저장 중 오류:", e)

def add_exchange(memory, role, text):
    """메모리에 교환 추가(유저 또는 어시스턴트). 가장 오래된 항목 삭제로 길이 제한 유지"""
    memory.append({"role": role, "text": text})
    # 메모리는 '발언' 단위(사용자 또는 어시스턴트). 최대 MAX_EXCHANGES*2 항목을 넘기지 않도록 제한.
    max_items = MAX_EXCHANGES * 2
    if len(memory) > max_items:
        memory[:] = memory[-max_items:]
    return memory

def format_memory(memory):
    """메모리를 사람이 읽기 쉬운 텍스트로 변환"""
    if not memory:
        return ""
    lines = ["최근 대화(간단히):"]
    for item in memory:
        prefix = "사용자" if item["role"] == "user" else "어시스턴트"
        # 한 줄로 정리
        text = item["text"].replace("\n", " ")
        lines.append(f"{prefix}: {text}")
    return "\n".join(lines) + "\n\n"

# 메모리 로드
memory = load_memory()

# Ask the user for input, answer the question and keep doing that until the user says "exit"
while True:
    user_input = input("Ask a question (or type 'exit' to quit): ")
    if user_input.lower() == "exit":
        break

    # 사용자 입력을 메모리에 추가
    add_exchange(memory, "user", user_input)
    save_memory(memory)

    # 메모리를 포함해 모델에 보낼 프롬프트 구성
    context = format_memory(memory)
    # 현재 날짜를 시스템 지시사항으로 추가
    system_info = f"오늘 날짜: {current_date}\n"
    prompt = f"{system_info}\n{context}사용자: {user_input}\n어시스턴트:"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        answer = getattr(response, "text", None) or getattr(response, "outputs", None) or str(response)
    except Exception as e:
        print("API 호출 중 오류가 발생했습니다:", e)
        # 오류 상황에서도 루프 계속
        continue

    print("Answer:", answer)

    # 어시스턴트 응답을 메모리에 추가하고 저장
    add_exchange(memory, "assistant", answer)
    save_memory(memory)
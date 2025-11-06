# 간단한 실행 가능한 예제로 교체합니다.
# 이 스크립트는 .env에서 GEMINI_API_KEY를 읽고, 가능한 Gemini 클라이언트로 호출을 시도합니다.
# 클라이언트가 없으면 친절한 안내를 출력합니다.

import os
from dotenv import load_dotenv
from datetime import datetime

# .env 파일이 있으면 로드합니다 (선택적)
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("오류: GEMINI_API_KEY 환경 변수가 설정되어 있지 않습니다.")
    print("해결: 프로젝트 루트에 .env 파일을 만들고 GEMINI_API_KEY=여기에_키 를 추가하세요.")
    raise SystemExit(1)

# 현재 날짜/시간 문자열 생성 (로컬 타임)
current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 가능한 클라이언트들에 대해 순차 시도합니다.
try:
    # 일부 배포판/버전에서는 `from google import genai` 형태일 수 있습니다.
    from google import genai  # type: ignore
    client = genai.Client()  # 클라이언트가 환경변수로 키를 읽을 수 있을 때 동작
    # 변경: 날짜 컨텍스트를 포함한 contents
    contents = f"Current date: {current_date}\nQuestion: How many days until Christmas?"
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents
    )
    # 응답 객체가 .text 속성을 가지면 출력, 아니면 전체 객체를 출력
    print(getattr(response, "text", response))
except Exception:
    # 대체로 최신 패키지명은 google.generativeai 일 수 있습니다.
    try:
        import google.generativeai as generativeai  # type: ignore
        generativeai.configure(api_key=API_KEY)
        # 변경: 날짜 컨텍스트를 포함한 프롬프트
        prompt = f"Current date: {current_date}\nExplain how AI works in a few words"
        # generate_text 또는 generate 호출 방식은 버전마다 다릅니다.
        # 아래는 흔한 패턴을 시도하고 실패 시 전체 객체를 출력합니다.
        try:
            resp = generativeai.generate_text(model="gemini-2.5-flash", prompt=prompt)
            # 응답이 dict 형태면 후보 텍스트를 찾아 출력
            if isinstance(resp, dict) and "candidates" in resp and resp["candidates"]:
                print(resp["candidates"][0].get("output") or resp["candidates"][0])
            else:
                print(getattr(resp, "text", resp))
        except Exception:
            # 다른 API 네이밍(예: generate, text.generate 등)을 시도
            try:
                resp2 = generativeai.generate(model="gemini-2.5-flash", prompt=prompt)
                print(getattr(resp2, "text", resp2))
            except Exception:
                print("클라이언트 호출에 실패했습니다. 설치된 google.generativeai의 사용법을 확인하세요.")
                raise
    except Exception:
        print("Gemini 클라이언트 라이브러리가 발견되지 않거나 초기화에 실패했습니다.")
        print("설치 및 사용 예시:")
        print("  pip install google-generativeai")
        print("그리고 사용 중인 라이브러리 문서를 확인하세요.")
        raise
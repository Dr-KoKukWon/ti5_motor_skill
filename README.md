# ti5_motor_skill

TI5 humanoid robot motor control AI agent — 3가지 방식으로 사용 가능.

## 구조

```
ti5_motor_skill/
├── AGENTS.md                       # Method 1: Claude Code 네이티브
├── agents/
│   └── ti5-motor.md                # Method 2: OMC 커스텀 에이전트
├── ti5_motor_agent/                # Method 3: Agent SDK 독립 앱
│   ├── main.py                     # CLI 엔트리포인트
│   ├── agent.py                    # 에이전트 코어 (10개 도구)
│   ├── system_prompt.py            # 도메인 지식 시스템 프롬프트
│   └── tools/
│       ├── can_control.py          # CAN 버스 제어 도구
│       ├── test_runner.py          # SIL/HIL 테스트 실행 도구
│       ├── doc_search.py           # 프로젝트 문서 검색 도구
│       └── web_search.py           # GitHub/웹 검색 도구
├── knowledge/                      # 공유 지식 베이스
│   ├── encoder_settings.md         # 엔코더 설정 (ISSUE-017)
│   ├── init_sequence.md            # 초기화 시퀀스
│   ├── sil_hil_testing.md          # SIL/HIL 테스트 방법
│   ├── cmd_codes.md                # CAN CMD 코드 레퍼런스
│   └── references.md               # 외부 참조 (GitHub, 매뉴얼)
├── install.sh                      # 설치 스크립트
└── requirements.txt                # Python 의존성
```

## 설치

```bash
git clone https://github.com/Dr-KoKukWon/ti5_motor_skill.git
cd ti5_motor_skill
bash install.sh ~/test-ti5-kkw
```

## 사용법

### Method 1 — Claude Code (자동 로드)

```bash
cd ~/test-ti5-kkw && claude
# AGENTS.md가 자동으로 로드되어 모터 도메인 지식 적용
```

### Method 2 — OMC 커스텀 에이전트

Claude Code 내에서:
```
Agent({ subagent_type: "ti5-motor", prompt: "모터 16번 상태 확인" })
```

### Method 3 — 독립 Agent SDK 앱

```bash
export ANTHROPIC_API_KEY='sk-ant-...'
export TI5_PROJECT_ROOT=~/test-ti5-kkw

# 대화형 모드
python3 -m ti5_motor_agent

# 단일 쿼리
python3 -m ti5_motor_agent "모터 16번 엔코더 5도 이동 카운트 계산"
```

## 에이전트 도구 (Method 3)

| 도구 | 설명 |
|------|------|
| `can_open` | CAN 버스 열기 (CH0=왼팔, CH1=오른팔) |
| `can_close` | CAN 버스 닫기 |
| `can_send_command` | 모터에 CAN 명령 전송 |
| `can_read_register` | 모터 레지스터 읽기 |
| `run_sil_test` | SIL 테스트 실행 (하드웨어 불필요) |
| `run_hil_test` | HIL 테스트 실행 (USB-CAN + 모터 필요) |
| `search_docs` | 프로젝트 문서 검색 |
| `search_github` | ti5robot GitHub 레포 검색 |
| `search_web` | 웹 검색 (TI5 관련 정보) |
| `convert_units` | 단위 변환 (degrees↔counts↔speed) |

## 핵심 도메인 지식

- **엔코더 스케일**: CAN Position register = 262,144 cnt/rev (cmd 8/30), Out position = gear_ratio × 65,536
- **초기화**: Open → Status(10) → Fault(11) → Enable(1) → VelLimit(36/37) → Cmd → Disable(2) → Close
- **안전 한계**: Position ±716°, Speed ±1031°/s, Current ±40A
- **CAN 채널**: CH0=왼팔(16-22), CH1=오른팔(23-29)
- **기어비**: 어깨=121, 팔꿈치/손목=101

## 추가 예정

- [ ] 파라미터 튜닝 방법 (실험 후 추가)
- [ ] 공식 데이터시트/매뉴얼 PDF 포함

## 라이선스

MIT

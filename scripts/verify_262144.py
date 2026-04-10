#!/usr/bin/env python3
"""
verify_262144.py — CAN Position register 262,144 cnt/rev 검증

사용법:
    이 스크립트는 test-ti5-kkw 프로젝트의 experiments/ 디렉토리에서 실행합니다.

    # 설치 (test-ti5-kkw 프로젝트에 복사)
    cp scripts/verify_262144.py ~/test-ti5-kkw/experiments/axis-19/verify_262144.py

    # 또는 심볼릭 링크
    ln -s $(pwd)/scripts/verify_262144.py ~/test-ti5-kkw/experiments/axis-19/verify_262144.py

    # 실행
    cd ~/test-ti5-kkw/experiments/axis-19
    python3 verify_262144.py                      # CAN ID 19, 5도
    python3 verify_262144.py --motor-id 20        # L_WRIST_Y
    python3 verify_262144.py --motor-id 26 --can-index 1  # R_ELBOW (CH1)
    python3 verify_262144.py --angle 3 --wait     # 3도, 각도기 대기

검증 대상:
    가설 A (universal):  Position = 262,144 cnt/rev (gear_ratio 무관)
    가설 B (gear_dep):   Position = gear_ratio × 65,536 cnt/rev

    기존 결과: CAN ID 16 (gear_ratio=121) → 가설 A 확정
    이 스크립트: CAN ID 19 (gear_ratio=101) → 가설 A/B 판별

상세 코드: test-ti5-kkw/experiments/axis-19/verify_262144.py
"""

print("이 스크립트는 test-ti5-kkw 프로젝트에서 실행해야 합니다.")
print("  cp scripts/verify_262144.py ~/test-ti5-kkw/experiments/axis-19/")
print("  cd ~/test-ti5-kkw/experiments/axis-19 && python3 verify_262144.py")

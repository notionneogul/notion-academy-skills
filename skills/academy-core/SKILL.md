---
name: academy-core
description: 학원 관리 PRO 스킬들이 공유하는 규칙 문서 보관소. 직접 호출하지 말 것. 읽기 전용 3개(academy-setup, academy-insight, academy-doctor)와 쓰기 7개(academy-attendance, academy-homework, academy-exam, academy-counsel, academy-enroll, academy-tuition, academy-message)와 발송 1개(academy-send), 총 11개 스킬이 references 폴더의 파일을 상대 경로로 읽어 쓴다.
---

# 학원 스킬 공유 규칙

이 스킬은 **직접 호출하지 않는다.** 다른 `academy-*` 스킬이 읽는 문서만 담는다.

## 파일

| 파일 | 내용 | 언제 읽나 |
|---|---|---|
| `references/db-map.md` | 데이터베이스 15개의 스키마 지문, `~/.academy/config.json` 읽는 법, **DB별 쓰기 불가 속성**(formula·rollup·button) | 노션에 접근하는 모든 스킬이 시작할 때 |
| `references/query-limits.md` | 노션 쿼리 도구의 제약. 무엇을 SQL 로 할 수 없고 무엇을 클로드가 계산해야 하는지 | 노션을 조회하는 모든 스킬이 조회를 시작하기 전에 |
| `references/domain-rules.md` | 정합성 규칙. 어기면 데이터가 깨진다 | 쓰기 전, 그리고 점검할 때 |
| `references/completeness-checks.md` | 누락 확인 규칙. 무엇을 되물을지 | 쓰기 전 |
| `references/write-safety.md` | 쓰기 경계. 무엇이 자율이고 무엇이 승인 대상인지 | 쓰기 전 |
| `references/write-gate.md` | 쓰기 관문 7단계. 되물음 → 사전 검증(4종) → 미리보기 → 승인 → 쓰기 → 결과 보고 → 남은 항목 확인. 되돌리기의 생성분/수정분 두 갈래도 여기 | 일곱 쓰기 스킬이 쓰기를 시작하기 전 |
| `references/routing.md` | 한 발화가 여러 DB에 걸칠 때의 처리 순서와 끝맺음 규칙 | 쓰기 스킬이 자기 몫을 마쳤을 때 |
| `references/name-resolution.md` | 사람 이름·클래스명을 relation에 넣을 과목 페이지 uuid로 바꾸는 절차 | 쓰기 스킬이 대상을 특정할 때 |

## 다른 스킬에서 읽는 법

각 스킬은 자기 base 디렉토리 기준 상대 경로로 읽는다.

```
../academy-core/references/domain-rules.md
```

읽지 않고 추측으로 진행하지 않는다. 이 규칙 파일들은 실제 운영에서 데이터가 깨진 사례와 쿼리 도구를 직접 돌려 확인한 실측을 근거로 만들어졌다.

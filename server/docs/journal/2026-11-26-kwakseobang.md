# 작업 일지 — 2026-11-26

단계: **서버 초기 셋팅**

## 스텝 1. 테스트 DB를 운영 DB와 같은 PostgreSQL로 맞춘다

**요청 (사용자)**: "테스트 DB도 그냥 운영 DB랑 맞추기로 했어", "그리고 postgresql임"

**결정 (사용자)**: 테스트 DB는 운영 DB와 맞춘다. DB는 PostgreSQL이다. 2026-11-23 일지 스텝 27의 "테스트는 H2"를 대신한다.

**한 일 (AI)**:
1. `@IntegrationTest`와 `@E2ETest`가 `PostgresTestConfig`의 PostgreSQL 컨테이너를 쓰게 했다.
2. `application-test.yml`의 H2 접속 설정을 지우고 H2 의존성을 뺐다. `spring-boot-testcontainers`와 `testcontainers-postgresql`을 더했다.
3. 임시 테스트로 `@IntegrationTest`가 PostgreSQL 17.12에 연결되는 것을 확인하고 그 테스트를 지웠다. `./gradlew check --rerun-tasks`가 통과했다.

**결정 (AI)** (확인이 필요하다):
- 연결 방식은 Testcontainers다. ADR-0002의 요구 15가 CI에 정한 방식이고, 로컬 개발 DB의 데이터와 나뉜다.
- 이미지는 `compose.yaml`과 같은 `postgres:17`이다.
- 스키마는 전처럼 `ddl-auto=create-drop`이고 Flyway는 끈다. 마이그레이션 파일이 아직 없다.

**관찰**:
- `@IntegrationTest`나 `@E2ETest`를 쓰는 테스트가 아직 없어서 `check`만으로는 DB 연결을 확인하지 못한다.
- 이제 이 두 테스트를 실행하려면 Docker가 켜져 있어야 한다.

**남은 일**:
- ADR-0002와 ADR-0004를 고친다(`setting/server-harness`).
- DB 비우기(ADR-0004의 E5)를 테스트 기반에 붙인다.
- 사용자가 확인한 뒤 push하고 PR #4의 설명을 고친다.

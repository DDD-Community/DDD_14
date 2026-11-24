# 작업 일지 — 2026-11-23

단계: **초기 셋팅 (슬라이스 밖)**

## 스텝 1. 초기 셋팅: 빌드

**요청 (사용자)**: "초기 셋팅 하자. 공통 에러 코드, 빌드 셋팅 등 공통 셋팅." 이어서 "MySQL은 빼 주고, yml로 갈 거고, 초기 셋팅은 메멘토를 따르고, 응답 코드는 어떰처럼 하면 될 듯." JDK는 "너가 올려라", "Liberica로 할 거고 최근 보안 이슈를 잡은 버전".

**결정 (사용자)**:
- `git config harness.handle`은 `kwakseobang`이다.
- Spring Boot는 4.1.3이다(ADR-0002의 "4.0이나 4.1 중 어느 줄").
- 그룹 ID와 기본 패키지는 `com.ttadak`이다.
- 초기 셋팅은 `setting/server-init` 브랜치에서 한다. 하네스 파일(`.claude`, `docs`, `scripts`, `AGENTS.md`)의 커밋은 사용자가 따로 한다.
- 스텝 순서는 빌드, 공통 코드, CI다.
- MySQL은 뺀다. 운영 DB의 드라이버와 Flyway 모듈은 4차 회의(11/24)에서 DB를 정한 뒤 더한다.
- 설정 파일은 yml이다.
- 초기 셋팅의 모양은 메멘토(`kwakseobang/memento-backend`)를 따른다. 오류 응답은 AuDDum(`support/error`)을 따른다(다음 스텝에서 한다).
- JDK는 Liberica 25.0.5.1 이상이다.

**한 일 (AI)**:
1. 하네스 문서(`docs/README.md`, ADR-0002, 0003, 0004, 0005, 0006)를 읽고, `git config harness.handle`을 `kwakseobang`으로 설정했다.
2. JDK를 확인했다. Liberica 25는 25.0.5.0.3이라 ADR-0002의 요구 1(25.0.5.1 이상)에 못 미쳤다. brew cask(`liberica-jdk25`)도 25.0.5.0.3이고 `temurin@25`는 `sudo` 비밀번호가 필요해 막혔다. BellSoft의 25.0.5.1+5 tar.gz를 받아 SHA-1을 확인하고 `~/Library/Java/JavaVirtualMachines/liberica-25.0.5.1.jdk`에 풀었다. `java_home`이 인식하도록 `Contents/Home`과 `Info.plist`를 만들었다.
3. 메멘토와 AuDDum의 빌드 파일, yml, 오류 처리 코드를 읽고 기준으로 삼았다.
4. 브랜치 `setting/server-init`을 만들었다.
5. 빌드 파일을 만들었다: `settings.gradle.kts`, `build.gradle.kts`, Gradle wrapper(9.7.1, AuDDum에서 복사), `.editorconfig`, `.gitattributes`, `.gitignore`에 빌드와 비밀 값 항목.
6. 포매터를 만들었다: `config/spotless/eclipse-formatter.xml`. 임시 샘플 클래스로 4칸 공백과 줄바꿈 동작을 확인하고 지웠다.
7. 설정을 만들었다: `application.yml`, `application-local.yml`(H2, `ddl-auto=update`, Flyway 끔), `application-prod.yml`(`validate`, Flyway 켬, DB 정보는 환경 변수), 테스트용 `application-test.yml`.
8. 앱 진입점 `TtadakApplication`을 만들었다.
9. 확인: `./gradlew build`(JDK 25.0.5.1)가 통과했다. `bootRun`이 `local` 프로필로 2.2초에 시작했다. 테스트는 아직 없다.

**결정 (AI)** (확인이 필요하다):
- 빌드 파일은 Kotlin DSL이고, 프로젝트 이름은 `ttadak-server`다. 메멘토와 AuDDum이 같은 방식이다.
- 의존성은 ADR-0002가 정한 것만 넣었다(webmvc, security, validation, data-jpa, flyway starter, H2, Lombok, ArchUnit 1.5.1, Testcontainers 코어). Actuator, springdoc, devtools, h2console, docker-compose는 ADR-0002의 "정하지 않은 것"이거나 ADR에 없어서 뺐다. Testcontainers의 DB 모듈은 DB가 정해지면 더한다.
- 프로필은 `local`(기본), `test`, `prod`다. ADR-0002는 CI와 운영의 설정이 같아서 `prod` 하나로 두었다. 기본 프로필은 메멘토처럼 `local`이다.
- Spotless는 Eclipse 포매터이고, 주석과 줄바꿈 합치기는 건드리지 않는다. ADR-0006의 C2("매개변수가 2개 이상이면 한 줄에 하나씩")는 Eclipse에 "둘 이상이면 항상"이 없고, 강제(49)를 켜면 매개변수가 하나여도 줄바꿈해서(`main(\n String[] args)`) 쓰지 않았다. 대신 "줄을 나눌 때는 한 줄에 하나씩"(48)이라서 C2는 지금 리뷰가 확인한다. C2의 상태는 "초기 셋팅 전"으로 남겨 둔다.
- 운영의 Flyway와 `validate`를 확인하는 테스트(ADR-0002의 요구 7)는 `@Covers`와 테스트 기반 클래스가 생기는 다음 스텝(공통 코드)으로 미뤘다.

**관찰**:
- brew의 `liberica-jdk25` cask는 BellSoft 최신보다 늦다. 보안 릴리스를 맞출 때는 BellSoft API로 확인한다.
- 설치 프로그램이 `sudo`를 요구하면 이 세션에서는 비밀번호를 받을 수 없다. tar.gz를 사용자 폴더에 푸는 길이 있다.
- `check.sh`는 `./gradlew test`만 실행해서 `spotlessCheck`를 돌리지 않는다.

**남은 일**:
- `check.sh`가 `./gradlew check`로 `spotlessCheck`까지 돌리도록 바꾼다(사용자 확인 필요, 하네스 스크립트).
- 스텝 2 공통 코드: 오류 응답 ADR(예: ADR-0007) 초안을 AuDDum 방식으로 쓰고 승인을 받는다. 승인 뒤에 `BaseEntity`와 `EntityStatus`, 예외와 오류 코드, 응답 DTO 기준 코드, `@Covers`, 테스트 기반 클래스, Fixture, 동시성 도우미, 운영 설정을 확인하는 테스트를 만든다.
- 스텝 3 CI: 워크플로(`.github/`는 루트라서 사용자의 허락이 필요하다).
- 4차 회의(11/24) 뒤: 운영 DB의 드라이버와 Flyway 모듈, Testcontainers의 DB 모듈, ADR-0002의 5, 6, 7, 15번을 고친다.

## 스텝 2. 코드와 설정의 주석에서 ADR 언급을 뺀다

**요청 (사용자)**: "그 주석에 ADR 이런 건 안 써도 된다."

**한 일 (AI)**:
1. `build.gradle.kts`, `application-local.yml`, `application-prod.yml`, `config/spotless/eclipse-formatter.xml`의 주석에서 ADR 번호와 요구 번호(C1, C2)를 뺐다. 설명은 남겼다.
2. 앞으로 코드와 설정의 주석에 ADR을 쓰지 않는 규칙을 메모리에 남겼다.

**관찰**:
- 스텝 1의 일지에는 ADR 번호가 있다. 일지와 문서는 ADR을 가리켜도 되고, 코드와 설정의 주석만 뺐다.

**남은 일**:
- 스텝 1의 남은 일과 같다.

## 스텝 3. 공통 코드의 시작: check.sh와 오류 응답 ADR 초안

**요청 (사용자)**: "공통 ㄱㄱ" (앞서 `check.sh`를 `./gradlew check`로 바꿔도 되는지 묻고, 괜찮으면 오류 응답 ADR 초안부터 쓰겠다고 했다.)

**결정 (사용자)**:
- 오류 응답은 AuDDum의 방식을 따른다(스텝 1).
- `check.sh`를 `./gradlew check`로 바꾸는 것은 "공통 ㄱㄱ"를 허락으로 읽었다. 틀렸으면 되돌린다.

**한 일 (AI)**:
1. `scripts/check.sh`가 `./gradlew test` 대신 `./gradlew check`를 실행하게 바꿨다(`spotlessCheck` 포함). 이 스크립트는 아직 커밋되지 않은 하네스 파일이라 이 스텝의 커밋에는 넣지 않았다. 하네스를 커밋할 때 같이 들어간다. `check.sh`를 인자와 함께 부르는 곳은 없었다(`check`는 `--tests`를 받지 못한다).
2. 오류 응답 ADR 초안 `docs/adr/0007-오류-응답.md`를 썼다(상태: 제안). AuDDum의 `support/error`(ProblemDetail에 `code`와 `errors`, `ErrorCode` enum, 전역 예외 처리기)를 요구 20개로 옮겼다. `docs_lint`를 통과했다.

**결정 (AI)** (확인이 필요하다):
- 예외 이름은 `TtadakException`, 공통 오류 코드는 `DefaultErrorCode`의 다섯 개(`MALFORMED_REQUEST`, `VALIDATION_FAILED`, `UNAUTHENTICATED`, `FORBIDDEN`, `INTERNAL_ERROR`)다. 상태와 메시지와 로그 수준은 AuDDum의 값이다.
- 오류 코드에 로그 수준을 두는 것은 ADR-0006의 "정하지 않은 것" 3번(로그 레벨의 구분)과 겹쳐서 ADR-0007의 "정하지 않은 것"에 올렸다.
- 도메인 오류 코드가 Spring의 `HttpStatus`를 쓰면 ADR-0003의 요구 2(도메인 계층은 다른 계층을 참조하지 않는다)와 부딪힐 수 있다. 패키지와 함께 "정하지 않은 것" 1번에 올렸고, 첫 코드를 쓸 때 정한다.
- 인증 필터 단계의 401과 403, 성공 응답과 페이지 처리의 형식, 오류 코드 문서 생성은 이 ADR에서 정하지 않았다.
- 메멘토의 `ApiResponse`(성공과 실패를 감싸는 형식)는 "버린 대안"에 올렸다. 사용자가 AuDDum을 따르자고 해서 버렸다.

**관찰**:
- docs-lint는 한 줄에 `반드시`와 `절대`를 섞으면 막는다. 요구를 둘로 나눠서 풀었다.

**남은 일**:
- 사용자가 ADR-0007을 확인하고 승인하면(상태의 줄을 `승인`으로) 공통 코드를 만든다: `ErrorCode`와 `DefaultErrorCode`, `TtadakException`, 전역 예외 처리기, `BaseEntity`와 `EntityStatus`, 응답 DTO 기준 코드, `@Covers`, 테스트 기반 클래스와 Fixture, 동시성 도우미, 운영 설정을 확인하는 테스트.

## 스텝 4. 오류 응답 ADR-0007의 수정과 승인

**요청 (사용자)**: "근데 오류 코드는 그냥 하나로 하자 메멘토처럼", 공통 접두어를 메멘토처럼 붙일지 물은 데 "응 그렇게 해봐", ADR을 보여 준 뒤 "그래".

**결정 (사용자)**:
- 오류 응답의 모양은 AuDDum(ProblemDetail)이다. 오류 코드는 메멘토처럼 enum 하나에 모은다.
- 공통 오류 코드의 이름은 메멘토처럼 접두어(`DEFAULT_`)를 붙인다.
- ADR-0007을 승인한다.
- `check.sh`를 `./gradlew check`로 바꾸는 것은 스텝 3에서 "공통 ㄱㄱ"로 읽었다. 그대로 두고 사용자가 이의가 없었다.
- 커밋은 사용자에게 확인을 받고 한다. `.claude/settings.json`의 `ask`에 `git commit`을 더했다(스텝 3 뒤).

**한 일 (AI)**:
1. 메멘토의 `ApiResponse`와 `ErrorType`, `GlobalExceptionHandler`를 읽고 AuDDum과 비교해 보였다. 클라이언트에는 기대하는 에러 형식이 아직 없었다.
2. ADR-0007을 고쳤다: `ErrorCode` 인터페이스와 `DefaultErrorCode`와 도메인별 enum을 없애고 `ErrorCode` enum 하나로 바꿨다. 기능의 코드는 `<기능>_<사유>`로 적고 기능별로 묶는다. 요구는 21개다. "버린 대안"에 메멘토의 `ApiResponse`와 AuDDum의 도메인별 enum을 올렸다.
3. 공통 오류 코드 다섯 개의 이름에 `DEFAULT_`를 붙였다.
4. 원문을 브라우저로 보인 뒤 사용자의 승인을 받고 상태의 줄을 `승인`으로 바꿨다.

**결정 (AI)** (확인이 필요하다):
- 접두어만 붙이고 이름은 AuDDum의 것을 그대로 썼다(`DEFAULT_MALFORMED_REQUEST`, `DEFAULT_VALIDATION_FAILED`, `DEFAULT_UNAUTHENTICATED`, `DEFAULT_FORBIDDEN`, `DEFAULT_INTERNAL_ERROR`). 메멘토의 `DEFAULT_BAD_REQUEST`는 우리의 `MALFORMED_REQUEST`와 `VALIDATION_FAILED` 두 개로 나뉘어서 이름까지 맞추지 않았다.
- "응 그렇게 해봐"는 접두어를 붙이라는 뜻으로 읽었다. ADR의 승인은 따로 "그래"를 받았다.

**관찰**:
- 사용자가 승인 전에 문서를 커밋하는 것을 막고 싶어 했다. 훅을 더하는 대신 `git commit`을 `ask`로 옮겼다. 이 방식은 확인창에 커밋 명령만 보이므로 제가 먼저 무엇을 커밋하는지 말해야 한다.
- 승인해야 하는 문서는 쓴 직후에 원문을 열어 보이고, 승인을 받은 뒤에 커밋한다. 이번에는 스텝 3에서 이 순서를 어겼다.

**남은 일**:
- 공통 코드를 만든다: `ErrorCode`, `TtadakException`, 전역 예외 처리기, `BaseEntity`와 `EntityStatus`, `TimeConfig`와 `JpaAuditingConfig`, 서비스 스테레오타입, 응답 DTO 기준 코드, `@Covers`, 테스트 기반 클래스와 Fixture, 동시성 도우미, 운영 설정 테스트(AuDDum의 `support` 기준).

## 스텝 5. 주석 포맷 켜기

**요청 (사용자)**: "주석 포맷팅도 맞춰라."

**한 일 (AI)**:
1. `config/spotless/eclipse-formatter.xml`에서 javadoc, 블록, 줄 주석의 포맷을 켰다(스텝 1에서는 꺼 두었다). 한 줄 길이는 130자다.
2. 임시 샘플로 확인한 뒤 샘플을 지웠다. 여러 칸 공백이 한 칸이 되고, `//` 뒤 공백이 정리된다. 줄바꿈과 문장은 그대로 둔다.

**결정 (AI)** (확인이 필요하다):
- "주석 포맷팅을 맞춘다"를 Spotless의 주석 포맷을 켜는 것으로 읽었다. 주석의 문장을 합치는 것(줄 합치기)은 켜지 않았다. 다른 뜻(예: 주석의 형식 규칙)이었으면 알려 달라.

**남은 일**:
- 스텝 4의 남은 일과 같다.

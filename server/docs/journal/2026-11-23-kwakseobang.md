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

## 스텝 6. 공통 코드 1: 오류 응답

**요청 (사용자)**: "응" (공통 코드를 AuDDum 기준으로 만드는 것. 만들기 전에 맞출 곳을 정리해 보인 뒤 시작했다.)

**결정 (사용자)**:
- `BaseEntity`의 삭제는 `delete(LocalDateTime now)`로 `deletedAt`을 둔다(스텝 7에서 만든다).
- AuDDum의 서비스 스테레오타입(`@WebApi`, `@CommandService`, `@QueryService`)은 지금은 가져오지 않는다.
- 패키지 구조(기능 먼저인지 계층 먼저인지)는 지금 정하지 않는다. 의존 방향 ArchUnit은 정한 뒤에 만든다.
- 공통 코드의 스텝 순서는 오류 응답, JPA 기본, 테스트 기반, 기준 코드다.

**한 일 (AI)**:
1. ADR-0007대로 `com.ttadak.support.error`에 `ErrorCode`(공통 오류 코드 다섯 개), `TtadakException`, `FieldViolation`, `GlobalExceptionHandler`를 만들었다. 전역 예외 처리기는 AuDDum의 것을 `ErrorCode` 하나에 맞게 고쳤다.
2. 표현 계층 테스트의 기반 `WebApiTestSupport`(모든 요청을 허용하는 시큐리티 설정)와 `ErrorResponseTest`(15개)를 만들었다. 확인하는 것: problem+json, `code`와 `status`와 `detail`, `instance`, `errors`의 유무, 검증 실패의 필드별 `errors`, 깨진 JSON과 타입 불일치의 `DEFAULT_MALFORMED_REQUEST`, 처리하지 못한 예외의 `DEFAULT_INTERNAL_ERROR`와 내부 메시지 비노출.
3. 포매터에 enum 상수를 한 줄에 하나씩 쓰는 설정을 더했다. 설정 전에는 상수가 한 줄에 이어 붙어 망가졌다.
4. 처리기가 내부 예외 메시지를 응답에 담도록 일부러 깨 보니 테스트 2개가 실패했고, 복구하니 15개가 통과했다.

**결정 (AI)** (확인이 필요하다):
- 공통 오류 코드의 로그 수준과 메시지는 AuDDum의 값을 그대로 썼다(ADR-0007의 표).
- 테스트 이름은 한글 문장에 밑줄을 넣었다(AuDDum과 같다). `@Covers`는 아직 없고 ADR의 요구에는 AC와 R이 없어서 달지 않았다.
- 테스트의 시큐리티 설정은 인증 방식이 정해지지 않아(ACC-03) 모든 요청을 허용한다.

**관찰**:
- 구현을 먼저 쓰고 테스트를 나중에 썼다. ADR-0004의 F4.1(구현 전에 red를 확인한다)을 어겼다. 초기 셋팅이라 슬라이스의 `test-author` 흐름이 없었기 때문이고, 대신 구현을 일부러 깨서 테스트가 실패하는 것을 확인했다.
- Spring Security 7에서는 `HttpSecurity` 빈을 쓰려면 설정 클래스에 `@EnableWebSecurity`가 필요하다.
- 전역 예외 처리기의 `@ExceptionHandler(Exception.class)`는 메서드 보안이 던지는 `AccessDeniedException`과 `AuthenticationException`도 500으로 바꾼다. 인증을 만들 때(ADR-0007의 "정하지 않은 것" 3번) 같이 다뤄야 한다.
- Eclipse 포매터는 enum 상수와 record의 줄바꿈을 기본 설정으로 두면 코드를 망가뜨릴 수 있다. 새 모양의 코드를 처음 넣을 때 `spotlessApply` 결과를 읽어 본다.

**남은 일**:
- 스텝 7 JPA 기본: `BaseEntity`와 `EntityStatus`(`delete(LocalDateTime now)`), `TimeConfig`, `JpaAuditingConfig`, 엔티티 규칙 ArchUnit(C4, C5).
- 스텝 8 테스트 기반: `@Covers`, 데이터와 통합 테스트 기반 클래스, 동시성 도우미, 운영 설정 테스트.
- 스텝 9 기준 코드: 엔티티와 응답 DTO 예시(C6, C7), Fixture. 패키지 구조를 정하면 의존 방향 ArchUnit.

## 스텝 7. 포매터의 줄바꿈과 enum 모양을 사용자의 모양에 맞춘다

**요청 (사용자)**: 줄바꿈할 때 `(` 뒤에서 한 줄에 하나씩 쓰고 `)`는 다음 줄에 둔다. enum 상수는 `(`를 세로로 맞춰 정렬한다. `TtadakException`의 private 생성자는 둔다. 미완성 생성자의 줄은 지운다.

**한 일 (AI)**:
1. `config/spotless/eclipse-formatter.xml`에 메서드와 record의 괄호 위치(`separate_lines_if_wrapped`)와 `@formatter:off/on` 태그를 켰다. 임시 복사본에서 짧은 시그니처는 그대로 두고 130자를 넘는 시그니처는 사용자의 모양으로 나뉘는 것을 확인했다.
2. `ErrorCode`의 상수 구간을 `// @formatter:off` ... `// @formatter:on`으로 감싸고 사용자의 정렬 모양으로 맞췄다.
3. `./gradlew spotlessApply`를 돌려 `FieldViolation`과 `GlobalExceptionHandler`가 새 모양이 된 것을 확인했다. `check.sh`가 통과했다.

**결정 (AI)** (확인이 필요하다):
- Eclipse에는 enum 상수를 `(` 기준으로 정렬하는 옵션이 없어서 상수 구간에는 포매터를 끈다. 상수를 더할 때는 직접 정렬한다.
- "둘 이상이면 항상 줄바꿈"(ADR-0006의 C2)은 여전히 포매터가 강제하지 못한다. 줄바꿈은 사용자가 하고 포매터는 그 모양을 유지한다. C2는 리뷰가 확인한다.

**관찰**:
- 포매터가 사용자가 IDE에서 고치던 파일(미완성 코드)을 건드렸다. 사용자의 파일이 편집 중일 수 있을 때는 `spotlessApply` 전에 백업하고, 바뀌었으면 되돌린다.
- 이 스텝으로 스텝 6의 "남은 일"에 적은 스텝 번호가 하나씩 밀린다(JPA 기본은 스텝 8).

**남은 일**:
- 스텝 6의 남은 일과 같다(JPA 기본, 테스트 기반, 기준 코드).

## 스텝 8. 공통 예외의 이름을 CustomException으로 바꾼다

**요청 (사용자)**: "TtadakException 그냥 CustomException이라고 바꿔줘." 그 앞에서 전역 예외 처리기의 핸들러가 `ProblemDetail`을 바로 반환할 수 있는지 물었다.

**결정 (사용자)**: 공통 예외의 이름은 `CustomException`이다.

**한 일 (AI)**:
1. `TtadakException`을 `CustomException`으로 바꿨다(`git mv`). 소스, 테스트, ADR-0007의 이름을 모두 바꿨다. 스텝 3과 6의 일지는 쌓기만 하는 문서라 고치지 않았다. 그 일지의 `TtadakException`은 이 스텝에서 `CustomException`이 된 것이다.
2. 승인된 ADR-0007을 고쳤으므로 상태의 줄 아래에 수정의 줄을 달았다.
3. 전역 예외 처리기의 `@ExceptionHandler` 두 개가 `ResponseEntity<Object>` 대신 `ProblemDetail`을 바로 반환하게 고쳤다. 상태 코드와 `application/problem+json`은 그대로이고 오류 응답 테스트 15개가 통과했다. 오버라이드한 두 메서드는 부모의 시그니처 때문에 `ResponseEntity<Object>`를 유지한다.

**결정 (AI)** (확인이 필요하다):
- ADR-0007의 수정은 이름 바꾸기뿐이고 요구의 내용은 바꾸지 않았다.

**관찰**:
- 사용자가 커밋 확인창을 두 번 거절하고 질문과 수정을 먼저 요청했다. 커밋은 사용자가 내용을 본 뒤에 한다.

**남은 일**:
- 404, 405, 415 같은 Spring 예외에 `code`가 없다(ADR-0007의 요구 2). 공통 오류 코드를 더할지, 400만 하고 미룰지 사용자가 정한다.
- 스텝 7의 남은 일과 같다(JPA 기본은 스텝 9로 밀렸다).

## 스텝 9. 공통 오류 코드에 404와 409를 더한다

**요청 (사용자)**: "400 404 409 401 403 정도 둘려고." (404, 405, 415 같은 Spring 예외에 `code`가 빠지는 문제에 대한 답이다.)

**결정 (사용자)**: 공통 오류 코드의 상태는 400, 401, 403, 404, 409다.

**한 일 (AI)**:
1. `ErrorCode`에 `DEFAULT_NOT_FOUND`(404)와 `DEFAULT_CONFLICT`(409)를 더했다. 500은 처리하지 못한 예외의 안전망이라 그대로 뒀다.
2. 전역 예외 처리기가 Spring MVC가 만든 404 응답에도 `DEFAULT_NOT_FOUND`를 붙이게 했다(전에는 400뿐이었다). 로그 수준은 오류 코드의 값을 쓴다.
3. 존재하지 않는 경로가 404와 `DEFAULT_NOT_FOUND`로 내려가는 테스트를 더했다. 오류 응답 테스트가 18개이고 통과했다.
4. 승인된 ADR-0007에 두 코드와 요구 22와 "정하지 않은 것" 7번을 더하고 수정의 줄을 달았다. 요구의 번호는 다시 매기지 않고 끝에 붙였다.

**결정 (AI)** (확인이 필요하다):
- 이름과 메시지: `DEFAULT_NOT_FOUND`("요청한 리소스를 찾을 수 없습니다."), `DEFAULT_CONFLICT`("요청이 현재 상태와 충돌합니다."). 메멘토의 `DEFAULT_NOT_FOUND`와 비슷하게 짓고, 409는 이유를 가리지 않는 이름으로 지었다(메멘토는 중복, 동시 수정, 잠금 등으로 나눴다). 로그 수준은 둘 다 INFO다.
- 405, 406, 415 같은 그 밖의 Spring 표준 4xx 응답에는 `code`를 붙이지 않았다. 상태와 맞는 코드가 없어서 억지로 `DEFAULT_MALFORMED_REQUEST`를 붙이지 않았다. ADR-0007의 "정하지 않은 것" 7번에 올렸다.

**관찰**:
- 사용자가 코드를 더하는 결정을 상태 번호로 짧게 답했다. 상태 번호와 코드 이름의 대응(401, 403은 이미 있고 404, 409가 새로 필요하다)은 AI가 풀었다.

**남은 일**:
- 스텝 8의 남은 일과 같다(JPA 기본, 테스트 기반, 기준 코드).

## 스텝 10. 응답 모양을 ProblemDetail에서 ApiResponse로 바꾼다

**요청 (사용자)**: 메멘토의 `ApiResponse`(`ApiResponse.success()`를 반환하는 컨트롤러)를 보여 주며 "그냥 다시 롤백해서 오류도 저걸로 할려고", 이유는 "그냥 간편하게 할려고 깔끔해 보여서". 검증 실패의 `error.data`는 "목록으로 해보자", 커밋은 "커밋없이 그냥 바꾸자."

**결정 (사용자)**: 성공과 오류 모두 메멘토의 `ApiResponse`(`result`, `data`, `error{status, code, message, data}`)로 내린다. 검증 실패의 `error.data`는 `[{field, reason}]` 목록이다. 앞 스텝의 ProblemDetail 변경은 커밋하지 않고 이어서 바꾼다.

**한 일 (AI)**:
1. 테스트를 먼저 새 모양으로 다시 썼다. 타입만 만든 상태에서 20개 중 16개가 실패하는 것(red)을 확인했다.
2. `support/response`에 `ApiResponse`, `ResultType`, `ErrorMessage`를 만들었다. `ErrorCode`에 `DEFAULT_METHOD_NOT_ALLOWED`(405)와 `DEFAULT_UNSUPPORTED_MEDIA_TYPE`(415)를 더했다.
3. `GlobalExceptionHandler`를 `ResponseEntity<ApiResponse<Void>>`를 반환하게 바꿨다. 부모(`ResponseEntityExceptionHandler`)를 상속하는 구조는 유지하고, `handleExceptionInternal`에서 표준 예외 응답의 본문만 `ApiResponse`로 바꿔 담는다. 상태에 맞는 코드가 없는 표준 4xx는 `DEFAULT_MALFORMED_REQUEST`의 코드에 원래 상태를 둔다.
4. 오류 응답 테스트 22개가 통과했다. 핸들러를 일부러 깨서(405 매핑과 검증 목록 제거) 2개가 실패하는 것을 확인하고 되돌렸다. `check.sh`가 통과했다.
5. 승인된 ADR-0007을 고쳤다(요구 1, 2, 3, 4, 9, 17 수정, 요구 23 추가, "정하지 않은 것" 4번과 7번 정리, "버린 대안"과 "결과" 갱신). 상태의 줄 아래에 수정의 줄을 달았다. `docs_lint.py`가 통과했다.

**결정 (AI)** (확인이 필요하다):
- 405와 415의 코드를 공통 코드에 더했다. 사용자가 "정하지 않은 것" 7번의 질문(405, 415의 `code`)에 답하지 않아 AI가 권장안대로 했다. 406 같은 그 밖의 표준 4xx는 전용 코드 없이 `DEFAULT_MALFORMED_REQUEST`의 코드와 원래 상태로 내린다.
- 메멘토의 500 처리는 `e.getMessage()`를 응답에 담지만 가져오지 않았다. 내부 메시지를 담지 않는 요구 5를 그대로 지켰다.
- `ApiResponse`는 `support/response`, 전역 예외 처리기는 `support/error`에 둬서 두 패키지가 서로를 참조한다(메멘토도 같다). 패키지 구조를 정할 때 다시 본다(ADR-0007의 "정하지 않은 것" 1번).
- `ApiResponse<?>` 대신 오류는 `ApiResponse<Void>`, 성공은 `ApiResponse<T>`로 타입을 적었다.

**관찰**:
- 사용자가 방식을 정한 이유를 "간편하고 깔끔해서"라고 말했다. ADR의 "버린 대안"에 그대로 적었다.
- 한 번 승인한 ADR을 하루 만에 뒤집었다. 이력이 남도록 앞 스텝의 일지는 고치지 않고 이 스텝에 쌓았다.
- 사용자가 직접 지시하지 않은 스텝 6~10은 아직 커밋하지 않았다. 사용자가 커밋을 한 번에 하자고 정했다.

**남은 일**:
- 스텝 6~10의 변경을 한 번에 커밋한다(사용자의 승인 후).
- 페이지 처리의 형식, `DEFAULT_CONFLICT`를 던지는 기준(ADR-0007의 "정하지 않은 것" 4번과 7번).
- 스텝 9의 남은 일과 같다(JPA 기본, 테스트 기반, 기준 코드).

## 스텝 11. 전역 예외 처리기를 메멘토 모양으로 바꾼다

**요청 (사용자)**: "어떰의 글로벌 핸들러처럼 하고 싶은데"라고 했다가 "아 미안 memento나 ransome-back 말한거였어"라고 바로잡았다.

**결정 (사용자)**: 전역 예외 처리기는 메멘토나 randsome의 모양이다. 부모 클래스를 상속하지 않고 예외마다 `@ExceptionHandler`를 하나씩 둔다.

**한 일 (AI)**:
1. 메멘토와 randsome의 핸들러를 읽었다. 둘 다 같은 모양이다.
2. 새 경로의 테스트를 먼저 더했다: 필수 요청 파라미터 누락, 요청 파라미터의 검증 실패. 기존 핸들러에서 2개가 실패하는 것(red)을 확인했다.
3. `GlobalExceptionHandler`를 `ResponseEntityExceptionHandler` 상속 없이 다시 썼다. 핸들러는 `CustomException`, `Exception`, `MethodArgumentNotValidException`, `HandlerMethodValidationException`, `HttpMessageNotReadableException`, `MethodArgumentTypeMismatchException`, `MissingServletRequestParameterException`, `NoHandlerFoundException`과 `NoResourceFoundException`, `HttpRequestMethodNotSupportedException`, `HttpMediaTypeNotSupportedException`이다.
4. 오류 응답 테스트 24개가 통과했다. 파라미터 두 핸들러를 일부러 깨서 새 테스트 2개가 실패하는 것을 확인하고 되돌렸다. `check.sh`가 통과했다.
5. 승인된 ADR-0007을 고쳤다(요구 17, 18, 23, "정하지 않은 것" 7번, "결과"). 수정의 줄을 달았다. `docs_lint.py`가 통과했다.

**결정 (AI)** (확인이 필요하다):
- 메멘토에 있던 `ConstraintViolationException`, 헤더 누락, 동시성 잠금 핸들러는 가져오지 않았다. 지금 쓰는 곳이 없다. 필요할 때 더한다.
- 타입 불일치와 누락 파라미터는 메멘토처럼 `error.data`에 사유를 담되, 문자열 대신 `[{field, reason}]` 목록으로 담았다(스텝 10에서 정한 목록 모양에 맞췄다).
- 메멘토처럼 핸들러에 나열하지 않은 표준 예외(406 등)는 `Exception` 핸들러로 가서 500이 된다. 스텝 10의 대체 코드(400대는 `DEFAULT_MALFORMED_REQUEST`)보다 후퇴했다. 단순한 모양의 대가로 ADR의 "정하지 않은 것" 7번에 올렸다.
- 500 응답에 내부 메시지를 담지 않는 요구 5는 메멘토와 달리 지켰다.

**관찰**:
- "어떰"이라고 말했지만 뜻은 메멘토였다. 어떰의 핸들러는 ProblemDetail 방식이라 질문으로 되물어 바로잡았다. 사용자가 어느 프로젝트를 가리키는지 헷갈리면 파일을 먼저 보고 물으면 된다.
- 스텝 10의 "부모 클래스를 유지했다"는 줄은 이 스텝에서 바뀌었다. 일지는 쌓기만 하므로 고치지 않았다.

**남은 일**:
- 스텝 6~11의 변경을 한 번에 커밋한다(사용자의 승인 후).
- 스텝 10의 남은 일과 같다(페이지 처리의 형식, `DEFAULT_CONFLICT`의 기준, JPA 기본, 테스트 기반, 기준 코드).

## 스텝 12. 전역 예외 처리기를 부모 상속과 두 핸들러로 줄인다

**요청 (사용자)**: "근데 지금은 너무 세세한데 어디선 그냥 커스텀이랑 Exception만 잡던데." AI가 세 가지(상속, 진짜 두 개, 다섯 개로 줄이기)를 보이자 "1번으로 해봐"라고 했다.

**결정 (사용자)**: `ResponseEntityExceptionHandler`를 상속하고 `CustomException`과 `Exception`만 직접 잡는다. 나머지 표준 예외는 부모가 만든 응답의 본문만 바꾼다.

**한 일 (AI)**:
1. `GlobalExceptionHandler`를 다시 썼다. 직접 잡는 것은 `CustomException`, `Exception`이고, 오버라이드는 `@Valid` 실패(필드 목록을 담는다)와 `handleExceptionInternal`(표준 예외의 본문을 `ApiResponse`로 바꾼다) 두 개다. 스텝 11에서 더한 핸들러 열 개를 지웠다.
2. 단순해진 만큼 달라지는 두 테스트의 기대를 고쳤다. 필수 파라미터 누락은 `error.data` 없이 `DEFAULT_MALFORMED_REQUEST`, 요청 파라미터의 검증 실패는 `DEFAULT_VALIDATION_FAILED` 대신 `DEFAULT_MALFORMED_REQUEST`다.
3. 오류 응답 테스트 24개가 통과했다. 405 매핑과 필드 목록을 일부러 깨서 2개가 실패하는 것을 확인하고 되돌렸다. `check.sh`가 통과했다.
4. 승인된 ADR-0007을 다시 고쳤다(요구 17, 18, 23, "정하지 않은 것" 7번, "결과"). `docs_lint.py`가 통과했다.

**결정 (AI)** (확인이 필요하다):
- 요청 파라미터(`@RequestParam`) 검증 실패에는 필드 목록이 없고 `DEFAULT_MALFORMED_REQUEST`로 내려간다. 요청 본문(`@Valid`)만 `DEFAULT_VALIDATION_FAILED`와 목록을 가진다. "정하지 않은 것" 7번에 올렸다.

**관찰**:
- 한 방향(나열)과 그 반대(상속)를 하루 안에 오갔다. 사용자는 코드의 양과 단순함을 기준으로 고른다. 선택지를 줄 때 코드 줄 수와 깨지는 경우를 같이 보이면 한 번에 정할 수 있다.
- 스텝 11의 핸들러 구성은 이 스텝에서 사라졌다. 일지는 쌓기만 하므로 고치지 않았다.

**남은 일**:
- 스텝 6~12의 변경을 한 번에 커밋한다(사용자의 승인 후).
- 스텝 11의 남은 일과 같다(페이지 처리의 형식, `DEFAULT_CONFLICT`의 기준, 요청 파라미터 검증의 목록, JPA 기본, 테스트 기반, 기준 코드).

## 스텝 13. 호출 인자도 줄바꿈하면 한 줄에 하나씩 쓴다

**요청 (사용자)**: 핸들러의 줄바꿈이 어색하다고 물었고, "호출 인자는 130 넘으면" `logByLevel(` 다음 줄부터 인자를 한 줄에 하나씩 쓰고 `)`는 다음 줄에 두는 모양을 보였다.

**결정 (사용자)**: 호출 인자는 130자를 넘으면 한 줄에 하나씩 쓰고 닫는 괄호는 다음 줄에 둔다.

**한 일 (AI)**:
1. `config/spotless/eclipse-formatter.xml`에 `alignment_for_arguments_in_method_invocation`(48), `alignment_for_arguments_in_allocation_expression`(48), `parentheses_positions_in_method_invocation`(`separate_lines_if_wrapped`)을 더하고 머리 주석을 고쳤다. 선언의 매개변수와 같은 방식이다(48은 줄바꿈할 때만 한 줄에 하나씩).
2. `spotlessApply` 전에 `src`를 백업했고, 바뀐 곳이 130자를 넘던 호출 다섯 곳과 닫는 괄호 둘뿐인 것을 비교로 확인했다. `check.sh`가 통과했다.

**관찰**:
- 이 설정은 `new`와 메서드 호출에 모두 적용되어, 130자를 넘는 호출은 항상 길게 풀린다. 짧은 호출은 그대로다.
- 호출 인자의 줄바꿈은 매개변수 선언보다 규칙이 모호해서 처음에는 Eclipse 기본값("넘칠 때만")으로 뒀는데, 읽기 어색해서 맞췄다.

**남은 일**:
- 스텝 12의 남은 일과 같다. 스텝 6~13의 변경을 한 번에 커밋한다(사용자의 승인 후).

## 스텝 14. JPA 기본: BaseEntity와 시계와 감사 시각

**요청 (사용자)**: "응 다음 순서 해보자" (스텝 6~13의 커밋 `1b1fcbc` 뒤에 JPA 기본으로 넘어가자는 뜻이다.)

**결정 (사용자)**: 스텝 8에서 정한 모양이다. `delete(LocalDateTime now)`, 시각은 `Clock`으로 읽는다. 메멘토의 `BaseEntity`를 바탕으로 한다.

**한 일 (AI)**:
1. 테스트를 먼저 썼다. `BaseEntityTest`(상태 전이 2개), `BaseEntityPersistenceTest`(`@DataJpaTest`: 저장 시 시각 채움, 수정 시 `updatedAt`만 변경, 삭제 상태 저장, id 동등성, 저장 전 엔티티는 다름, 프록시 동등성 6개), `TimeConfigTest`(한국 표준시), `EntityConventionTest`(ArchUnit: C4, C5). 구현 전에는 컴파일이 안 되는 것(red)을 확인했다.
2. `support/entity`에 `BaseEntity`와 `EntityStatus`, `support/config`에 `TimeConfig`(`Asia/Seoul`의 `Clock` 빈)와 `JpaAuditingConfig`(`DateTimeProvider`가 `Clock`으로 시각을 만든다)를 만들었다.
3. 테스트에서만 쓰는 `SampleEntity`(보호된 기본 생성자, 정적 팩토리)를 엔티티의 예시이자 검사 대상으로 뒀다.
4. 전체 테스트 35개가 통과했다. 규칙을 일부러 깨서(매개변수 있는 생성자, public 기본 생성자, `delete`가 시각을 안 넣음) 테스트가 잡는 것을 확인하고 되돌렸다. `check.sh`가 통과했다.

**결정 (AI)** (확인이 필요하다):
- 패키지는 `support/entity`와 `support/config`로 뒀다. 패키지 구조는 아직 정하지 않았으므로 정할 때 옮긴다(ADR-0007의 "정하지 않은 것" 1번과 같은 문제다).
- `createdAt`과 `updatedAt`은 `nullable = false`, `createdAt`은 `updatable = false`다. 시각은 `LocalDateTime`(한국 표준시, 시간대 정보 없음)으로 저장한다.
- 식별자는 `GenerationType.IDENTITY`다(메멘토와 같다). 운영 DB가 정해지면(4차 회의) 맞는지 다시 본다.
- 삭제를 되돌리는 `active()`와 `isActive()`는 가져오지 않았다. 쓰는 곳이 없다. 필요할 때 더한다.
- `equals`와 `hashCode`는 `final`이다. 프록시를 풀기 위해 Hibernate의 `Hibernate.getClass`를 썼다.
- `SampleEntity`는 테스트 소스에 있어서 JPA를 쓰는 모든 테스트가 이 엔티티의 테이블도 만든다. 다음 스텝(테스트 기반)에서 분리할지 본다.
- ADR-0006의 C3 문장은 `delete()`로 쓰여 있는데 구현은 `delete(LocalDateTime now)`다. ADR-0006은 승인 전(제안)이라 이 스텝에서 고치지 않았다. 사용자가 ADR-0006을 확인할 때 같이 고친다.

**관찰**:
- ArchUnit은 테스트 클래스도 분석하므로 테스트용 엔티티(`SampleEntity`)가 규칙의 첫 검사 대상이 된다. 운영 엔티티가 없는 지금도 규칙이 빈 집합이 되지 않는다.

**남은 일**:
- 테스트 기반(`@Covers`, 데이터와 통합 테스트의 기반 클래스, 동시성 도우미, 운영 설정 검증 테스트), 기준 코드(엔티티와 응답 DTO 예시, Fixture), CI.
- ADR-0006의 C3 문장(`delete(now)`)과 C3~C5의 상태 갱신.
- 사용자가 정할 것: 패키지 구조, 파라미터 오류의 필드 목록, `null` 필드의 응답 포함 여부, 페이징의 모양, 4차 회의 결과(운영 DB).

## 스텝 15. equals와 hashCode를 사용자의 코드로 바꾸고 주석을 줄인다

**요청 (사용자)**: `BaseEntity`의 `equals`와 `hashCode`를 붙여 주며 "이걸로 해줘". 이어서 "난 꼭 필요한 주석만 넣을 거야."

**결정 (사용자)**: 동등성은 `HibernateProxy`를 직접 풀어 쓰는 사용자의 코드를 쓴다. 주석은 꼭 필요한 것만 둔다.

**한 일 (AI)**:
1. `BaseEntity`의 `equals`와 `hashCode`를 붙여 준 코드로 바꿨다(`Hibernate.getClass` 대신 `HibernateProxy`). 프록시 동등성 테스트를 포함한 전체 테스트가 통과했다. 포매터가 삼항 연산자의 `?`를 줄 앞으로 옮겼다.
2. 이름과 시그니처로 알 수 있는 Javadoc 9개를 지웠다(`ResultType`, `EntityStatus`, `FieldViolation`, `JpaAuditingConfig`, `CustomException`의 클래스와 `validation`, 테스트 세 곳의 클래스와 `MutableClock`). `FieldViolation`의 주석은 옛 `errors` 필드를 가리키는 낡은 설명이었다. 이유나 제약이 담긴 주석은 남겼다(`ApiResponse`, `ErrorMessage`, `TimeConfig`, `ErrorCode`, `WebApiTestSupport`, `SampleEntity`, `EntityConventionTest`, 핸들러의 두 메서드). 사용자가 직접 쓴 주석은 건드리지 않았다.
3. `check.sh`가 통과했다.

**관찰**:
- AI가 만든 코드는 클래스마다 Javadoc을 붙이는 경향이 있다. 새 클래스에는 주석을 기본으로 붙이지 않고, 숨은 제약이나 이유가 있을 때만 쓴다(AI의 작업 기억에도 적었다).
- 스텝 14에서 `BaseEntity`의 Javadoc과 `GlobalExceptionHandler`의 클래스 Javadoc은 사용자가 이미 지웠다.

**남은 일**:
- 스텝 14의 남은 일과 같다. 스텝 14와 15의 변경을 커밋한다(사용자의 승인 후).

## 스텝 16. Clock을 빼고 LocalDateTime.now()를 쓴다

**요청 (사용자)**: "그냥 난 now()로 깔끔하게 할 거긴 해. 나중에 JVM이든 서버 시간이든 한국 시간으로 맞출 거야."

**결정 (사용자)**: 시각은 `LocalDateTime.now()`로 읽는다. 한국 시간은 나중에 JVM이나 서버의 시간대 설정으로 맞춘다. `Clock` 빈은 두지 않는다.

**한 일 (AI)**:
1. `TimeConfig`와 `TimeConfigTest`를 지웠다. `JpaAuditingConfig`는 `@EnableJpaAuditing` 한 줄로 줄였다.
2. `BaseEntityPersistenceTest`를 시각을 고정하지 않는 방식으로 다시 썼다. 저장하면 생성, 수정 시각이 저장 전후 사이로 채워지는지, 수정하면 생성 시각은 그대로이고 수정 시각이 앞서지 않는지를 본다. 정확한 시각은 확인할 수 없다.
3. 감사 기능을 일부러 끄면 테스트 5개가 실패하는 것을 확인하고 되돌렸다. 전체 테스트와 `check.sh`가 통과했다.

**결정 (AI)** (확인이 필요하다):
- `delete(LocalDateTime now)`는 그대로 두었다. 시각을 인자로 받으므로 도메인 쪽은 시각을 직접 읽지 않는다. 호출하는 쪽이 `LocalDateTime.now()`를 넘긴다.

**관찰**:
- ADR-0004의 E2.1(현재 시각을 직접 읽지 않고 주입받는다)과 ADR-0006의 "정하지 않은 것" 1번(`Clock` 주입의 방식)이 이 결정과 맞지 않는다. 두 ADR은 승인 전(제안)이라 고치지 않았다. 사용자가 ADR을 확인할 때 E2.1을 "서비스가 `now()`를 읽고 도메인에는 값을 넘긴다"로 바꿀지 정한다.
- `now()`를 쓰면 시각이 얽힌 서비스 규칙(예: 마감 시각의 경계)을 테스트에서 고정할 수 없다. 그런 규칙이 생기면 그때 시각을 인자로 받게 설계한다.
- 서버의 시간대가 한국이 아니면 `createdAt`, `updatedAt`, 로그의 시각이 UTC로 나간다. 배포 설정에서 맞추는 일을 잊지 않도록 CI와 배포 단계의 확인 목록에 올린다.

**남은 일**:
- 스텝 14의 남은 일과 같다. 스텝 14~16의 변경을 커밋한다(사용자의 승인 후).
- ADR-0004의 E2.1과 ADR-0006의 C3 문장, "정하지 않은 것" 1번을 사용자의 결정에 맞춘다.

## 스텝 17. 시각 규칙을 ADR에 맞춘다

**요청 (사용자)**: 스텝 16에서 올린 ADR 충돌에 "응 바꿔". 서비스 테스트에서 시각을 고정할 방법이 없는지도 물었다("테스트에서만 어떻게 안되나?").

**결정 (사용자)**: ADR-0004의 E2.1과 ADR-0006을 `Clock` 없이 `LocalDateTime.now()`를 쓰는 결정에 맞춘다.

**한 일 (AI)**:
1. ADR-0004의 E2를 "시간과 무작위는 값으로 넘긴다"로 고쳤다. 도메인 코드는 시각을 인자로 받고 서비스가 `LocalDateTime.now()`를 읽어 넘긴다. 시각의 규칙은 서비스가 아니라 시각을 인자로 받는 도메인 메서드에 둔다.
2. ADR-0006의 C3 문장을 `delete(LocalDateTime now)`로 고치고, "정하지 않은 것" 1번에서 `Clock`을 빼고 시간대 설정(배포를 정할 때)만 남겼다.
3. 두 ADR은 아직 제안이라 수정의 줄을 달았다. `docs_lint.py`가 통과했다.

**결정 (AI)** (확인이 필요하다):
- 서비스 테스트에서 시각을 고정하는 방법으로 정적 목(`mockStatic`)을 권하지 않는다. 정적 목은 호출한 스레드에서만 동작하고 동시성 테스트를 깨며, 같은 스레드의 다른 라이브러리가 부르는 `now()`도 바꾼다. 시각이 중요한 규칙은 도메인 메서드가 시각을 인자로 받게 한다.

**관찰**:
- 시각이 얽힌 서비스 규칙이 처음 생기는 슬라이스에서 이 방식이 불편한지 다시 본다.

**남은 일**:
- 스텝 16의 남은 일과 같다. 스텝 14~17의 변경을 커밋한다(사용자의 승인 후).

## 스텝 18. 프레임워크가 하는 일은 테스트하지 않는다

**요청 (사용자)**: "근데 이걸 테스트로 만들어야돼? 스프링 기능은 믿으면 안돼?" AI가 감사 기능의 연결 확인 하나는 남기자고 하자 "이것도 믿자 그냥." 이어서 "BaseEntity코드도 믿자 그냥.", "사실상 지금 엔티티 관련해서 테스트는 안해도 돼 다 지워."

**결정 (사용자)**: 엔티티와 관련된 테스트는 두지 않는다. Spring, JPA, Hibernate가 하는 일과 `BaseEntity`의 코드(`delete`, `equals`, `hashCode`)와 엔티티 생성자 규칙을 모두 믿고, 코드 리뷰로 본다.

**한 일 (AI)**:
1. 엔티티 테스트를 모두 지웠다. 영속성 테스트 6개(감사 시각, 삭제 저장, 동등성), 상태 전이 테스트 2개(`BaseEntityTest`), ArchUnit의 엔티티 생성자 규칙(`EntityConventionTest`), 테스트용 `SampleEntity`다.
2. 승인 전인 ADR-0006의 C4와 C5의 확인 방법을 ArchUnit에서 코드 리뷰로 바꾸고 수정의 줄을 달았다.

**결정 (AI)** (확인이 필요하다):
- 감사 연결(`@EnableJpaAuditing`, `@EntityListeners`)이 빠지거나 `equals`가 틀리거나 엔티티에 매개변수 있는 생성자가 생겨도 테스트가 잡지 못한다. 감사 연결이 빠지면 시각이 `null`로 저장되어 `NOT NULL` 오류로 드러난다. 나머지는 코드 리뷰와 실제 기능의 테스트가 잡는다. 운영 엔티티가 생기면 ArchUnit 규칙을 다시 둘지 사용자가 정한다.

**관찰**:
- 테스트 대상의 기준은 "프레임워크가 하는 일인가, 우리가 쓴 코드나 정한 규칙인가"다. 앞으로 JPA 기본 동작(매핑, 저장, 조회)과 기반 클래스를 확인하는 테스트는 쓰지 않는다. 쿼리처럼 우리가 쓴 로직만 데이터 테스트로 확인한다.

**남은 일**:
- 스텝 17의 남은 일과 같다. 스텝 14~18의 변경을 커밋한다(사용자의 승인 후).

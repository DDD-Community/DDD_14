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

## 스텝 19. 테스트 애너테이션을 만든다

**요청 (사용자)**: "그 테스트 기반 커스텀 어노테이션들 다 만들어주면 될듯? E2E, controller slice, 통합". 이름은 "ControllerSlice는 어때? 통합은 그대로 가고." 이어서 "@TestConstructor(autowireMode = TestConstructor.AutowireMode.ALL) 같은 거 넣을거고."

**결정 (사용자)**: 테스트 종류마다 합성 애너테이션을 만든다. 이름은 `@ControllerSliceTest`(표현 계층), `@IntegrationTest`(응용 계층 통합), `@E2ETest`다. 기반 클래스를 상속하는 방식은 쓰지 않는다. 세 애너테이션에 `@TestConstructor(autowireMode = ALL)`을 넣어 테스트 클래스는 생성자 주입을 쓴다.

**한 일 (AI)**:
1. `src/test/java/com/ttadak/support/`에 `@Covers`(요구사항 ID, 소스 보존), `@ControllerSliceTest`(`@WebMvcTest` + 모든 요청을 허용하는 보안 설정, `controllers`를 `value`로 받는다), `@IntegrationTest`(`@SpringBootTest` + `test` 프로파일), `@E2ETest`(`@SpringBootTest(RANDOM_PORT)` + `test` 프로파일)를 만들었다. 모든 요청을 허용하는 보안 설정은 `SecurityTestConfig`다.
2. 세 애너테이션에 `@TestConstructor(autowireMode = ALL)`을 넣었다. `WebApiTestSupport`(상속하는 기반 클래스)를 지우고 `ErrorResponseTest`를 `@ControllerSliceTest`와 생성자 주입(`MockMvcTester`)으로 바꿨다.
3. 임시 확인 테스트로 `@IntegrationTest`가 `test` 프로파일로 앱을 띄우는 것과 `@E2ETest`가 임의의 포트로 띄우는 것, 두 곳 모두 생성자 주입(`@LocalServerPort` 포함)이 되는 것을 확인하고 지웠다. `ErrorResponseTest` 24개가 통과했다.

**결정 (AI)** (확인이 필요하다):
- 애너테이션의 이름과 위치(`com.ttadak.support`)는 임시로 정했고 사용자가 이름을 골랐다. 패키지는 패키지 구조를 정할 때 다시 본다.
- DB 비우기(ADR-0004 E5)와 Testcontainers는 붙이지 않았다. 운영 DB가 정해진 뒤(4차 회의) `@IntegrationTest`와 `@E2ETest`에 JUnit 확장으로 붙인다.
- 동시성 도우미와 운영 설정 검증 테스트는 쓰는 곳이 없어 만들지 않았다. 필요한 첫 슬라이스에서 만든다.
- 기존 `ErrorResponseTest`에는 `@Covers`를 달지 않았다. 위키의 요구사항이 아니라 공통 셋팅을 확인하는 테스트다.
- 애너테이션과 앱의 기동은 상시 테스트로 두지 않았다. 애너테이션이 틀리면 첫 `@IntegrationTest`가 바로 드러낸다.

**관찰**:
- 애너테이션 방식은 상속을 쓰지 않아서 한 클래스가 기반 클래스 하나에 묶이지 않고, 종류가 테스트 클래스 맨 위에 보인다.

**남은 일**:
- 스텝 18의 남은 일과 같다. 스텝 19의 변경을 커밋한다(사용자의 승인 후).
- DB가 정해진 뒤: DB 비우기와 Testcontainers 확장, 운영 설정 검증 테스트.
- 기준 코드(엔티티와 응답 DTO 예시, Fixture)는 첫 기능에서 만든다.

## 스텝 20. 엔티티와 응답 DTO의 기준 코드를 만든다

**요청 (사용자)**: "음 테스트에 예시 작성해볼까? 예시 엔티티 작성 방법 말이야." AI가 안을 보이자 "일단 만들어봐." 이어서 "도메인 로직 좀 더 추가해주고 그리고 응답엔 of도 해줘. of는 여러 인자 받을 때.", "VO도 추가해주고 그리고 그냥 of랑 from은 하나로 합치면 될듯? 한 클래스에서?"

**결정 (사용자)**: 엔티티와 응답 DTO의 작성 방법은 테스트 소스의 예시 코드로 보인다.

**한 일 (AI)**:
1. `src/test/java/com/ttadak/sample/`에 세 파일을 만들었다. `Price`(VO)는 `@Embeddable` 레코드이고 만들 때 0 이상인지 검증하며 `plus`, `times`, `isFree` 같은 값 단위의 동작을 가진다. `SampleEntity`는 `BaseEntity`를 상속하고 `protected` 기본 생성자만 두며 매개변수 있는 생성자는 두지 않는다. 정적 팩토리 `create`가 `new`로 만들어 필드를 채우고 돌려준다. 스스로 확인하고 거절하는 `rename`, `decreaseStock`, `increaseStock`, VO를 받는 `changePrice`, VO를 돌려주는 `stockValue`, 질의 메서드 `isSoldOut`을 가진다. `SampleResponse`는 레코드이고 `@Builder(access = PRIVATE)`이며 한 클래스에 `from(entity)`(엔티티 하나)와 `of(여러 값)`(엔티티 없이 값 여러 개로, 조회 전용 쿼리 결과 등)를 둔다. 규칙 번호는 코드에 쓰지 않았고, 사용자가 요청한 `from`과 `of`의 쓰임 주석만 달았다.
2. 임시 테스트로 엔티티의 저장, 감사 시각, 기본 상태(ACTIVE), VO의 저장과 조회(레코드 `@Embeddable`), 도메인 메서드(재고 감소, 증가, 거절), `from`과 `of`가 동작하는 것을 확인하고 지웠다. 예시는 테스트 대상이 아니라서 상시 테스트를 두지 않았다. `check.sh`가 통과했다.

**결정 (사용자)**: 테스트의 보안 설정 클래스의 이름을 `PermitAllSecurityTestConfig`에서 `SecurityTestConfig`로 바꿨다. IDE의 이름 바꾸기가 스텝 19의 일지 줄도 새 이름으로 고쳤고, 사용자가 "내가 바뀐 걸로 해줘"라고 해서 그대로 뒀다. 일지의 기존 줄을 고치지 않는 규칙의 예외이고, 커밋하면 이 줄이 새 기준이 되어 검사가 다시 통과한다.

**결정 (AI)** (확인이 필요하다):
- 예시는 `com.ttadak.sample`에 뒀다. 테스트 소스라서 운영 빌드에 들어가지 않고, JPA를 쓰는 테스트는 이 엔티티의 테이블도 만든다.
- 입력이 틀리면 `CustomException.validation`(`DEFAULT_VALIDATION_FAILED`)을 던지고, 재고가 모자라면 `DEFAULT_CONFLICT`를 던진다. 이 예시가 `DEFAULT_CONFLICT`를 쓰는 기준의 첫 예다. 도메인 객체가 `support`의 예외와 오류 코드를 참조하므로 ADR-0007의 "정하지 않은 것" 1번(도메인 계층이 참조해도 되는지)을 정할 때 다시 본다.
- 예시 이름과 필드(`name`, `stock`, `price`)는 규칙을 보이기 위한 임의의 값이다. 위키의 정책이나 도메인 용어와 관계없다.
- ADR-0006의 "코드로 넘긴 규칙" 표에서 C6과 C7의 상태를 바꾸지 않았다. 표의 상태 칸은 C1~C7 모두 초기 셋팅 전으로 남아 있어 사용자가 ADR-0006을 확인할 때 한 번에 갱신한다.

**관찰**:
- 예시는 코드와 같이 낡는다. 컨벤션이 바뀌면 이 두 파일을 같이 고친다.

**남은 일**:
- 스텝 19의 남은 일과 같다. 스텝 20의 변경을 커밋한다(사용자의 승인 후).
- Fixture는 테스트가 처음 필요한 첫 기능에서 만든다.

## 스텝 21. 로컬 로그와 정적 리소스 매핑을 끈다

**요청 (사용자)**: randsome의 `application.yml`(프로파일별 문서와 `config.import`, Tomcat 값, `add-mappings: false`, Jackson 시간대)을 보이며 "이런 식으로 하려 했는데 yml을 어떻게 생각해? 로컬 로그도 하자."

**결정 (사용자)**: 로컬 프로파일에 SQL 로그를 켠다.

**한 일 (AI)**:
1. `application-local.yml`에 `com.ttadak`의 debug 로그, Hibernate의 SQL 출력(`org.hibernate.SQL: debug`)과 바인딩 값(`org.hibernate.orm.jdbc.bind: trace`), SQL 줄바꿈(`format_sql`)을 더했다.
2. 의견을 물어서 `add-mappings: false`만 `application.yml`에 가져왔다. 정적 리소스 매핑을 끄는 설정이다. 기존 테스트 24개가 그대로 통과해서, 없는 경로가 계속 `ApiResponse`의 404로 내려가는 것을 확인했다.
3. 임시 테스트로 `local` 프로파일에서 로그 레벨과 `add-mappings`가 읽히는 것을 확인하고 지웠다. `check.sh`가 통과했다.

**결정 (AI)** (확인이 필요하다):
- randsome의 나머지는 가져오지 않았다. 프로파일별 `---` 문서와 `config.import`는 Spring Boot가 `application-{프로파일}.yml`을 자동으로 읽으므로 같은 일을 두 번 쓰게 된다. Tomcat의 `max-connections`와 스레드 값은 부하 테스트로 필요하다고 나온 뒤에 올린다. `jackson.time-zone`은 `Date`, `Instant`, `ZonedDateTime`에만 영향을 주고 `LocalDateTime`에는 효과가 없다.
- 운영 프로파일의 로그 설정(패턴, 파일, 레벨)은 정하지 않았다. ADR-0006의 "정하지 않은 것" 3번(로그 레벨의 구분)과 ADR-0007의 6번(요청 식별자)이 먼저다.

**관찰**:
- 기본 프로파일이 `local`이라 운영에서 `SPRING_PROFILES_ACTIVE=prod`를 빠뜨리면 H2와 `ddl-auto: update`로 뜬다. 배포 설정을 만들 때 prod 프로파일을 강제하는 장치를 둔다.
- 보안 설정이 없어서 앱을 띄우면 Spring Security의 기본값으로 모든 요청이 인증을 요구한다. 인증 방식이 정해질 때(ACC-03) 다룬다.

**남은 일**:
- 스텝 20의 남은 일과 같다. 스텝 21의 변경을 커밋한다(사용자의 승인 후).
- 4차 회의 결과의 반영(DB, CI), 하네스 파일의 정리와 충돌 확인(`.gitignore`와 일지).

## 스텝 22. ADR-0006의 코드로 넘긴 규칙 표를 실제 상태에 맞춘다

**요청 (사용자)**: AI가 표의 상태 칸이 전부 "초기 셋팅 전"이라고 짚자 "응".

**결정 (사용자)**: 아직 확정하지 않았다. AI가 고친 표를 보였고, 사용자가 다음 주제(Spotless)로 넘어갔다.

**한 일 (AI)**:
1. ADR-0006의 "코드로 넘긴 규칙" 표를 C1, C3, C6, C7은 "코드로 대체했다", C2는 "일부 코드로 대체했다"(포매터는 줄바꿈하면 한 줄에 하나씩만 맞추고 줄바꿈 자체는 리뷰), C4와 C5는 "기준 코드가 있다. 확인은 리뷰"로 고쳤다. 기준 코드의 위치(`src/main`의 `BaseEntity`, `src/test`의 `sample`)를 적었고 수정의 줄을 달았다. `docs_lint.py`가 통과했다.

**관찰**:
- ADR-0006은 하네스 브랜치에서 아직 커밋되지 않은 문서라 제 작업 트리에만 반영되어 있다. 하네스 파일 정리 때 함께 커밋한다.

**남은 일**:
- 사용자의 확인(표대로 확정할지).

## 스텝 23. Spotless 설정을 더한다

**요청 (사용자)**: "아직 하고 싶은 게 spotless 설정을 더 하고 싶긴 해." AI가 후보를 보이자 "import 순서, 메서드 체인 줄바꿈, 중괄호 안 공백, 빈 줄 규칙 하자. 근데 하기 전에 각각 예시 좀." 예시를 본 뒤 "1번 A, 2번 바꾸자, 3. 공백 없애자, 4. ㄴㄴ 클래스 본문 첫 줄은 빈 줄 맞는데 메서드에서는 빈 줄 없어."

**결정 (사용자)**: import는 알파벳 한 덩어리, 메서드 체인은 넘으면 한 줄에 하나씩, 중괄호 안 공백은 없음, 클래스 본문 첫 줄은 빈 줄이고 메서드 본문 첫 줄은 빈 줄이 없다.

**한 일 (AI)**:
1. `build.gradle.kts`에 `importOrder("\\#", "")`를 더했다. `static` import는 맨 위에 두고 빈 줄로 나누며, 나머지는 알파벳 한 덩어리다.
2. `config/spotless/eclipse-formatter.xml`에 더했다: 메서드 체인(`alignment_for_selector_in_method_invocation` 80), 배열 초기화의 중괄호 안 공백 없음, 클래스 본문 첫 줄 빈 줄 1개(`blank_lines_before_first_class_body_declaration`), 클래스 본문 끝 빈 줄 1개(`blank_lines_after_last_class_body_declaration`), 메서드 앞 빈 줄 1개, 연속 빈 줄은 최대 1개.
3. 체인 값은 처음 48로 했다가 사용자가 직접 끊은 체인의 첫 호출까지 떼어내서(`mvcTester\n.get()`) 80("첫 요소는 필요할 때만 줄바꿈")으로 바꿨다. 적용 전에 `src`를 백업했고, 되돌린 뒤 80으로 다시 적용했다.
4. 바뀐 파일은 `BaseEntity`, `GlobalExceptionHandler`, `ErrorResponseTest` 세 개다. `ErrorResponseTest`는 import가 정렬됐고, `GlobalExceptionHandler`는 메서드 사이 빈 줄 하나와 체인 줄바꿈이 맞춰졌다. 임시 파일로 각 규칙을 확인하고 지웠다. `check.sh`는 통과한다(일지의 `docs_lint`는 이 스텝을 쓴 뒤에 확인한다).

**결정 (AI)** (확인이 필요하다):
- 메서드 본문 첫 줄의 빈 줄을 없애는 것은 설정으로 할 수 없다. Eclipse의 "기존 빈 줄 유지" 때문에 `number_of_blank_lines_at_beginning_of_method_body`가 0이어도 남는다. 정규식으로 지울 수 있지만 레코드와 `if` 블록의 첫 줄 빈 줄까지 지운다. 지금 코드에는 메서드 본문 첫 줄의 빈 줄이 없으므로 코드 리뷰가 확인하는 규칙으로 둔다.
- 중괄호 안 공백은 배열 초기화(`{ElementType.TYPE, ElementType.METHOD}`)만 설정했다. 빈 클래스 본문은 `{\n}`로 정리되고 공백 없는 `{}`로는 맞추지 못한다.
- 메서드 체인이 길 때 `ex.getBindingResult()` 같은 첫 호출은 앞줄에 붙고 나머지 호출이 한 줄씩 풀린다.

**관찰**:
- 포매터 옵션의 값은 이름만으로 뜻을 알기 어렵다(48과 80, 49). 값을 고를 때 임시 파일로 먼저 확인한다.

**남은 일**:
- 스텝 22의 확인. 스텝 21 이후의 변경(스텝 23의 설정과 소스)을 커밋한다(사용자의 승인 후).

## 스텝 24. API 문서(springdoc)와 컨트롤러 문서 분리의 기준 코드

**요청 (사용자)**: 모노레포라 OpenAPI를 쓴다는데 Swagger와 무엇이 다른지, 어노테이션을 붙여야 하는지 물었다. "그동안 다 어노테이션 붙이긴 했는데 그냥 붙여도 되나?", "붙이고 그냥 openapi.json도 쓰는 거야? 아마 커밋할 거 같은데", "일단 추상 클래스로 뺄 거야", "예시만 만들자. SampleControllerDocs로 갈 거야. 네이밍은. 요청 매핑은 컨트롤러에 둘 거고."

**결정 (사용자)**: Swagger 어노테이션을 붙인다. 어노테이션은 추상 클래스 `<이름>ControllerDocs`에 모으고, 요청 매핑은 컨트롤러에 둔다. `openapi.json`은 파일로 만들어 커밋할 것 같다(확정 전, 프런트 쪽 확인 필요).

**한 일 (AI)**:
1. `springdoc-openapi-starter-webmvc-api:3.2.1`을 넣었다. Spring Boot 4의 모듈 이름을 쓰는 3.x 계열이고, 프런트가 별도 뷰어를 쓴다고 해서 Swagger UI가 없는 `-api` 아티팩트로 정했다.
2. `src/test/java/com/ttadak/sample/`에 `SampleControllerDocs`(추상 클래스: `@Tag`, `@Operation`, `@Parameter`), `SampleController`(`@RestController`, 요청 매핑과 `@Valid`, `@PathVariable`, `@RequestBody`), `SampleCreateRequest`(검증 어노테이션이 있는 요청 레코드)를 만들었다. 서비스가 없는 예시라 응답은 `SampleResponse.of(...)`와 `ApiResponse.success()`다.
3. 임시 테스트로 `/v3/api-docs`를 내려 받아 확인하고 지웠다. 부모 클래스의 어노테이션이 문서에 반영되고(태그, 요약, 설명, 경로 변수 설명), `ApiResponse<SampleResponse>`가 `ApiResponseSampleResponse`로 풀리며, 요청 레코드의 `@NotBlank`와 `@Min`이 제약으로 나오는 것을 확인했다. `check.sh`가 통과했다.

**결정 (AI)** (확인이 필요하다):
- 의존성은 `implementation`이다. 운영 코드가 어노테이션을 쓰게 되기 때문이다. 앱을 띄우면 `/v3/api-docs`가 열리는데 운영에서 열지는 정하지 않았다(인증 방식이 정해질 때 함께 정한다).
- 확인한 문서에서 두 가지가 눈에 띄었다. (1) 응답의 필드가 필수로 표시되지 않는다. `ApiResponse`, `ErrorMessage`, `SampleResponse`에 `required`가 없어서 프런트의 생성 타입이 모두 선택(`?`)이 된다. 요청 쪽은 `@NotBlank` 필드만 필수로 나온다. (2) 응답의 콘텐츠 타입이 `*/*`이고 `operationId`가 `get`, `create`처럼 일반적인 이름이라 컨트롤러가 늘면 겹친다. 둘 다 프런트와 상의해서 정한다(필수 표시는 `@Schema(requiredMode)`, 콘텐츠 타입은 `produces`, 이름은 `@Operation(operationId)`).
- 예시의 컨트롤러는 `src/test`에 있어서 `@ControllerSliceTest`가 `/samples` 경로도 함께 띄운다. 의존이 없어 테스트에는 영향이 없다.

**관찰**:
- ADR-0002의 "정하지 않은 것" 1번(API 문서 도구)이 springdoc으로 정해졌다. ADR-0002는 승인 전 문서라 이 스텝에서 고치지 않았다. 사용자가 ADR을 확인할 때 함께 정한다.

**남은 일**:
- `openapi.json`의 위치와 생성 방법(테스트로 생성, 낡음 확인 테스트), 프런트의 뷰어와 코드 생성 도구, 응답 필드의 필수 표시, 공통 오류 응답의 전역 설정, 운영에서 문서 엔드포인트의 공개 여부.
- 스텝 23의 남은 일과 같다. 스텝 24의 변경을 커밋한다(사용자의 승인 후).

## 스텝 25. 공통 패키지의 이름을 shared로 바꾼다

**요청 (사용자)**: "support 말고 shared는 어때? 객관적으로 뭐가 나아 보여." AI가 비교하고 `shared`를 권하자 "일단 바꾸자. 그리고 규칙은 굳이."

**결정 (사용자)**: 공통 패키지의 이름은 `shared`다. 이 패키지에 무엇을 두는지 한 줄의 규칙은 두지 않는다.

**한 일 (AI)**:
1. `src/main`과 `src/test`의 `com.ttadak.support`를 `git mv`로 `com.ttadak.shared`로 바꾸고 패키지 선언과 import를 고쳤다. Spring의 `org.springframework.data.jpa.domain.support`는 그대로다. 포매터가 import 순서를 다시 맞췄다. 전체 검사가 통과했다.
2. ADR-0007(승인 문서)의 "정하지 않은 것" 1번의 패키지 이름을 바꾸고 수정의 줄을 달았다. ADR-0006의 기준 코드 경로도 바꾸고 수정의 줄을 달았다.
3. 일지의 옛 스텝에는 `support`가 남아 있다. 일지는 쌓기만 하는 문서라 고치지 않았다.

**결정 (AI)** (확인이 필요하다):
- 비교에서 `support`는 DDD의 "supporting subdomain"과 뜻이 겹치고, `shared`는 "여러 기능이 같이 쓴다"는 뜻이 정확하다고 봐서 `shared`를 권했다. 차이가 크지 않다는 것도 함께 말했다.
- `shared`에 기능(도메인) 규칙이 쌓일 위험은 규칙 문장 없이 코드 리뷰에 맡긴다.

**관찰**:
- 명령 하나를 일지 쓰기와 스테이징으로 묶었는데 훅이 그 명령을 통째로 막아서 일지가 쓰이지 않았다. 일지를 쓰는 명령과 스테이징, 커밋을 따로 실행한다.

**남은 일**:
- 스텝 24의 남은 일과 같다. 스텝 25의 변경을 커밋한다.

## 스텝 26. 운영 DB를 PostgreSQL로 맞춘다

**요청 (사용자)**: "아 그리고 PostgreSQL로 하기로 함" (4차 회의의 결과다.)

**결정 (사용자)**: 운영 DB는 PostgreSQL이다.

**한 일 (AI)**:
1. `build.gradle.kts`에 PostgreSQL 드라이버(`org.postgresql:postgresql`), Flyway의 PostgreSQL 모듈(`org.flywaydb:flyway-database-postgresql`), Testcontainers의 PostgreSQL 모듈(`org.testcontainers:testcontainers-postgresql`)을 더하고 "4차 회의 뒤에 더한다"는 주석을 지웠다. 버전은 Spring Boot가 관리하고(Flyway 12.4.0, 드라이버 42.7.14, Testcontainers 2.0.5), 의존성이 해결되는 것을 확인했다.
2. 로컬과 테스트의 H2를 PostgreSQL 호환 모드(`MODE=PostgreSQL`)로 바꿨다. 로컬과 운영의 SQL 차이를 조금 줄이려는 것이다. 모드가 실제로 적용되는 것을 확인했다(`INFORMATION_SCHEMA`의 `MODE`).
3. `application-prod.yml`의 "DB를 정한 뒤 더한다"는 주석을 지웠다. 접속 정보는 이미 환경 변수(`DB_URL` 등)다.
4. ADR-0002의 MySQL 가정(요구 5, 용어 표, 서두, "결과", "정하지 않은 것" 4번)을 PostgreSQL로 고치고 수정의 줄을 달았다. "정하지 않은 것" 4번은 PostgreSQL의 버전과 커넥션 설정으로 바꿨다. `docs_lint.py`가 통과했다. 전체 테스트와 `check.sh`가 통과했다.

**결정 (AI)** (확인이 필요하다):
- 로컬과 테스트의 H2는 그대로 쓴다(ADR-0002의 요구 14). `MODE=PostgreSQL`은 완전한 호환이 아니다. SQL과 잠금의 차이는 CI에서만 잡힌다.
- Testcontainers(PostgreSQL) 의존성만 더했고 `@IntegrationTest`에는 아직 연결하지 않았다. 이 환경에서는 Docker가 응답하지 않아서 동작을 확인할 수 없었다. 연결 방식(항상 컨테이너로 할지, CI에서만 할지)은 사용자가 정한다.
- DB 비우기(ADR-0004 E5)도 아직 만들지 않았다. 엔티티가 없어 쓰임이 없다.

**관찰**:
- H2의 `getURL()`은 `MODE` 같은 옵션을 떼고 돌려줘서 처음 쓴 확인 방법이 틀렸다. 설정은 `INFORMATION_SCHEMA`로 확인해야 한다.

**남은 일**:
- Testcontainers PostgreSQL을 `@IntegrationTest`와 `@E2ETest`에 연결하는 방식을 정한다. CI 워크플로(Docker가 있는 환경에서 Postgres 컨테이너, `validate`, 마이그레이션 검증).
- 마이그레이션 파일의 위치와 이름 규칙(Flyway), PostgreSQL 버전.
- 스텝 25의 남은 일과 같다. 스텝 26의 변경을 커밋한다(사용자의 승인 후).

## 스텝 27. 로컬 개발 DB는 compose의 PostgreSQL, 테스트는 H2, Flyway는 나중에

**요청 (사용자)**: "그리고 Docker compose로 로컬 DB는 가져갈 거고 test는 H2로 할 듯, 그리고 flyway는 운영 환경 들어가면 시작할 듯."

**결정 (사용자)**: 로컬 개발은 docker compose의 PostgreSQL을 쓴다. 테스트는 H2를 쓴다(확정은 아니고 "할 듯"). Flyway는 운영 환경에 들어갈 때부터 쓴다.

**한 일 (AI)**:
1. `compose.yaml`(`server/`)을 만들었다. `postgres:17` 한 서비스, 데이터베이스, 사용자, 비밀번호는 모두 `ttadak`(로컬 전용), 포트 5432, 이름 있는 볼륨, `pg_isready` 상태 확인이다.
2. `application-local.yml`을 H2에서 `jdbc:postgresql://localhost:5432/ttadak`로 바꿨다. `ddl-auto: update`, Flyway 꺼짐, SQL 로그는 그대로다. 테스트 프로파일(`application-test.yml`)은 H2(`MODE=PostgreSQL`)다.
3. 스텝 26에서 더한 `testcontainers-postgresql` 의존성을 뺐다. 테스트가 H2라서 쓸 곳이 없다. 전체 테스트와 `check.sh`가 통과했다.
4. ADR-0002를 고쳤다. 요구 14와 서두, 용어, 버린 대안을 바꿨다. 요구 6, 7, 15는 덮어쓰지 않고 "정하지 않은 것" 8번(Flyway 시작 시점)과 9번(CI 통합 테스트의 DB)으로 올렸다. `docs_lint.py`가 통과했다.

**결정 (AI)** (확인이 필요하다):
- PostgreSQL 버전을 `17`로 임시로 정했다. 결정이 없는 값이라 "정하지 않은 것" 4번에 적었다.
- 로컬 DB의 접속 정보(`ttadak` 사용자와 비밀번호)는 로컬 전용 값이라 설정 파일에 그대로 적었다. 운영은 환경 변수를 쓴다.
- Docker가 응답하지 않아 `docker compose up`과 로컬 프로파일의 기동은 확인하지 못했다. 설정 파일의 구문과 H2 테스트 쪽 동작만 확인했다.
- 앱의 Flyway 의존성(`spring-boot-starter-flyway`, `flyway-database-postgresql`)은 그대로 뒀다. 운영 프로파일에서 켜져 있고, 마이그레이션 파일이 없으면 운영 프로파일의 기동은 실패한다(운영 환경 전에는 쓰지 않는다).
- `spring-boot-testcontainers`와 `testcontainers-junit-jupiter`는 처음 셋팅 때 넣은 것인데 지금은 쓰는 곳이 없다. 삭제는 사용자가 정하게 남겼다.

**관찰**:
- CI와 로컬 테스트가 모두 H2이면 H2와 PostgreSQL의 차이(SQL 문법, 잠금)가 운영에서야 드러난다. 잠금과 동시성의 테스트는 H2로 믿을 수 없다(ADR-0002의 "결과"). 시간이 지나면 CI에서만 Testcontainers를 쓰는 안을 다시 볼 수 있다.

**남은 일**:
- CI 워크플로(사용자의 허락 후), "정하지 않은 것" 8번과 9번.
- 스텝 26의 남은 일 중 Testcontainers 연결은 이 스텝의 결정으로 접힌다.
- 스텝 26과 27의 변경을 커밋한다(사용자의 승인 후).

## 스텝 28. 쓰지 않는 Testcontainers 의존성을 지운다

**요청 (사용자)**: "지워라 일단."

**결정 (사용자)**: 쓰지 않는 Testcontainers 의존성은 지운다.

**한 일 (AI)**:
1. `spring-boot-testcontainers`와 `testcontainers-junit-jupiter`를 `build.gradle.kts`에서 지웠다. 소스와 설정에서 쓰는 곳이 없는 것을 확인했고 전체 검사가 통과했다.

**결정 (AI)** (확인이 필요하다):
- ADR-0002의 요구 15와 "정하지 않은 것" 9번은 Testcontainers를 그대로 언급한다. CI의 테스트 DB를 정할 때(CI를 만들 때) 고친다. CI에서 Testcontainers를 쓰기로 하면 그때 의존성을 다시 더한다.

**관찰**:
- `archunit-junit5`도 지금은 쓰는 곳이 없다(엔티티 규칙 검사를 두지 않기로 했다). 지울지는 사용자가 정한다.

**남은 일**:
- CI 워크플로(사용자의 허락 후), "정하지 않은 것" 8번과 9번.
- 스텝 28의 변경을 커밋한다(사용자의 승인 후).

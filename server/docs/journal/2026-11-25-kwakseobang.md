# 작업 일지 — 2026-11-25

단계: **초기 셋팅 (PR #4)**

## 스텝 1. Java 한 줄을 100자로 줄이고 record의 모양을 정한다

**요청 (사용자)**: 샘플 프로젝트에서 정한 포맷 규칙을 서버에 적용한다.

**결정 (사용자)**:
- 한 줄은 100자까지다.
- record 컴포넌트는 짧아도 한 줄에 하나씩 쓴다.
- record 컴포넌트의 어노테이션은 한 줄에 하나씩 쓰고 필드는 그 아랫줄에 쓴다. 어노테이션이 있는 record는 컴포넌트 사이를 한 줄 띄운다.
- 메서드 매개변수와 호출 인자는 100자를 넘을 때만 줄을 나눈다.

**한 일 (AI)**:
1. Eclipse 포매터의 `lineSplit`과 `comment.line_length`를 100으로, `alignment_for_record_components`를 49로 바꾸고 `.editorconfig`의 `max_line_length`를 100으로 바꿨다.
2. record의 어노테이션 모양은 Eclipse 설정으로 만들지 못해 `build.gradle.kts`에 Spotless 커스텀 단계(`RecordAnnotationNewLine`)를 넣었다.
3. `spotlessApply`를 돌리고, `GlobalExceptionHandler`의 어색하게 끊긴 Javadoc 두 곳과 100자 안에 들어가는데 나뉜 `ErrorMessage`의 호출 한 곳을 손으로 고쳤다.
4. `./gradlew check`가 통과했다.

**결정 (AI)** (확인이 필요하다):
- `ErrorCode`의 `@formatter:off` 표는 줄을 맞춘 모양을 지키려고 고치지 않았다. 세 줄이 100자를 넘는다.

**관찰**:
- 포매터는 직접 나눈 줄을 합치지 않는다. "100자를 넘을 때만 나눈다"는 작성자와 리뷰가 지킨다.
- IDE의 자동 포맷은 커스텀 단계를 실행하지 않는다. 기준은 `./gradlew spotlessApply`다.

**남은 일**:
- ADR-0002의 요구 12와 ADR-0006의 C1, C2를 PR #3에서 맞춘다.

## 스텝 2. 한 줄을 120자로 바꾸고 선언의 줄바꿈 기준을 정한다

**요청 (사용자)**: 한 줄은 120자로 한다. 매개변수가 많은 메서드는 120자 전에도 나눈다.

**결정 (사용자)**:
- 한 줄은 120자까지다. 스텝 1의 100자를 대신한다.
- 메서드와 생성자의 선언은 매개변수가 4개 이상이면 길이와 관계없이 한 줄에 하나씩 쓴다.
- 3개 이하의 선언과 호출 인자는 120자를 넘을 때만 나눈다.

**한 일 (AI)**:
1. Java 파일을 포맷 전(`46363e9`)으로 되돌리고 120자 설정으로 `spotlessApply`를 다시 돌렸다. 스텝 1에서 100자 때문에 나뉜 줄은 남기지 않았다.
2. `SampleResponse.of`의 선언(매개변수 4개)을 나누고, 120자 안에 들어가는 `ErrorMessage`의 호출을 한 줄로 합쳤다.
3. `./gradlew check`가 통과했다.

**관찰**:
- 개수 기준은 Spotless 설정에 넣지 못했다. 직접 나눈 줄은 유지되고, 빠뜨린 곳은 리뷰가 확인한다.

**남은 일**:
- ADR-0002의 요구 12와 ADR-0006의 C1, C2를 PR #3에서 맞춘다.

## 스텝 3. 기준 코드를 새 ADR 규칙에 맞춘다

**요청 (사용자)**: 기준 코드(`src/test/java/com/ttadak/sample`)를 고친다.

**한 일 (AI)**:
1. 조회 메서드의 이름을 `get`에서 `findSample`로 바꿨다(ADR-0006의 1.10).
2. `SampleCreateRequest`와 `SampleResponse`의 필드에 `@Schema`를 달았다(5.2).
3. `SampleControllerDocs`의 `@Operation` 설명에 오류 코드와 상태를 적었다(5.3).
4. `SampleEntity`가 받는 `Price`의 `null`을 `requireNonNull`로 막고(4.8), 이름과 재고의 검사를 `validate` 하나에 모았다(4.10).
5. `./gradlew check`가 통과했다.

**관찰**:
- 위 번호의 ADR은 PR #3에 있고 이 브랜치에는 아직 없다.

**남은 일**:
- 사용자가 확인한 뒤 두 브랜치를 push하고 PR #4의 설명을 고친다.

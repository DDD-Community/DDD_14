package com.ttadak.support.error;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;
import com.ttadak.support.WebApiTestSupport;
import com.ttadak.support.response.ApiResponse;
import org.springframework.context.annotation.Import;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@Import(ErrorResponseTest.ErrorProbeController.class)
class ErrorResponseTest extends WebApiTestSupport {

    @Test
    void 성공하면_result가_SUCCESS이고_data에_값이_담긴다() {
        mvcTester.get()
            .uri("/probe/ok")
            .assertThat()
            .hasStatus(HttpStatus.OK)
            .hasContentTypeCompatibleWith(MediaType.APPLICATION_JSON)
            .bodyJson()
            .hasPathSatisfying("$.result", v -> v.assertThat().isEqualTo("SUCCESS"))
            .hasPathSatisfying("$.data", v -> v.assertThat().isEqualTo("값"))
            .hasPathSatisfying("$.error", v -> v.assertThat().isNull());
    }

    @Test
    void 돌려줄_값이_없는_성공은_data가_비어_있다() {
        mvcTester.get()
            .uri("/probe/empty")
            .assertThat()
            .hasStatus(HttpStatus.OK)
            .bodyJson()
            .hasPathSatisfying("$.result", v -> v.assertThat().isEqualTo("SUCCESS"))
            .hasPathSatisfying("$.data", v -> v.assertThat().isNull());
    }

    @ParameterizedTest
    @EnumSource(ErrorCode.class)
    void 업무_오류를_던지면_오류_코드의_상태와_error로_내려간다(ErrorCode errorCode) {
        mvcTester.get()
            .uri("/probe/error/" + errorCode.name())
            .assertThat()
            .hasStatus(errorCode.getStatus())
            .hasContentTypeCompatibleWith(MediaType.APPLICATION_JSON)
            .bodyJson()
            .hasPathSatisfying("$.result", v -> v.assertThat().isEqualTo("ERROR"))
            .hasPathSatisfying("$.data", v -> v.assertThat().isNull())
            .hasPathSatisfying("$.error.status", v -> v.assertThat().isEqualTo(errorCode.getStatus().value()))
            .hasPathSatisfying("$.error.code", v -> v.assertThat().isEqualTo(errorCode.name()))
            .hasPathSatisfying("$.error.message", v -> v.assertThat().isEqualTo(errorCode.getMessage()));
    }

    @Test
    void 업무_오류_응답의_error_data는_비어_있다() {
        mvcTester.get()
            .uri("/probe/error/DEFAULT_FORBIDDEN")
            .assertThat()
            .bodyJson()
            .hasPathSatisfying("$.error.data", v -> v.assertThat().isNull());
    }

    @Test
    void 필드와_사유를_가진_검증_오류를_던지면_error_data에_담긴다() {
        mvcTester.get()
            .uri("/probe/field-error")
            .assertThat()
            .hasStatus(HttpStatus.BAD_REQUEST)
            .bodyJson()
            .hasPathSatisfying("$.error.code", v -> v.assertThat().isEqualTo("DEFAULT_VALIDATION_FAILED"))
            .hasPathSatisfying("$.error.data[0].field", v -> v.assertThat().isEqualTo("closesAt"))
            .hasPathSatisfying("$.error.data[0].reason", v -> v.assertThat().isEqualTo("마감 시각은 현재보다 뒤여야 합니다."));
    }

    @Test
    void 요청_값이_검증을_통과하지_못하면_필드마다_error_data에_담긴다() {
        mvcTester.post()
            .uri("/probe/validate")
            .contentType(MediaType.APPLICATION_JSON)
            .content("""
                {"title": "", "options": ["하나"]}
                """)
            .assertThat()
            .hasStatus(HttpStatus.BAD_REQUEST)
            .hasContentTypeCompatibleWith(MediaType.APPLICATION_JSON)
            .bodyJson()
            .hasPathSatisfying("$.result", v -> v.assertThat().isEqualTo("ERROR"))
            .hasPathSatisfying("$.error.code", v -> v.assertThat().isEqualTo("DEFAULT_VALIDATION_FAILED"))
            .hasPathSatisfying("$.error.data", v -> v.assertThat().asList().hasSize(2))
            .hasPathSatisfying(
                "$.error.data[*].field",
                v -> v.assertThat().asList().containsExactlyInAnyOrder("title", "options")
            );
    }

    @Test
    void 요청_값이_검증을_통과하면_오류_응답이_아니다() {
        mvcTester.post()
            .uri("/probe/validate")
            .contentType(MediaType.APPLICATION_JSON)
            .content("""
                {"title": "질문", "options": ["하나", "둘"]}
                """)
            .assertThat()
            .hasStatus(HttpStatus.OK)
            .bodyJson()
            .hasPathSatisfying("$.result", v -> v.assertThat().isEqualTo("SUCCESS"));
    }

    @Test
    void 깨진_JSON_본문은_400_DEFAULT_MALFORMED_REQUEST다() {
        mvcTester.post()
            .uri("/probe/validate")
            .contentType(MediaType.APPLICATION_JSON)
            .content("{\"title\": ")
            .assertThat()
            .hasStatus(HttpStatus.BAD_REQUEST)
            .bodyJson()
            .hasPathSatisfying("$.result", v -> v.assertThat().isEqualTo("ERROR"))
            .hasPathSatisfying("$.error.code", v -> v.assertThat().isEqualTo("DEFAULT_MALFORMED_REQUEST"))
            .hasPathSatisfying("$.error.status", v -> v.assertThat().isEqualTo(400));
    }

    @Test
    void 경로_변수의_타입이_맞지_않으면_400_DEFAULT_MALFORMED_REQUEST다() {
        mvcTester.get()
            .uri("/probe/number/abc")
            .assertThat()
            .hasStatus(HttpStatus.BAD_REQUEST)
            .bodyJson()
            .hasPathSatisfying("$.error.code", v -> v.assertThat().isEqualTo("DEFAULT_MALFORMED_REQUEST"));
    }

    @Test
    void 필수_요청_파라미터가_없으면_400_DEFAULT_MALFORMED_REQUEST다() {
        mvcTester.get()
            .uri("/probe/param")
            .assertThat()
            .hasStatus(HttpStatus.BAD_REQUEST)
            .bodyJson()
            .hasPathSatisfying("$.error.code", v -> v.assertThat().isEqualTo("DEFAULT_MALFORMED_REQUEST"));
    }

    @Test
    void 요청_파라미터가_검증을_통과하지_못하면_400_DEFAULT_MALFORMED_REQUEST다() {
        mvcTester.get()
            .uri("/probe/param?size=0")
            .assertThat()
            .hasStatus(HttpStatus.BAD_REQUEST)
            .bodyJson()
            .hasPathSatisfying("$.error.code", v -> v.assertThat().isEqualTo("DEFAULT_MALFORMED_REQUEST"));
    }

    @Test
    void 존재하지_않는_경로를_요청하면_404_DEFAULT_NOT_FOUND다() {
        mvcTester.get()
            .uri("/probe/does-not-exist")
            .assertThat()
            .hasStatus(HttpStatus.NOT_FOUND)
            .hasContentTypeCompatibleWith(MediaType.APPLICATION_JSON)
            .bodyJson()
            .hasPathSatisfying("$.result", v -> v.assertThat().isEqualTo("ERROR"))
            .hasPathSatisfying("$.error.code", v -> v.assertThat().isEqualTo("DEFAULT_NOT_FOUND"));
    }

    @Test
    void 지원하지_않는_메서드로_요청하면_405_DEFAULT_METHOD_NOT_ALLOWED다() {
        mvcTester.post()
            .uri("/probe/number/1")
            .assertThat()
            .hasStatus(HttpStatus.METHOD_NOT_ALLOWED)
            .bodyJson()
            .hasPathSatisfying("$.result", v -> v.assertThat().isEqualTo("ERROR"))
            .hasPathSatisfying("$.error.code", v -> v.assertThat().isEqualTo("DEFAULT_METHOD_NOT_ALLOWED"));
    }

    @Test
    void 지원하지_않는_본문_형식으로_요청하면_415_DEFAULT_UNSUPPORTED_MEDIA_TYPE이다() {
        mvcTester.post()
            .uri("/probe/validate")
            .contentType(MediaType.TEXT_PLAIN)
            .content("텍스트")
            .assertThat()
            .hasStatus(HttpStatus.UNSUPPORTED_MEDIA_TYPE)
            .bodyJson()
            .hasPathSatisfying("$.result", v -> v.assertThat().isEqualTo("ERROR"))
            .hasPathSatisfying("$.error.code", v -> v.assertThat().isEqualTo("DEFAULT_UNSUPPORTED_MEDIA_TYPE"));
    }

    @Test
    void 처리하지_못한_예외는_500_DEFAULT_INTERNAL_ERROR로_내려간다() {
        mvcTester.get()
            .uri("/probe/unexpected")
            .assertThat()
            .hasStatus(HttpStatus.INTERNAL_SERVER_ERROR)
            .hasContentTypeCompatibleWith(MediaType.APPLICATION_JSON)
            .bodyJson()
            .hasPathSatisfying("$.result", v -> v.assertThat().isEqualTo("ERROR"))
            .hasPathSatisfying("$.error.code", v -> v.assertThat().isEqualTo("DEFAULT_INTERNAL_ERROR"))
            .hasPathSatisfying("$.error.message", v -> v.assertThat().isEqualTo(ErrorCode.DEFAULT_INTERNAL_ERROR.getMessage()));
    }

    @Test
    void 처리하지_못한_예외의_응답에는_예외_메시지와_클래스_이름이_없다() {
        mvcTester.get()
            .uri("/probe/unexpected")
            .assertThat()
            .bodyText()
            .doesNotContain("SECRET-DB-PASSWORD")
            .doesNotContain("IllegalStateException")
            .doesNotContain("ErrorResponseTest")
            .doesNotContain("trace");
    }

    @RestController
    static class ErrorProbeController {

        @GetMapping("/probe/ok")
        ApiResponse<String> ok() {
            return ApiResponse.success("값");
        }

        @GetMapping("/probe/empty")
        ApiResponse<Void> empty() {
            return ApiResponse.success();
        }

        @GetMapping("/probe/error/{code}")
        ApiResponse<String> throwError(@PathVariable String code) {
            throw new CustomException(ErrorCode.valueOf(code));
        }

        @GetMapping("/probe/field-error")
        ApiResponse<String> throwFieldError() {
            throw CustomException.validation("closesAt", "마감 시각은 현재보다 뒤여야 합니다.");
        }

        @GetMapping("/probe/number/{id}")
        ApiResponse<Long> number(@PathVariable long id) {
            return ApiResponse.success(id);
        }

        @GetMapping("/probe/param")
        ApiResponse<Integer> param(@RequestParam @Min(value = 1, message = "1 이상이어야 합니다.") int size) {
            return ApiResponse.success(size);
        }

        @GetMapping("/probe/unexpected")
        ApiResponse<String> unexpected() {
            throw new IllegalStateException("SECRET-DB-PASSWORD");
        }

        @PostMapping("/probe/validate")
        ApiResponse<Void> validate(@Valid @RequestBody ProbeRequest request) {
            return ApiResponse.success();
        }

    }

    record ProbeRequest(
        @NotBlank(message = "제목은 필수입니다.") String title,
        @Size(min = 2, max = 5, message = "선택지는 2~5개여야 합니다.") List<String> options
    ) {

    }

}

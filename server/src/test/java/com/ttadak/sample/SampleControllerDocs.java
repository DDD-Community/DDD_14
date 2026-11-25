package com.ttadak.sample;

import com.ttadak.shared.response.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;

@Tag(name = "Sample", description = "기준 코드의 예시 API")
public abstract class SampleControllerDocs {

    @Operation(summary = "샘플 조회", description = """
        id로 샘플 하나를 조회한다.

        - id가 숫자가 아니면 DEFAULT_MALFORMED_REQUEST(400)다.
        """)
    public abstract ApiResponse<SampleResponse> findSample(@Parameter(description = "샘플 id") Long id);

    @Operation(summary = "샘플 등록", description = """
        샘플을 등록한다. 돌려주는 값은 없다.

        - 이름은 비어 있을 수 없다. 재고와 가격은 0 이상이다. 어기면 DEFAULT_VALIDATION_FAILED(400)다.
        - 요청 본문의 형식이 틀리면 DEFAULT_MALFORMED_REQUEST(400)다.
        """)
    public abstract ApiResponse<Void> create(SampleCreateRequest request);

}

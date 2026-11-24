package com.ttadak.sample;

import com.ttadak.shared.response.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;

@Tag(name = "Sample", description = "기준 코드의 예시 API")
public abstract class SampleControllerDocs {

    @Operation(summary = "샘플 조회", description = "id로 샘플 하나를 조회한다.")
    public abstract ApiResponse<SampleResponse> get(@Parameter(description = "샘플 id") Long id);

    @Operation(summary = "샘플 등록", description = "샘플을 등록한다.")
    public abstract ApiResponse<Void> create(SampleCreateRequest request);

}

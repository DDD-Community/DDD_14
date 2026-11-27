package com.ttadak.sample;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;

public record SampleCreateRequest(
    @Schema(description = "샘플 이름", example = "예시")
    @NotBlank
    String name,

    @Schema(description = "재고. 0 이상", example = "10")
    @Min(0)
    int stock,

    @Schema(description = "가격. 0 이상", example = "1000")
    @Min(0)
    int price
) {

}

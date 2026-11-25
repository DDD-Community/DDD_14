package com.ttadak.sample;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;

public record SampleCreateRequest(
    @NotBlank
    String name,

    @Min(0)
    int stock,

    @Min(0)
    int price
) {

}

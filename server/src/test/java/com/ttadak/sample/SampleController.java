package com.ttadak.sample;

import com.ttadak.shared.response.ApiResponse;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/samples")
class SampleController extends SampleControllerDocs {

    @Override
    @GetMapping("/{id}")
    public ApiResponse<SampleResponse> findSample(@PathVariable Long id) {
        return ApiResponse.success(SampleResponse.of(id, "예시", 1000, false));
    }

    @Override
    @PostMapping
    public ApiResponse<Void> create(@Valid @RequestBody SampleCreateRequest request) {
        return ApiResponse.success();
    }

}

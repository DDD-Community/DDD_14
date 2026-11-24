package com.ttadak.support.error;

public record FieldViolation(
    String field,
    String reason
) {

}

package com.ttadak.sample;

import lombok.AccessLevel;
import lombok.Builder;

@Builder(access = AccessLevel.PRIVATE)
public record SampleResponse(
    Long id,
    String name,
    int price,
    boolean soldOut
) {

    /** 엔티티 하나에서 만든다. 조회한 엔티티를 그대로 응답으로 바꿀 때 쓴다. */
    public static SampleResponse from(SampleEntity entity) {
        return SampleResponse.builder()
            .id(entity.getId())
            .name(entity.getName())
            .price(entity.getPrice().amount())
            .soldOut(entity.isSoldOut())
            .build();
    }

    /** 값 여러 개로 만든다. 엔티티가 없을 때(조회 전용 쿼리의 결과 등)나 엔티티 밖의 값을 함께 담을 때 쓴다. */
    public static SampleResponse of(Long id, String name, int price, boolean soldOut) {
        return SampleResponse.builder()
            .id(id)
            .name(name)
            .price(price)
            .soldOut(soldOut)
            .build();
    }

}

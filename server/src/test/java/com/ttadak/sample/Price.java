package com.ttadak.sample;

import com.ttadak.shared.error.CustomException;
import jakarta.persistence.Embeddable;

@Embeddable
public record Price(int amount) {

    public Price {
        if (amount < 0) {
            throw CustomException.validation("price", "금액은 0 이상이어야 합니다.");
        }
    }

    public static Price of(int amount) {
        return new Price(amount);
    }

    public Price plus(Price other) {
        return new Price(amount + other.amount);
    }

    public Price times(int count) {
        return new Price(amount * count);
    }

    public boolean isFree() {
        return amount == 0;
    }

}

package com.ttadak.sample;

import com.ttadak.shared.entity.BaseEntity;
import com.ttadak.shared.error.CustomException;
import com.ttadak.shared.error.ErrorCode;
import jakarta.persistence.Entity;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Entity
public class SampleEntity extends BaseEntity {

    private String name;
    private int stock;
    private Price price;

    public static SampleEntity create(String name, int stock, Price price) {
        if (stock < 0) {
            throw CustomException.validation("stock", "재고는 0 이상이어야 합니다.");
        }

        SampleEntity entity = new SampleEntity();

        entity.rename(name);
        entity.stock = stock;
        entity.price = price;

        return entity;
    }

    public void rename(String name) {
        if (name == null || name.isBlank()) {
            throw CustomException.validation("name", "이름은 비어 있을 수 없습니다.");
        }
        this.name = name;
    }

    public void decreaseStock(int quantity) {
        requirePositive(quantity);
        if (stock < quantity) {
            throw new CustomException(ErrorCode.DEFAULT_CONFLICT);
        }
        stock -= quantity;
    }

    public void increaseStock(int quantity) {
        requirePositive(quantity);
        stock += quantity;
    }

    public void changePrice(Price price) {
        this.price = price;
    }

    public Price stockValue() {
        return price.times(stock);
    }

    public boolean isSoldOut() {
        return stock == 0;
    }

    private void requirePositive(int quantity) {
        if (quantity <= 0) {
            throw CustomException.validation("quantity", "수량은 1 이상이어야 합니다.");
        }
    }

}

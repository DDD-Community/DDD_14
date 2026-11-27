package com.ttadak.shared;

import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.web.SecurityFilterChain;

/** 인증 방식이 정해지지 않아 표현 계층 테스트는 모든 요청을 허용한다. */
@TestConfiguration
@EnableWebSecurity
public class SecurityTestConfig {

    @Bean
    SecurityFilterChain permitAll(HttpSecurity http) {
        http.authorizeHttpRequests(requests -> requests.anyRequest().permitAll())
            .csrf(AbstractHttpConfigurer::disable);

        return http.build();
    }

}

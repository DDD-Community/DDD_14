package com.ttadak.support;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.test.web.servlet.assertj.MockMvcTester;

/**
 * 표현 계층 테스트의 공통 설정. 인증 방식이 정해지지 않아 모든 요청을 허용하고, 컨트롤러가 의존하는 응용 계층은 하위 클래스가 목으로 대체한다.
 */
@Import(WebApiTestSupport.PermitAllSecurityConfig.class)
@WebMvcTest
public abstract class WebApiTestSupport {

    @Autowired
    protected MockMvcTester mvcTester;

    @TestConfiguration
    @EnableWebSecurity
    static class PermitAllSecurityConfig {

        @Bean
        SecurityFilterChain permitAll(HttpSecurity http) {
            http.authorizeHttpRequests(requests -> requests.anyRequest().permitAll())
                .csrf(AbstractHttpConfigurer::disable);

            return http.build();
        }

    }

}

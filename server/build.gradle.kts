plugins {
    java
    id("org.springframework.boot") version "4.1.3"
    id("io.spring.dependency-management") version "1.1.7"
    id("com.diffplug.spotless") version "8.12.0"
}

group = "com.ttadak"
version = "0.0.1-SNAPSHOT"
description = "ttadak-server"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(25)
    }
}

repositories {
    mavenCentral()
}

// Spring Boot 의존성 관리 밖에 있는 라이브러리의 버전
val archunitVersion = "1.5.1"
val lombok = "org.projectlombok:lombok"

dependencies {
    // Web & Security & Validation
    implementation("org.springframework.boot:spring-boot-starter-webmvc")
    implementation("org.springframework.boot:spring-boot-starter-security")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    implementation("org.springdoc:springdoc-openapi-starter-webmvc-api:3.2.1")

    // DB & Migration
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-flyway")
    implementation("org.flywaydb:flyway-database-postgresql")
    runtimeOnly("org.postgresql:postgresql")
    runtimeOnly("com.h2database:h2")

    // Lombok
    compileOnly(lombok)
    annotationProcessor(lombok)
    testCompileOnly(lombok)
    testAnnotationProcessor(lombok)

    // Testing
    testImplementation("org.springframework.boot:spring-boot-starter-data-jpa-test")
    testImplementation("org.springframework.boot:spring-boot-starter-webmvc-test")
    testImplementation("org.springframework.security:spring-security-test")
    testImplementation("com.tngtech.archunit:archunit-junit5:$archunitVersion")
    testRuntimeOnly   ("org.junit.platform:junit-platform-launcher")
}

tasks.withType<Test> {
    useJUnitPlatform()
}

// 코드 형식. 기준은 .editorconfig와 config/spotless/eclipse-formatter.xml이다.
spotless {
    java {
        target("src/**/*.java")
        eclipse().configFile("config/spotless/eclipse-formatter.xml")
        removeUnusedImports()
        importOrder("\\#", "")
        trimTrailingWhitespace()
        endWithNewline()
    }
}

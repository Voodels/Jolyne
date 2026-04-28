package com.example.demo.config;

import java.net.URI;
import java.net.URISyntaxException;

import javax.sql.DataSource;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.jdbc.DataSourceBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

@Configuration
public class DataSourceConfig {

    @Value("${SPRING_DATASOURCE_URL:}")
    private String springDatasourceUrl;

    @Value("${SPRING_DATASOURCE_USERNAME:}")
    private String springDatasourceUsername;

    @Value("${SPRING_DATASOURCE_PASSWORD:}")
    private String springDatasourcePassword;

    @Value("${NEON_DATABASE_URL:}")
    private String neonDatabaseUrl;

    @Bean
    @Primary
    public DataSource dataSource() {
        if (hasText(springDatasourceUrl)) {
            return DataSourceBuilder.create()
                    .url(springDatasourceUrl.trim())
                    .username(emptyToNull(springDatasourceUsername))
                    .password(emptyToNull(springDatasourcePassword))
                    .build();
        }

        if (!hasText(neonDatabaseUrl)) {
            throw new IllegalStateException(
                    "Missing database configuration. Set SPRING_DATASOURCE_URL or NEON_DATABASE_URL."
            );
        }

        try {
            URI uri = new URI(neonDatabaseUrl.trim());
            String userInfo = uri.getUserInfo();
            String username = null;
            String password = null;
            int port = uri.getPort() > 0 ? uri.getPort() : 5432;

            if (hasText(userInfo)) {
                String[] parts = userInfo.split(":", 2);
                username = parts[0];
                password = parts.length > 1 ? parts[1] : null;
            }

            String query = hasText(uri.getQuery()) ? "?" + uri.getQuery() : "";
            String jdbcUrl = "jdbc:postgresql://" + uri.getHost() + ":" + port
                    + uri.getPath() + query;

            return DataSourceBuilder.create()
                    .url(jdbcUrl)
                    .username(username)
                    .password(password)
                    .build();
        } catch (URISyntaxException ex) {
            throw new IllegalStateException("Invalid NEON_DATABASE_URL format", ex);
        }
    }

    private boolean hasText(String value) {
        return value != null && !value.isBlank();
    }

    private String emptyToNull(String value) {
        return hasText(value) ? value.trim() : null;
    }
}

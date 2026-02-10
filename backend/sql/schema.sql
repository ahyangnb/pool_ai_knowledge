-- ============================================================
-- Pool AI Knowledge - Database Schema
-- Database is specified by DATABASE_URL in .env
-- ============================================================

-- ==================== posts ====================
CREATE TABLE IF NOT EXISTS `posts` (
  `id`         VARCHAR(255) NOT NULL,
  `title`      VARCHAR(500) NOT NULL,
  `content`    TEXT         NOT NULL,
  `tags`       TEXT         DEFAULT NULL,
  `created_at` DATETIME     DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active`  TINYINT(1)   DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==================== api_keys ====================
CREATE TABLE IF NOT EXISTS `api_keys` (
  `id`          INT          NOT NULL AUTO_INCREMENT,
  `key_type`    VARCHAR(50)  NOT NULL COMMENT 'openai / google',
  `key_name`    VARCHAR(100) NOT NULL,
  `key_value`   TEXT         NOT NULL,
  `is_active`   TINYINT(1)   DEFAULT 1,
  `created_at`  DATETIME     DEFAULT CURRENT_TIMESTAMP,
  `updated_at`  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_by`  VARCHAR(100) DEFAULT NULL,
  `description` TEXT         DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==================== admin_users ====================
CREATE TABLE IF NOT EXISTS `admin_users` (
  `id`             INT          NOT NULL AUTO_INCREMENT,
  `username`       VARCHAR(100) NOT NULL,
  `email`          VARCHAR(255) NOT NULL,
  `password_hash`  VARCHAR(255) NOT NULL,
  `is_active`      TINYINT(1)   DEFAULT 1,
  `is_super_admin` TINYINT(1)   DEFAULT 0,
  `created_at`     DATETIME     DEFAULT CURRENT_TIMESTAMP,
  `updated_at`     DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==================== system_config ====================
CREATE TABLE IF NOT EXISTS `system_config` (
  `id`           INT          NOT NULL AUTO_INCREMENT,
  `config_key`   VARCHAR(100) NOT NULL,
  `config_value` TEXT         DEFAULT NULL,
  `description`  TEXT         DEFAULT NULL,
  `updated_at`   DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

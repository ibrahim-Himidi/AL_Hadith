-- MySQL 8.0 init script — UTF8MB4 + FULLTEXT hazırlığı
-- Bu dosya Docker ilk başlatmada çalışır

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- ============================================================
-- 1. Kullanıcılar tablosu (JWT Auth)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    email       VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name   VARCHAR(100),
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 2. Ana hadis metadata tablosu
-- ============================================================
CREATE TABLE IF NOT EXISTS hadisler (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    hadis_no    VARCHAR(30) NOT NULL,        -- Örn: "BH-1", "BH-7563"
    kitap       VARCHAR(100) NOT NULL,       -- 'Sahih al-Bukhari'
    kitap_id    INT,                         -- bukhari_books.id
    bab         TEXT,                       -- Bölüm adı
    ravi        TEXT,                       -- Ravi (narrator)
    kaynak_link VARCHAR(500),               -- https://sunnah.com/bukhari:1
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_hadis_no  (hadis_no),
    INDEX idx_kitap     (kitap),
    INDEX idx_kitap_id  (kitap_id),
    INDEX idx_ravi      (ravi(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 3. Arapça metin tablosu
-- ============================================================
CREATE TABLE IF NOT EXISTS hadis_arapca (
    hadis_id        INT PRIMARY KEY,
    sanad           MEDIUMTEXT,              -- Rivayet zinciri (orijinal)
    hadith_detail   MEDIUMTEXT NOT NULL,     -- Hadis metni (orijinal)
    metin_temiz     MEDIUMTEXT NOT NULL,     -- sanad + hadith_detail temizlenmiş

    FOREIGN KEY (hadis_id) REFERENCES hadisler(id) ON DELETE CASCADE,
    FULLTEXT INDEX ft_arapca (metin_temiz) WITH PARSER ngram
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 4. İngilizce metin tablosu
-- ============================================================
CREATE TABLE IF NOT EXISTS hadis_ingilizce (
    hadis_id        INT PRIMARY KEY,
    sanad           MEDIUMTEXT,              -- Narrator chain
    hadith_detail   MEDIUMTEXT NOT NULL,     -- Hadith text
    metin_temiz     MEDIUMTEXT NOT NULL,     -- Cleaned text for FULLTEXT

    FOREIGN KEY (hadis_id) REFERENCES hadisler(id) ON DELETE CASCADE,
    FULLTEXT INDEX ft_ingilizce (metin_temiz)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 5. Favoriler tablosu (user <-> hadis)
-- ============================================================
CREATE TABLE IF NOT EXISTS favoriler (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    user_id     INT NOT NULL,
    hadis_id    INT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uk_user_hadis (user_id, hadis_id),
    FOREIGN KEY (user_id)  REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (hadis_id) REFERENCES hadisler(id) ON DELETE CASCADE,
    INDEX idx_user_id  (user_id),
    INDEX idx_hadis_id (hadis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 6. Refresh token tablosu
-- ============================================================
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    user_id     INT NOT NULL,
    token       VARCHAR(512) NOT NULL UNIQUE,
    expires_at  TIMESTAMP NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

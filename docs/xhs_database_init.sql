-- ============================================
-- 小红书笔记数据 MySQL 数据库初始化脚本
-- 创建日期: 2026-02-05
-- 数据来源: fetch_by_subject.py 采集
-- ============================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS xhs_spider
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE xhs_spider;

-- ============================================
-- 1. 用户表
-- ============================================
DROP TABLE IF EXISTS xhs_users;
CREATE TABLE xhs_users (
    user_id          VARCHAR(64)      PRIMARY KEY COMMENT '用户ID',
    nickname         VARCHAR(255)     NOT NULL DEFAULT '' COMMENT '用户昵称',
    nick_name        VARCHAR(255)     DEFAULT '' COMMENT '备用昵称',
    avatar           VARCHAR(1024)    DEFAULT '' COMMENT '头像URL',
    xsec_token       VARCHAR(128)     DEFAULT '' COMMENT '安全令牌',
    created_at       DATETIME         DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at       DATETIME         DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_nickname (nickname(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='小红书用户表';

-- ============================================
-- 2. 笔记主表
-- ============================================
DROP TABLE IF EXISTS xhs_notes;
CREATE TABLE xhs_notes (
    id               VARCHAR(64)      PRIMARY KEY COMMENT '笔记ID',
    model_type       VARCHAR(32)      NOT NULL DEFAULT 'note' COMMENT '模型类型',
    xsec_token       VARCHAR(128)     NOT NULL DEFAULT '' COMMENT '安全令牌',
    hot_query        VARCHAR(255)     DEFAULT NULL COMMENT '热门搜索词',
    crawl_time       DATETIME         NOT NULL COMMENT '采集时间',
    created_at       DATETIME         DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at       DATETIME         DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_model_type (model_type),
    INDEX idx_crawl_time (crawl_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='小红书笔记主表';

-- ============================================
-- 3. 笔记详情表
-- ============================================
DROP TABLE IF EXISTS xhs_note_cards;
CREATE TABLE xhs_note_cards (
    id               BIGINT AUTO_INCREMENT PRIMARY KEY,
    note_id          VARCHAR(64)      NOT NULL COMMENT '关联笔记ID',
    type             VARCHAR(32)      NOT NULL DEFAULT 'normal' COMMENT '类型: normal/video',
    display_title    VARCHAR(512)     NOT NULL DEFAULT '' COMMENT '笔记标题',
    cover_url        VARCHAR(1024)    DEFAULT '' COMMENT '封面URL',
    cover_width      INT              DEFAULT 0 COMMENT '封面宽度',
    cover_height     INT              DEFAULT 0 COMMENT '封面高度',
    published_time   VARCHAR(32)      DEFAULT '' COMMENT '发布时间文本',
    created_at       DATETIME         DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME         DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES xhs_notes(id) ON DELETE CASCADE,
    INDEX idx_type (type),
    INDEX idx_published_time (published_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='小红书笔记详情表';

-- ============================================
-- 4. 互动统计表
-- ============================================
DROP TABLE IF EXISTS xhs_note_stats;
CREATE TABLE xhs_note_stats (
    id               BIGINT AUTO_INCREMENT PRIMARY KEY,
    note_id          VARCHAR(64)      NOT NULL COMMENT '关联笔记ID',
    liked_count      BIGINT           DEFAULT 0 COMMENT '点赞数',
    collected_count  BIGINT           DEFAULT 0 COMMENT '收藏数',
    comment_count    BIGINT           DEFAULT 0 COMMENT '评论数',
    shared_count     BIGINT           DEFAULT 0 COMMENT '分享数',
    liked            TINYINT(1)       DEFAULT 0 COMMENT '是否已点赞',
    collected        TINYINT(1)       DEFAULT 0 COMMENT '是否已收藏',
    created_at       DATETIME         DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME         DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES xhs_notes(id) ON DELETE CASCADE,
    INDEX idx_liked_count (liked_count),
    INDEX idx_collected_count (collected_count),
    INDEX idx_comment_count (comment_count)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='小红书笔记互动统计表';

-- ============================================
-- 5. 用户关联表（笔记-作者）
-- ============================================
DROP TABLE IF EXISTS xhs_note_authors;
CREATE TABLE xhs_note_authors (
    id               BIGINT AUTO_INCREMENT PRIMARY KEY,
    note_id          VARCHAR(64)      NOT NULL COMMENT '笔记ID',
    user_id          VARCHAR(64)      NOT NULL COMMENT '用户ID',
    created_at       DATETIME         DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES xhs_notes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES xhs_users(user_id) ON DELETE CASCADE,
    UNIQUE KEY uk_note_user (note_id, user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='笔记作者关联表';

-- ============================================
-- 6. 图片列表表
-- ============================================
DROP TABLE IF EXISTS xhs_note_images;
CREATE TABLE xhs_note_images (
    id               BIGINT AUTO_INCREMENT PRIMARY KEY,
    note_id          VARCHAR(64)      NOT NULL COMMENT '笔记ID',
    image_index      INT              NOT NULL COMMENT '图片序号(0开始)',
    width            INT              DEFAULT 0 COMMENT '图片宽度',
    height           INT              DEFAULT 0 COMMENT '图片高度',
    url_default      VARCHAR(1024)    DEFAULT '' COMMENT '默认URL',
    url_preview      VARCHAR(1024)    DEFAULT '' COMMENT '预览URL',
    created_at       DATETIME         DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES xhs_notes(id) ON DELETE CASCADE,
    UNIQUE KEY uk_note_index (note_id, image_index),
    INDEX idx_note_id (note_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='小红书笔记图片表';

-- ============================================
-- 7. 图片详情表（每张图片可能有多个场景）
-- ============================================
DROP TABLE IF EXISTS xhs_image_scenes;
CREATE TABLE xhs_image_scenes (
    id               BIGINT AUTO_INCREMENT PRIMARY KEY,
    image_id         BIGINT           NOT NULL COMMENT '关联图片ID',
    image_scene      VARCHAR(32)      NOT NULL DEFAULT 'WB_DFT' COMMENT '场景: WB_DFT/WB_PRV',
    url              VARCHAR(1024)    NOT NULL DEFAULT '' COMMENT '场景图片URL',
    created_at       DATETIME         DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES xhs_note_images(id) ON DELETE CASCADE,
    INDEX idx_image_scene (image_scene)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='图片场景详情表';

-- ============================================
-- 8. 数据采集批次表
-- ============================================
DROP TABLE IF EXISTS xhs_crawl_batches;
CREATE TABLE xhs_crawl_batches (
    id               BIGINT AUTO_INCREMENT PRIMARY KEY,
    batch_no         VARCHAR(64)      NOT NULL COMMENT '批次号',
    keyword          VARCHAR(255)     NOT NULL COMMENT '搜索关键词',
    target_quantity  INT              DEFAULT 0 COMMENT '目标数量',
    actual_quantity  INT              DEFAULT 0 COMMENT '实际采集数量',
    status           VARCHAR(32)      DEFAULT 'running' COMMENT '状态: running/completed/failed',
    started_at       DATETIME         DEFAULT CURRENT_TIMESTAMP COMMENT '开始时间',
    completed_at     DATETIME         NULL COMMENT '完成时间',
    INDEX idx_batch_no (batch_no),
    INDEX idx_keyword (keyword(100)),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据采集批次表';

-- ============================================
-- 9. ER 图关系说明
-- ============================================
/*
ER Diagram:
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│  xhs_notes  │──────▶│  xhs_note_cards  │◀──────│ xhs_note_stats │
└─────────────┘       └──────────────────┘       └─────────────┘
       │                       │                       │
       │                       ▼                       │
       │               ┌──────────────────┐
       │               │  xhs_note_images │
       │               └──────────────────┘
       │                       │
       ▼                       ▼
┌─────────────┐       ┌──────────────────┐
│ xhs_users   │◀──────│ xhs_note_authors │
└─────────────┘       └──────────────────┘
*/

-- ============================================
-- 示例：导入单条记录
-- ============================================
/*
-- 1. 插入笔记
INSERT INTO xhs_notes (id, model_type, xsec_token, crawl_time)
VALUES ('68f71e060000000005011573', 'note', 'ABMew6WZDjUiGAWnfoS5Ky95w9J-s9EN1Oyz38s_Cbt-w=', '2026-02-05 10:32:00');

-- 2. 插入用户
INSERT INTO xhs_users (user_id, nickname, avatar)
VALUES ('584458606a6a69696e3b9472', '控师地狱', 'https://sns-avatar-qc.xhscdn.com/...');

-- 3. 插入关联
INSERT INTO xhs_note_authors (note_id, user_id)
VALUES ('68f71e060000000005011573', '584458606a6a69696e3b9472');

-- 4. 插入详情
INSERT INTO xhs_note_cards (note_id, type, display_title, cover_url, cover_width, cover_height, published_time)
VALUES ('68f71e060000000005011573', 'normal', 'Jojo的奇妙合集', 'http://sns-webpic-qc.xhscdn.com/...', 1080, 2462, '2025-10-21');

-- 5. 插入统计
INSERT INTO xhs_note_stats (note_id, liked_count, collected_count, comment_count, shared_count)
VALUES ('68f71e060000000005011573', 18026, 3474, 265, 607);
*/

-- 完成提示
SELECT '✅ 数据库初始化完成！' AS message;

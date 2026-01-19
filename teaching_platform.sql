/*
 Navicat Premium Data Transfer

 Source Server         : 192.168.31.11_3306
 Source Server Type    : MySQL
 Source Server Version : 90200 (9.2.0)
 Source Host           : 192.168.31.11:3306
 Source Schema         : teaching_platform

 Target Server Type    : MySQL
 Target Server Version : 90200 (9.2.0)
 File Encoding         : 65001

 Date: 19/01/2026 23:53:34
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for announcement_reads
-- ----------------------------
DROP TABLE IF EXISTS `announcement_reads`;
CREATE TABLE `announcement_reads`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `announcement_id` int NOT NULL COMMENT '公告ID',
  `student_id` int NOT NULL COMMENT '学生ID',
  `read_at` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '阅读时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_announcement_student`(`announcement_id` ASC, `student_id` ASC) USING BTREE,
  INDEX `idx_student`(`student_id` ASC) USING BTREE,
  CONSTRAINT `fk_ar_announcement` FOREIGN KEY (`announcement_id`) REFERENCES `announcements` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_ar_student` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '公告阅读记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of announcement_reads
-- ----------------------------
INSERT INTO `announcement_reads` VALUES (1, 1, 1, '2026-01-19 22:43:25');
INSERT INTO `announcement_reads` VALUES (2, 2, 1, '2026-01-19 22:43:27');
INSERT INTO `announcement_reads` VALUES (3, 3, 1, '2026-01-19 22:43:29');
INSERT INTO `announcement_reads` VALUES (4, 1, 15, '2026-01-19 23:41:48');
INSERT INTO `announcement_reads` VALUES (5, 3, 15, '2026-01-19 23:44:58');
INSERT INTO `announcement_reads` VALUES (6, 2, 15, '2026-01-19 23:45:05');

-- ----------------------------
-- Table structure for announcement_targets
-- ----------------------------
DROP TABLE IF EXISTS `announcement_targets`;
CREATE TABLE `announcement_targets`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `announcement_id` int NOT NULL COMMENT '公告ID',
  `class_id` int NOT NULL COMMENT '班级ID',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_announcement`(`announcement_id` ASC) USING BTREE,
  INDEX `idx_class`(`class_id` ASC) USING BTREE,
  CONSTRAINT `fk_at_announcement` FOREIGN KEY (`announcement_id`) REFERENCES `announcements` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_at_class` FOREIGN KEY (`class_id`) REFERENCES `classes` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '公告班级关联表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of announcement_targets
-- ----------------------------
INSERT INTO `announcement_targets` VALUES (1, 1, 1);
INSERT INTO `announcement_targets` VALUES (2, 2, 1);
INSERT INTO `announcement_targets` VALUES (3, 2, 2);
INSERT INTO `announcement_targets` VALUES (4, 2, 3);
INSERT INTO `announcement_targets` VALUES (5, 3, 1);

-- ----------------------------
-- Table structure for announcements
-- ----------------------------
DROP TABLE IF EXISTS `announcements`;
CREATE TABLE `announcements`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '公告ID',
  `title` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '公告标题',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '公告正文',
  `type` enum('urgent','normal','course','tip') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'normal' COMMENT '公告类型:紧急/常规/课程/提示',
  `target_type` enum('all','class') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT 'class' COMMENT '发布范围:全部/指定班级',
  `is_pinned` tinyint(1) NULL DEFAULT 0 COMMENT '是否置顶',
  `publisher_id` int NOT NULL COMMENT '发布者ID(教师)',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
  `expires_at` datetime NULL DEFAULT NULL COMMENT '过期时间(可选)',
  `status` tinyint NULL DEFAULT 1 COMMENT '状态:1正常/0已删除',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_publisher`(`publisher_id` ASC) USING BTREE,
  INDEX `idx_created`(`created_at` ASC) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE,
  CONSTRAINT `fk_announcement_publisher` FOREIGN KEY (`publisher_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '班级公告表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of announcements
-- ----------------------------
INSERT INTO `announcements` VALUES (1, '📌 期末考试时间安排', '各位同学请注意：\n本学期期末考试将于下周开始，请提前做好复习准备。\n考试时间：1月25日-27日\n考试地点：另行通知', 'urgent', 'class', 1, 2, '2026-01-19 21:43:33', '2026-01-27 23:59:59', 1);
INSERT INTO `announcements` VALUES (2, '第五章课件已更新', 'ComfyUI第五章《商品变体工作流》课件已上传，请同学们及时查看学习。', 'course', 'class', 0, 2, '2026-01-19 21:43:33', NULL, 1);
INSERT INTO `announcements` VALUES (3, '💡 作业提交注意事项', '请同学们在提交作业时注意：\n1. 图片清晰度\n2. 文字说明完整\n3. 截图包含完整界面\n祝大家学习愉快！', 'tip', 'class', 0, 2, '2026-01-19 21:43:33', NULL, 1);

-- ----------------------------
-- Table structure for class_assignments
-- ----------------------------
DROP TABLE IF EXISTS `class_assignments`;
CREATE TABLE `class_assignments`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `class_id` int NOT NULL COMMENT '所属班级ID',
  `origin_task_id` int NULL DEFAULT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '作业标题',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '作业要求',
  `deadline` datetime NULL DEFAULT NULL COMMENT '截止时间',
  `status` int NULL DEFAULT 0 COMMENT '0:待发布, 1:进行中, 2:已截止',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `attachments` json NULL,
  `max_score` int NULL DEFAULT 100,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_assign_class`(`class_id` ASC) USING BTREE,
  INDEX `fk_assign_origin`(`origin_task_id` ASC) USING BTREE,
  CONSTRAINT `fk_assign_class` FOREIGN KEY (`class_id`) REFERENCES `classes` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_assign_origin` FOREIGN KEY (`origin_task_id`) REFERENCES `course_tasks` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 12 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '班级作业发布表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of class_assignments
-- ----------------------------
INSERT INTO `class_assignments` VALUES (1, 1, 1, '实训任务1：完成Shopee店铺入驻', '<p>请按照课件指导，完成店铺注册流程。</p><p><strong>提交要求：</strong>上传店铺后台首页截图，需包含店铺名称。</p>', '2026-01-09 00:00:00', 1, '2026-01-07 15:30:25', NULL, 100);
INSERT INTO `class_assignments` VALUES (2, 3, 1, '实训任务1：完成Shopee店铺入驻', '<p>请按照课件指导，完成店铺注册流程。</p><p><strong>提交要求：</strong>上传店铺后台首页截图，需包含店铺名称。</p>', NULL, 1, '2026-01-07 17:48:11', NULL, 100);
INSERT INTO `class_assignments` VALUES (3, 1, 2, '实训任务2：配置店铺物流渠道', '进入卖家中心 -> 物流设置，开启 SLS 物流渠道。<br>提交设置成功的界面截图。', '2026-01-09 16:00:00', 1, '2026-01-07 17:49:46', NULL, 100);
INSERT INTO `class_assignments` VALUES (4, 3, 2, '实训任务2：配置店铺物流渠道', '进入卖家中心 -> 物流设置，开启 SLS 物流渠道。<br>提交设置成功的界面截图。', NULL, 1, '2026-01-07 17:49:46', NULL, 100);
INSERT INTO `class_assignments` VALUES (5, 1, 3, '实训任务3：完成首个商品上架', '1. 标题包含核心关键词<br>2. 上传至少5张主图<br>3. 填写完整的属性<br>提交商品前台链接。', '2026-01-10 16:00:00', 1, '2026-01-07 17:49:51', NULL, 100);
INSERT INTO `class_assignments` VALUES (6, 3, 3, '实训任务3：完成首个商品上架', '1. 标题包含核心关键词<br>2. 上传至少5张主图<br>3. 填写完整的属性<br>提交商品前台链接。', NULL, 1, '2026-01-07 17:49:51', NULL, 100);
INSERT INTO `class_assignments` VALUES (7, 2, NULL, 'BBBBBBBB', '飒飒的阿德啊沙发沙发是撒大大飒飒飒飒水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水', '2026-01-15 00:00:00', 1, '2026-01-12 11:23:30', '[\"/static/uploads/common/f87ffd63-94a2-4c56-b856-753d0cc200ad.png\"]', 100);
INSERT INTO `class_assignments` VALUES (8, 1, NULL, 'AAAAAAAAAAAAAA', 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', '2026-01-15 00:00:00', 1, '2026-01-12 11:44:48', '[\"/static/uploads/common/2e307a96-e750-4d28-94e9-ebb94612054b.png\"]', 100);
INSERT INTO `class_assignments` VALUES (9, 1, NULL, '工作表测试', '测试', '2026-01-17 00:00:00', 1, '2026-01-15 17:05:10', '[]', 100);
INSERT INTO `class_assignments` VALUES (10, 6, 1, '实训任务1：完成Shopee店铺入驻', '<p>请按照课件指导，完成店铺注册流程。</p><p><strong>提交要求：</strong>上传店铺后台首页截图，需包含店铺名称。</p>', '2026-01-19 16:00:00', 1, '2026-01-19 13:53:15', NULL, 100);
INSERT INTO `class_assignments` VALUES (11, 6, NULL, 'shopee市场调研', 'shopee市场调研', '2026-01-20 00:00:00', 1, '2026-01-19 14:10:04', '[]', 100);

-- ----------------------------
-- Table structure for class_course_bindings
-- ----------------------------
DROP TABLE IF EXISTS `class_course_bindings`;
CREATE TABLE `class_course_bindings`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `class_id` int NOT NULL COMMENT '班级ID',
  `course_id` int NOT NULL COMMENT '课程包ID',
  `bound_at` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '绑定时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_ccb_class`(`class_id` ASC) USING BTREE,
  INDEX `fk_ccb_course`(`course_id` ASC) USING BTREE,
  CONSTRAINT `fk_ccb_class` FOREIGN KEY (`class_id`) REFERENCES `classes` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_ccb_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 52 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of class_course_bindings
-- ----------------------------
INSERT INTO `class_course_bindings` VALUES (15, 4, 7, '2025-12-31 16:09:21');
INSERT INTO `class_course_bindings` VALUES (16, 5, 8, '2025-12-31 16:10:00');
INSERT INTO `class_course_bindings` VALUES (36, 1, 1, '2026-01-06 11:40:50');
INSERT INTO `class_course_bindings` VALUES (37, 1, 2, '2026-01-06 11:40:50');
INSERT INTO `class_course_bindings` VALUES (38, 1, 6, '2026-01-06 11:40:50');
INSERT INTO `class_course_bindings` VALUES (39, 3, 1, '2026-01-07 15:40:13');
INSERT INTO `class_course_bindings` VALUES (40, 3, 6, '2026-01-07 15:40:13');
INSERT INTO `class_course_bindings` VALUES (47, 2, 2, '2026-01-16 15:41:44');
INSERT INTO `class_course_bindings` VALUES (48, 2, 1, '2026-01-16 15:41:44');
INSERT INTO `class_course_bindings` VALUES (49, 2, 3, '2026-01-16 15:41:44');
INSERT INTO `class_course_bindings` VALUES (50, 6, 1, '2026-01-19 10:19:29');
INSERT INTO `class_course_bindings` VALUES (51, 6, 6, '2026-01-19 10:19:29');

-- ----------------------------
-- Table structure for classes
-- ----------------------------
DROP TABLE IF EXISTS `classes`;
CREATE TABLE `classes`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  `teacher_id` int NOT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `cover_image` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '班级封面图URL',
  `start_date` datetime NULL DEFAULT NULL COMMENT '开课时间',
  `end_date` datetime NULL DEFAULT NULL COMMENT '结课时间',
  `status` int NULL DEFAULT 0 COMMENT '0进行中 1已归档',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `teacher_id`(`teacher_id` ASC) USING BTREE,
  INDEX `ix_classes_id`(`id` ASC) USING BTREE,
  CONSTRAINT `classes_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of classes
-- ----------------------------
INSERT INTO `classes` VALUES (1, '25跨境电商1班', '', 2, '2025-12-26 16:01:20', 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?q=80&w=300&auto=format&fit=crop', '2025-12-10 16:00:00', '2025-12-22 16:00:00', 0);
INSERT INTO `classes` VALUES (2, '25电子商务1班', '电商', 2, '2025-12-29 10:21:33', 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=300&auto=format&fit=crop', '2025-12-29 10:18:00', '2025-12-31 15:47:00', 0);
INSERT INTO `classes` VALUES (3, '25商务英语1班', '商务英语1班', 2, '2025-12-29 16:28:53', 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=300&auto=format&fit=crop', '2025-12-29 08:28:00', '2025-12-30 16:00:00', 1);
INSERT INTO `classes` VALUES (4, '25电子商务2班', '', 4, '2025-12-31 16:09:21', 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=300&auto=format&fit=crop', '2025-12-31 08:08:00', '2026-02-25 16:00:00', 0);
INSERT INTO `classes` VALUES (5, '25跨境电商2班', '', 4, '2025-12-31 16:10:00', 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=300&auto=format&fit=crop', '2025-12-30 16:00:00', '2026-02-11 16:00:00', 0);
INSERT INTO `classes` VALUES (6, '2025跨境电商1班', '基础学习', 55, '2026-01-19 10:19:29', 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=300&auto=format&fit=crop', '2026-01-19 02:18:00', '2026-06-29 16:00:00', 0);

-- ----------------------------
-- Table structure for course_chapters
-- ----------------------------
DROP TABLE IF EXISTS `course_chapters`;
CREATE TABLE `course_chapters`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_id` int NOT NULL COMMENT '所属课程ID',
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '章节标题',
  `sort_order` int NULL DEFAULT 0 COMMENT '排序权重(越小越靠前)',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_chapter_course`(`course_id` ASC) USING BTREE,
  CONSTRAINT `fk_chapter_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 55 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '课程章节表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of course_chapters
-- ----------------------------
INSERT INTO `course_chapters` VALUES (26, 6, '第01章 平台入驻与基础建设', 1, '2026-01-06 10:24:04');
INSERT INTO `course_chapters` VALUES (27, 6, '第02章 商品运营与店铺装修', 2, '2026-01-06 10:24:04');
INSERT INTO `course_chapters` VALUES (28, 6, '第03章 营销推广与流量获取', 3, '2026-01-06 10:24:04');
INSERT INTO `course_chapters` VALUES (29, 6, '第04章 订单履约与售后服务', 4, '2026-01-06 10:24:05');
INSERT INTO `course_chapters` VALUES (52, 1, '第01章 课程简介', 1, '2026-01-19 11:43:38');
INSERT INTO `course_chapters` VALUES (53, 1, '第02章 ComfyUI基础入门', 2, '2026-01-19 11:43:38');
INSERT INTO `course_chapters` VALUES (54, 1, '第03章 跨境电商业务场景实战工作流体系', 3, '2026-01-19 11:43:38');

-- ----------------------------
-- Table structure for course_lessons
-- ----------------------------
DROP TABLE IF EXISTS `course_lessons`;
CREATE TABLE `course_lessons`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `chapter_id` int NOT NULL COMMENT '所属章节ID',
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '课时标题',
  `resource_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '类型: pdf, ppt, video',
  `file_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '文件存储路径 (/static/...)',
  `duration` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '时长或页数 (如 \"15min\", \"23页\")',
  `is_free` tinyint(1) NULL DEFAULT 0 COMMENT '是否免费试看 (0:否, 1:是)',
  `sort_order` int NULL DEFAULT 0 COMMENT '排序权重',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_lesson_chapter`(`chapter_id` ASC) USING BTREE,
  CONSTRAINT `fk_lesson_chapter` FOREIGN KEY (`chapter_id`) REFERENCES `course_chapters` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 410 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '课时资源表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of course_lessons
-- ----------------------------
INSERT INTO `course_lessons` VALUES (201, 26, '任务1 Shopee平台店铺入驻指导', 'pdf', '/static/uploads/materials/course_6/chapter_26/任务1 Shopee平台店铺入驻指导.pdf', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (202, 26, '任务1 Shopee平台店铺入驻指导', 'ppt', '/static/uploads/materials/course_6/chapter_26/任务1 Shopee平台店铺入驻指导.pptx', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (203, 26, '任务2 Shopee平台卖家端功能介绍', 'pdf', '/static/uploads/materials/course_6/chapter_26/任务2 Shopee平台卖家端功能介绍.pdf', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (204, 26, '任务2 Shopee平台卖家端功能介绍', 'ppt', '/static/uploads/materials/course_6/chapter_26/任务2 Shopee平台卖家端功能介绍.pptx', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (205, 26, '任务3 Shopee平台店铺基础设置', 'pdf', '/static/uploads/materials/course_6/chapter_26/任务3 Shopee平台店铺基础设置.pdf', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (206, 26, '任务3 Shopee平台店铺基础设置', 'ppt', '/static/uploads/materials/course_6/chapter_26/任务3 Shopee平台店铺基础设置.pptx', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (207, 26, '任务4 Shopee平台物流设置指导', 'pdf', '/static/uploads/materials/course_6/chapter_26/任务4 Shopee平台物流设置指导.pdf', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (208, 26, '任务4 Shopee平台物流设置指导', 'ppt', '/static/uploads/materials/course_6/chapter_26/任务4 Shopee平台物流设置指导.pptx', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (209, 27, '任务5 如何在Shopee平台进行商品上架', 'pdf', '/static/uploads/materials/course_6/chapter_27/任务5 如何在Shopee平台进行商品上架.pdf', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (210, 27, '任务5 如何在Shopee平台进行商品上架', 'ppt', '/static/uploads/materials/course_6/chapter_27/任务5 如何在Shopee平台进行商品上架.pptx', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (211, 27, '任务6 Shopee平台商品优化技巧（标题、类目、属性）', 'pdf', '/static/uploads/materials/course_6/chapter_27/任务6 Shopee平台商品优化技巧（标题、类目、属性）.pdf', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (212, 27, '任务6 Shopee平台商品优化技巧（标题、类目、属性）', 'ppt', '/static/uploads/materials/course_6/chapter_27/任务6 Shopee平台商品优化技巧（标题、类目、属性）.pptx', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (213, 27, '任务7 Shopee平台商品优化技巧（描述、图片、视频）', 'pdf', '/static/uploads/materials/course_6/chapter_27/任务7 Shopee平台商品优化技巧（描述、图片、视频）.pdf', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (214, 27, '任务7 Shopee平台商品优化技巧（描述、图片、视频）', 'ppt', '/static/uploads/materials/course_6/chapter_27/任务7 Shopee平台商品优化技巧（描述、图片、视频）.pptx', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (215, 27, '任务8 Shopee平台商店介绍设置流程', 'pdf', '/static/uploads/materials/course_6/chapter_27/任务8 Shopee平台商店介绍设置流程.pdf', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (216, 27, '任务8 Shopee平台商店介绍设置流程', 'ppt', '/static/uploads/materials/course_6/chapter_27/任务8 Shopee平台商店介绍设置流程.pptx', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (217, 27, '任务9 Shopee平台店铺装修指南', 'pdf', '/static/uploads/materials/course_6/chapter_27/任务9 Shopee平台店铺装修指南.pdf', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (218, 27, '任务9 Shopee平台店铺装修指南', 'ppt', '/static/uploads/materials/course_6/chapter_27/任务9 Shopee平台店铺装修指南.pptx', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (219, 27, '任务10 Shopee平台店铺装修：装饰组件的运用', 'pdf', '/static/uploads/materials/course_6/chapter_27/任务10 Shopee平台店铺装修：装饰组件的运用.pdf', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (220, 27, '任务10 Shopee平台店铺装修：装饰组件的运用', 'ppt', '/static/uploads/materials/course_6/chapter_27/任务10 Shopee平台店铺装修：装饰组件的运用.pptx', '15页', 0, 0, '2026-01-06 10:24:04');
INSERT INTO `course_lessons` VALUES (221, 28, '任务11 Shopee平台如何设置优惠券', 'pdf', '/static/uploads/materials/course_6/chapter_28/任务11 Shopee平台如何设置优惠券.pdf', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (222, 28, '任务11 Shopee平台如何设置优惠券', 'ppt', '/static/uploads/materials/course_6/chapter_28/任务11 Shopee平台如何设置优惠券.pptx', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (223, 28, '任务12 Shopee平台折扣活动设置流程', 'pdf', '/static/uploads/materials/course_6/chapter_28/任务12 Shopee平台折扣活动设置流程.pdf', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (224, 28, '任务12 Shopee平台折扣活动设置流程', 'ppt', '/static/uploads/materials/course_6/chapter_28/任务12 Shopee平台折扣活动设置流程.pptx', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (225, 28, '任务13 Shopee平台套装优惠设置流程 (Bundle Deal)', 'pdf', '/static/uploads/materials/course_6/chapter_28/任务13 Shopee平台套装优惠设置流程 (Bundle Deal).pdf', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (226, 28, '任务13 Shopee平台套装优惠设置流程 (Bundle Deal)', 'ppt', '/static/uploads/materials/course_6/chapter_28/任务13 Shopee平台套装优惠设置流程 (Bundle Deal).pptx', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (227, 28, '任务14 Shopee平台设置限时选购使用方法 (Flash Deal)', 'pdf', '/static/uploads/materials/course_6/chapter_28/任务14 Shopee平台设置限时选购使用方法 (Flash Deal).pdf', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (228, 28, '任务14 Shopee平台设置限时选购使用方法 (Flash Deal)', 'ppt', '/static/uploads/materials/course_6/chapter_28/任务14 Shopee平台设置限时选购使用方法 (Flash Deal).pptx', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (229, 28, '任务15 Shopee平台广告 (Ads) 投放流程', 'pdf', '/static/uploads/materials/course_6/chapter_28/任务15 Shopee平台广告 (Ads) 投放流程.pdf', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (230, 28, '任务15 Shopee平台广告 (Ads) 投放流程', 'ppt', '/static/uploads/materials/course_6/chapter_28/任务15 Shopee平台广告 (Ads) 投放流程.pptx', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (231, 28, '任务16 Shopee平台站外渠道广告功能介绍', 'pdf', '/static/uploads/materials/course_6/chapter_28/任务16 Shopee平台站外渠道广告功能介绍.pdf', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (232, 28, '任务16 Shopee平台站外渠道广告功能介绍', 'ppt', '/static/uploads/materials/course_6/chapter_28/任务16 Shopee平台站外渠道广告功能介绍.pptx', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (233, 29, '任务17 Shopee平台订单发货流程', 'pdf', '/static/uploads/materials/course_6/chapter_29/任务17 Shopee平台订单发货流程.pdf', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (234, 29, '任务17 Shopee平台订单发货流程', 'ppt', '/static/uploads/materials/course_6/chapter_29/任务17 Shopee平台订单发货流程.pptx', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (235, 29, '任务18 Shopee平台退货退款处理流程', 'pdf', '/static/uploads/materials/course_6/chapter_29/任务18 Shopee平台退货退款处理流程.pdf', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (236, 29, '任务18 Shopee平台退货退款处理流程', 'ppt', '/static/uploads/materials/course_6/chapter_29/任务18 Shopee平台退货退款处理流程.pptx', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (237, 29, '任务19 关于Shopee平台售前、售中、售后咨询服务', 'pdf', '/static/uploads/materials/course_6/chapter_29/任务19 关于Shopee平台售前、售中、售后咨询服务.pdf', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (238, 29, '任务19 关于Shopee平台售前、售中、售后咨询服务', 'ppt', '/static/uploads/materials/course_6/chapter_29/任务19 关于Shopee平台售前、售中、售后咨询服务.pptx', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (239, 29, '任务20 Shopee平台如何使用运费测算工具', 'pdf', '/static/uploads/materials/course_6/chapter_29/任务20 Shopee平台如何使用运费测算工具.pdf', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (240, 29, '任务20 Shopee平台如何使用运费测算工具', 'ppt', '/static/uploads/materials/course_6/chapter_29/任务20 Shopee平台如何使用运费测算工具.pptx', '15页', 0, 0, '2026-01-06 10:24:05');
INSERT INTO `course_lessons` VALUES (389, 52, '1.1 课程定位', 'pdf', '/static/uploads/materials/course_1/chapter_52/1.1 课程定位.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (390, 52, '1.2 学习目标', 'pdf', '/static/uploads/materials/course_1/chapter_52/1.2 学习目标.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (391, 52, '1.3 适用人群', 'pdf', '/static/uploads/materials/course_1/chapter_52/1.3 适用人群.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (392, 52, '1.4 ComfyUI 在跨境电商中的价值与前景', 'pdf', '/static/uploads/materials/course_1/chapter_52/1.4 ComfyUI 在跨境电商中的价值与前景.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (393, 53, '2.1 认识 ComfyUI', 'pdf', '/static/uploads/materials/course_1/chapter_53/2.1 认识 ComfyUI.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (394, 53, '2.2 安装与环境配置', 'pdf', '/static/uploads/materials/course_1/chapter_53/2.2 安装与环境配置.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (395, 53, '2.3 界面总览', 'pdf', '/static/uploads/materials/course_1/chapter_53/2.3 界面总览.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (396, 53, '2.4 第一张图的生成', 'pdf', '/static/uploads/materials/course_1/chapter_53/2.4 第一张图的生成.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (397, 53, '2.5 章节任务', 'pdf', '/static/uploads/materials/course_1/chapter_53/2.5 章节任务.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (398, 54, '任务01 局部重绘工作流', 'pdf', '/static/uploads/materials/course_1/chapter_54/任务01 局部重绘工作流.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (399, 54, '任务02 图片扩展', 'pdf', '/static/uploads/materials/course_1/chapter_54/任务02 图片扩展.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (400, 54, '任务03 产品图场景迁移（指定场景）', 'pdf', '/static/uploads/materials/course_1/chapter_54/任务03 产品图场景迁移（指定场景）.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (401, 54, '任务04 风格迁移生成', 'pdf', '/static/uploads/materials/course_1/chapter_54/任务04 风格迁移生成.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (402, 54, '任务05 线稿生成器', 'pdf', '/static/uploads/materials/course_1/chapter_54/任务05 线稿生成器.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (403, 54, '任务06 小物件迁移（指定场景）', 'pdf', '/static/uploads/materials/course_1/chapter_54/任务06 小物件迁移（指定场景）.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (404, 54, '任务07 商品变体工作流（canny篇）', 'pdf', '/static/uploads/materials/course_1/chapter_54/任务07 商品变体工作流（canny篇）.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (405, 54, '任务08 商品变体工作流（depth篇）', 'pdf', '/static/uploads/materials/course_1/chapter_54/任务08 商品变体工作流（depth篇）.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (406, 54, '任务09 商品变体工作流（openpose篇）', 'pdf', '/static/uploads/materials/course_1/chapter_54/任务09 商品变体工作流（openpose篇）.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (407, 54, '任务10 模特换装（绘制遮罩）', 'pdf', '/static/uploads/materials/course_1/chapter_54/任务10 模特换装（绘制遮罩）.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (408, 54, '任务11 模特换装（Qwen全自动指令版）', 'pdf', '/static/uploads/materials/course_1/chapter_54/任务11 模特换装（Qwen全自动指令版）.pdf', '15页', 0, 0, '2026-01-19 11:43:38');
INSERT INTO `course_lessons` VALUES (409, 54, '任务12 图像编辑', 'pdf', '/static/uploads/materials/course_1/chapter_54/任务12 图像编辑.pdf', '15页', 0, 0, '2026-01-19 11:43:38');

-- ----------------------------
-- Table structure for course_tasks
-- ----------------------------
DROP TABLE IF EXISTS `course_tasks`;
CREATE TABLE `course_tasks`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_id` int NOT NULL COMMENT '所属课程ID',
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '作业标题',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '作业要求(富文本/HTML)',
  `sort_order` int NULL DEFAULT 0 COMMENT '排序',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `lesson_id` int NULL DEFAULT NULL COMMENT '关联的课时ID',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_task_course`(`course_id` ASC) USING BTREE,
  INDEX `fk_task_lesson`(`lesson_id` ASC) USING BTREE,
  CONSTRAINT `fk_task_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_task_lesson` FOREIGN KEY (`lesson_id`) REFERENCES `course_lessons` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '课程作业模板表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of course_tasks
-- ----------------------------
INSERT INTO `course_tasks` VALUES (1, 6, '实训任务1：完成Shopee店铺入驻', '<p>请按照课件指导，完成店铺注册流程。</p><p><strong>提交要求：</strong>上传店铺后台首页截图，需包含店铺名称。</p>', 1, '2026-01-07 11:35:58', 201);
INSERT INTO `course_tasks` VALUES (2, 6, '实训任务2：配置店铺物流渠道', '进入卖家中心 -> 物流设置，开启 SLS 物流渠道。<br>提交设置成功的界面截图。', 2, '2026-01-07 11:35:58', 203);
INSERT INTO `course_tasks` VALUES (3, 6, '实训任务3：完成首个商品上架', '1. 标题包含核心关键词<br>2. 上传至少5张主图<br>3. 填写完整的属性<br>提交商品前台链接。', 3, '2026-01-07 11:35:58', 205);
INSERT INTO `course_tasks` VALUES (4, 6, '期末考核：店铺装修闭环', '使用“装修大师”完成店铺首页装修，包括轮播图、商品分类栏。', 4, '2026-01-07 11:35:58', 207);

-- ----------------------------
-- Table structure for courses
-- ----------------------------
DROP TABLE IF EXISTS `courses`;
CREATE TABLE `courses`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '课程名称',
  `cover` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '课程封面URL',
  `intro` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '课程简介',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `task_count` int NULL DEFAULT 0 COMMENT '本课程任务数量',
  `total_duration` int NULL DEFAULT 0 COMMENT '总时长(分钟)',
  `lesson_count` int NULL DEFAULT 0 COMMENT '本课程课时数',
  `course_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '实训课程' COMMENT '课程类型',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 12 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of courses
-- ----------------------------
INSERT INTO `courses` VALUES (1, '【01】AI+(跨境)电商视觉营销设计', '/static/uploads/courses/f48d9e7d-4d3b-4b67-846b-663341a632ab.webp', '本课程专为跨境电商行业量身打造，从零开始系统学习如何使用ComfyUI打造电商商品图、场景图、模特图等视觉内容生产流程。面对传统拍摄成本高昂、制作周期长达3-7天影响新品上线的行业痛点，本课程通过节点式可视化工作流，让运营人员、设计师、讲师无需美术基础即可实现专业级图像生成。', '2025-12-29 16:27:59', 20, 800, 21, '实训课程');
INSERT INTO `courses` VALUES (2, '【02】AI+智能体跨境客服应用', '/static/uploads/courses/121a8ee1-6756-4f38-9617-305fd69f97bc.png', '可视化节点编排AI电商自动化工作流', '2025-12-29 16:31:28', 0, 0, 0, '实训课程');
INSERT INTO `courses` VALUES (3, '【03】AI提示词工程与跨境电商运营实务', '/static/uploads/courses/824528c9-caff-49cb-85df-4e5e46277d17.png', 'AI提示词工程与跨境电商运营实务', '2025-12-29 16:32:12', 0, 0, 0, '实训课程');
INSERT INTO `courses` VALUES (4, '【04】跨境AI+短视频运营实战', '/static/uploads/courses/829cd3c3-d1b1-4b0d-8a7e-63c543a9f588.png', '', '2025-12-30 17:11:50', 0, 0, 0, '实训课程');
INSERT INTO `courses` VALUES (5, '【05】AI+跨境电商数据分析实务', '/static/uploads/courses/0486fddf-3fbc-4907-a7ed-ce9ec8c925c6.png', '', '2025-12-30 17:12:10', 0, 0, 0, '实训课程');
INSERT INTO `courses` VALUES (6, '【06】Shopee虚拟仿真与实战应用（东盟市场）', '/static/uploads/courses/379724bb-5ef3-47a5-b1b4-84dc219f8f7d.png', 'Shopee电商平台实训课程以典型工作任务驱 ，该课程涵盖卖家开店与经营的完整业务流程。在本课程中，学生将学习如何卖家完成账号注册、业务信息设置、运费模板设置、商品管理、营销活动、广告活动、订单管理等平台任务操作，使学生具备Shopee店铺的开设与营销、客服服务等能力。', '2025-12-30 17:12:33', 20, 510, 50, '实训课程');
INSERT INTO `courses` VALUES (7, '【07】Ozon虚拟仿真与实战应用（中亚市场）', '/static/uploads/courses/3f48e3fb-130e-4acf-b059-0406583edf67.png', '', '2025-12-30 17:12:49', 0, 0, 0, '实训课程');
INSERT INTO `courses` VALUES (8, '【08】东盟语种跨境直播实战', '/static/uploads/courses/e7c2c671-aa9b-4e1f-80d4-b0ff47e8c927.png', '', '2025-12-30 17:13:34', 0, 0, 0, '实训课程');

-- ----------------------------
-- Table structure for enrollments
-- ----------------------------
DROP TABLE IF EXISTS `enrollments`;
CREATE TABLE `enrollments`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `class_id` int NOT NULL,
  `student_id` int NOT NULL,
  `joined_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `class_id`(`class_id` ASC) USING BTREE,
  INDEX `student_id`(`student_id` ASC) USING BTREE,
  INDEX `ix_enrollments_id`(`id` ASC) USING BTREE,
  CONSTRAINT `enrollments_ibfk_1` FOREIGN KEY (`class_id`) REFERENCES `classes` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `enrollments_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 112 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of enrollments
-- ----------------------------
INSERT INTO `enrollments` VALUES (1, 1, 8, '2025-12-26 16:02:05');
INSERT INTO `enrollments` VALUES (2, 1, 1, '2025-12-26 16:28:51');
INSERT INTO `enrollments` VALUES (3, 2, 5, '2025-12-29 16:35:07');
INSERT INTO `enrollments` VALUES (4, 2, 6, '2025-12-29 16:35:29');
INSERT INTO `enrollments` VALUES (6, 3, 9, '2025-12-29 17:59:50');
INSERT INTO `enrollments` VALUES (7, 3, 10, '2025-12-30 14:20:52');
INSERT INTO `enrollments` VALUES (8, 2, 7, '2025-12-30 16:38:13');
INSERT INTO `enrollments` VALUES (9, 2, 11, '2025-12-30 16:38:48');
INSERT INTO `enrollments` VALUES (10, 4, 12, '2025-12-31 16:11:05');
INSERT INTO `enrollments` VALUES (11, 4, 13, '2025-12-31 16:14:41');
INSERT INTO `enrollments` VALUES (12, 5, 14, '2025-12-31 16:15:10');
INSERT INTO `enrollments` VALUES (13, 1, 15, '2026-01-04 16:34:15');
INSERT INTO `enrollments` VALUES (14, 2, 16, '2026-01-04 16:34:15');
INSERT INTO `enrollments` VALUES (15, 2, 17, '2026-01-04 16:34:16');
INSERT INTO `enrollments` VALUES (16, 2, 18, '2026-01-04 16:34:16');
INSERT INTO `enrollments` VALUES (17, 2, 19, '2026-01-04 16:34:16');
INSERT INTO `enrollments` VALUES (18, 2, 20, '2026-01-04 16:34:16');
INSERT INTO `enrollments` VALUES (19, 2, 21, '2026-01-04 16:34:16');
INSERT INTO `enrollments` VALUES (20, 2, 22, '2026-01-04 16:34:17');
INSERT INTO `enrollments` VALUES (21, 2, 23, '2026-01-04 16:34:17');
INSERT INTO `enrollments` VALUES (31, 1, 24, '2026-01-04 17:31:26');
INSERT INTO `enrollments` VALUES (32, 1, 25, '2026-01-04 17:31:26');
INSERT INTO `enrollments` VALUES (33, 1, 26, '2026-01-04 17:31:26');
INSERT INTO `enrollments` VALUES (34, 1, 27, '2026-01-04 17:31:26');
INSERT INTO `enrollments` VALUES (35, 1, 28, '2026-01-04 17:31:26');
INSERT INTO `enrollments` VALUES (36, 1, 29, '2026-01-04 17:31:26');
INSERT INTO `enrollments` VALUES (37, 1, 30, '2026-01-04 17:31:26');
INSERT INTO `enrollments` VALUES (38, 1, 31, '2026-01-04 17:31:26');
INSERT INTO `enrollments` VALUES (39, 1, 32, '2026-01-04 17:31:26');
INSERT INTO `enrollments` VALUES (40, 1, 33, '2026-01-04 17:31:26');
INSERT INTO `enrollments` VALUES (41, 1, 34, '2026-01-04 17:31:26');
INSERT INTO `enrollments` VALUES (42, 1, 35, '2026-01-04 17:31:26');
INSERT INTO `enrollments` VALUES (43, 1, 36, '2026-01-04 17:31:27');
INSERT INTO `enrollments` VALUES (44, 1, 37, '2026-01-04 17:31:27');
INSERT INTO `enrollments` VALUES (45, 1, 38, '2026-01-04 17:31:27');
INSERT INTO `enrollments` VALUES (46, 1, 39, '2026-01-04 17:31:27');
INSERT INTO `enrollments` VALUES (47, 1, 40, '2026-01-04 17:31:27');
INSERT INTO `enrollments` VALUES (48, 1, 41, '2026-01-04 17:31:28');
INSERT INTO `enrollments` VALUES (49, 1, 42, '2026-01-04 17:31:28');
INSERT INTO `enrollments` VALUES (50, 1, 43, '2026-01-04 17:31:28');
INSERT INTO `enrollments` VALUES (51, 1, 44, '2026-01-04 17:31:28');
INSERT INTO `enrollments` VALUES (52, 1, 45, '2026-01-04 17:31:28');
INSERT INTO `enrollments` VALUES (53, 1, 46, '2026-01-04 17:31:29');
INSERT INTO `enrollments` VALUES (54, 1, 47, '2026-01-04 17:31:29');
INSERT INTO `enrollments` VALUES (55, 1, 48, '2026-01-04 17:31:29');
INSERT INTO `enrollments` VALUES (56, 1, 49, '2026-01-04 17:31:29');
INSERT INTO `enrollments` VALUES (57, 1, 50, '2026-01-04 17:31:29');
INSERT INTO `enrollments` VALUES (58, 1, 51, '2026-01-04 17:31:30');
INSERT INTO `enrollments` VALUES (59, 1, 52, '2026-01-04 17:31:30');
INSERT INTO `enrollments` VALUES (60, 1, 53, '2026-01-04 17:31:30');
INSERT INTO `enrollments` VALUES (61, 1, 54, '2026-01-04 17:31:30');
INSERT INTO `enrollments` VALUES (62, 6, 56, '2026-01-19 10:26:29');
INSERT INTO `enrollments` VALUES (63, 6, 57, '2026-01-19 10:26:29');
INSERT INTO `enrollments` VALUES (64, 6, 58, '2026-01-19 10:26:29');
INSERT INTO `enrollments` VALUES (65, 6, 59, '2026-01-19 10:26:29');
INSERT INTO `enrollments` VALUES (66, 6, 60, '2026-01-19 10:26:30');
INSERT INTO `enrollments` VALUES (67, 6, 61, '2026-01-19 10:26:30');
INSERT INTO `enrollments` VALUES (68, 6, 62, '2026-01-19 10:26:30');
INSERT INTO `enrollments` VALUES (69, 6, 63, '2026-01-19 10:26:30');
INSERT INTO `enrollments` VALUES (70, 6, 64, '2026-01-19 10:26:31');
INSERT INTO `enrollments` VALUES (71, 6, 65, '2026-01-19 10:26:31');
INSERT INTO `enrollments` VALUES (72, 6, 66, '2026-01-19 10:26:31');
INSERT INTO `enrollments` VALUES (73, 6, 67, '2026-01-19 10:26:31');
INSERT INTO `enrollments` VALUES (74, 6, 68, '2026-01-19 10:26:32');
INSERT INTO `enrollments` VALUES (75, 6, 69, '2026-01-19 10:26:32');
INSERT INTO `enrollments` VALUES (76, 6, 70, '2026-01-19 10:26:32');
INSERT INTO `enrollments` VALUES (77, 6, 71, '2026-01-19 10:26:32');
INSERT INTO `enrollments` VALUES (78, 6, 72, '2026-01-19 10:26:32');
INSERT INTO `enrollments` VALUES (79, 6, 73, '2026-01-19 10:26:33');
INSERT INTO `enrollments` VALUES (80, 6, 74, '2026-01-19 10:26:33');
INSERT INTO `enrollments` VALUES (81, 6, 75, '2026-01-19 10:26:33');
INSERT INTO `enrollments` VALUES (82, 6, 76, '2026-01-19 10:26:33');
INSERT INTO `enrollments` VALUES (83, 6, 77, '2026-01-19 10:26:33');
INSERT INTO `enrollments` VALUES (84, 6, 78, '2026-01-19 10:26:34');
INSERT INTO `enrollments` VALUES (85, 6, 79, '2026-01-19 10:26:34');
INSERT INTO `enrollments` VALUES (86, 6, 80, '2026-01-19 10:26:34');
INSERT INTO `enrollments` VALUES (87, 6, 81, '2026-01-19 10:26:34');
INSERT INTO `enrollments` VALUES (88, 6, 82, '2026-01-19 10:26:34');
INSERT INTO `enrollments` VALUES (89, 6, 83, '2026-01-19 10:26:35');
INSERT INTO `enrollments` VALUES (90, 6, 84, '2026-01-19 10:26:35');
INSERT INTO `enrollments` VALUES (91, 6, 85, '2026-01-19 10:26:35');
INSERT INTO `enrollments` VALUES (92, 6, 86, '2026-01-19 10:26:35');
INSERT INTO `enrollments` VALUES (93, 6, 87, '2026-01-19 10:26:35');
INSERT INTO `enrollments` VALUES (94, 6, 88, '2026-01-19 10:26:36');
INSERT INTO `enrollments` VALUES (95, 6, 89, '2026-01-19 10:26:36');
INSERT INTO `enrollments` VALUES (96, 6, 90, '2026-01-19 10:26:36');
INSERT INTO `enrollments` VALUES (97, 6, 91, '2026-01-19 10:26:36');
INSERT INTO `enrollments` VALUES (98, 6, 92, '2026-01-19 10:26:36');
INSERT INTO `enrollments` VALUES (99, 6, 93, '2026-01-19 10:26:37');
INSERT INTO `enrollments` VALUES (100, 6, 94, '2026-01-19 10:26:37');
INSERT INTO `enrollments` VALUES (101, 6, 95, '2026-01-19 10:26:37');
INSERT INTO `enrollments` VALUES (102, 6, 96, '2026-01-19 10:26:37');
INSERT INTO `enrollments` VALUES (103, 6, 97, '2026-01-19 10:26:37');
INSERT INTO `enrollments` VALUES (104, 6, 98, '2026-01-19 10:26:38');
INSERT INTO `enrollments` VALUES (105, 6, 99, '2026-01-19 10:26:38');
INSERT INTO `enrollments` VALUES (106, 6, 100, '2026-01-19 10:26:38');
INSERT INTO `enrollments` VALUES (107, 6, 101, '2026-01-19 10:26:38');
INSERT INTO `enrollments` VALUES (108, 6, 102, '2026-01-19 10:26:38');
INSERT INTO `enrollments` VALUES (109, 6, 103, '2026-01-19 10:26:39');
INSERT INTO `enrollments` VALUES (110, 6, 104, '2026-01-19 10:26:39');
INSERT INTO `enrollments` VALUES (111, 6, 105, '2026-01-19 10:26:39');

-- ----------------------------
-- Table structure for exam_answers
-- ----------------------------
DROP TABLE IF EXISTS `exam_answers`;
CREATE TABLE `exam_answers`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `record_id` int NOT NULL,
  `question_id` int NOT NULL,
  `answer_content` json NULL,
  `is_correct` tinyint(1) NULL DEFAULT NULL,
  `score` int NULL DEFAULT NULL,
  `teacher_feedback` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `record_id`(`record_id` ASC) USING BTREE,
  INDEX `question_id`(`question_id` ASC) USING BTREE,
  INDEX `ix_exam_answers_id`(`id` ASC) USING BTREE,
  CONSTRAINT `exam_answers_ibfk_1` FOREIGN KEY (`record_id`) REFERENCES `exam_records` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `exam_answers_ibfk_2` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 35 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of exam_answers
-- ----------------------------
INSERT INTO `exam_answers` VALUES (1, 1, 2, '\"A\"', 1, 2, NULL);
INSERT INTO `exam_answers` VALUES (2, 1, 3, '\"B\"', 1, 2, NULL);
INSERT INTO `exam_answers` VALUES (3, 1, 8, '\"\"', 0, 0, NULL);
INSERT INTO `exam_answers` VALUES (4, 1, 9, '\"2,3\"', 1, 2, '');
INSERT INTO `exam_answers` VALUES (5, 1, 10, '\"11,12\"', 1, 2, '');
INSERT INTO `exam_answers` VALUES (6, 1, 11, '\"我不知道\"', 0, 2, '');
INSERT INTO `exam_answers` VALUES (25, 2, 5, '[\"A\", \"B\"]', 0, 0, NULL);
INSERT INTO `exam_answers` VALUES (26, 2, 9, '\"2, 3\"', 1, 2, NULL);
INSERT INTO `exam_answers` VALUES (27, 2, 10, '\"11, 12\"', 1, 2, NULL);
INSERT INTO `exam_answers` VALUES (28, 3, 1, '\"B\"', 1, 2, NULL);
INSERT INTO `exam_answers` VALUES (29, 3, 4, '\"B\"', 1, 2, NULL);
INSERT INTO `exam_answers` VALUES (30, 3, 6, '[\"B\", \"A\", \"C\", \"D\", \"E\", \"F\"]', 1, 2, NULL);
INSERT INTO `exam_answers` VALUES (31, 4, 2, '\"\"', 0, 0, NULL);
INSERT INTO `exam_answers` VALUES (32, 4, 5, '[]', 0, 0, NULL);
INSERT INTO `exam_answers` VALUES (33, 4, 9, '\"\"', 0, 0, NULL);
INSERT INTO `exam_answers` VALUES (34, 4, 10, '\"\"', 0, 0, NULL);

-- ----------------------------
-- Table structure for exam_questions
-- ----------------------------
DROP TABLE IF EXISTS `exam_questions`;
CREATE TABLE `exam_questions`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `exam_id` int NOT NULL,
  `question_id` int NOT NULL,
  `score` int NULL DEFAULT NULL,
  `sort_order` int NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `exam_id`(`exam_id` ASC) USING BTREE,
  INDEX `question_id`(`question_id` ASC) USING BTREE,
  INDEX `ix_exam_questions_id`(`id` ASC) USING BTREE,
  CONSTRAINT `exam_questions_ibfk_1` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `exam_questions_ibfk_2` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 56 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of exam_questions
-- ----------------------------
INSERT INTO `exam_questions` VALUES (22, 6, 9, 2, 0);
INSERT INTO `exam_questions` VALUES (23, 6, 10, 2, 1);
INSERT INTO `exam_questions` VALUES (24, 6, 5, 2, 2);
INSERT INTO `exam_questions` VALUES (25, 7, 1, 2, 0);
INSERT INTO `exam_questions` VALUES (26, 7, 4, 2, 1);
INSERT INTO `exam_questions` VALUES (27, 7, 6, 2, 2);
INSERT INTO `exam_questions` VALUES (28, 8, 2, 5, 0);
INSERT INTO `exam_questions` VALUES (29, 8, 3, 5, 1);
INSERT INTO `exam_questions` VALUES (30, 8, 4, 5, 2);
INSERT INTO `exam_questions` VALUES (31, 8, 5, 5, 3);
INSERT INTO `exam_questions` VALUES (36, 10, 13, 10, 0);
INSERT INTO `exam_questions` VALUES (37, 10, 14, 10, 1);
INSERT INTO `exam_questions` VALUES (38, 10, 15, 10, 2);
INSERT INTO `exam_questions` VALUES (39, 10, 16, 10, 3);
INSERT INTO `exam_questions` VALUES (40, 10, 17, 10, 4);
INSERT INTO `exam_questions` VALUES (41, 10, 19, 10, 5);
INSERT INTO `exam_questions` VALUES (42, 10, 18, 10, 6);
INSERT INTO `exam_questions` VALUES (43, 10, 20, 10, 7);
INSERT INTO `exam_questions` VALUES (44, 10, 21, 10, 8);
INSERT INTO `exam_questions` VALUES (45, 10, 22, 10, 9);
INSERT INTO `exam_questions` VALUES (46, 2, 2, 2, 0);
INSERT INTO `exam_questions` VALUES (47, 2, 3, 2, 1);
INSERT INTO `exam_questions` VALUES (48, 2, 10, 2, 2);
INSERT INTO `exam_questions` VALUES (49, 2, 9, 2, 3);
INSERT INTO `exam_questions` VALUES (50, 2, 8, 2, 4);
INSERT INTO `exam_questions` VALUES (51, 2, 11, 2, 5);
INSERT INTO `exam_questions` VALUES (52, 9, 2, 5, 0);
INSERT INTO `exam_questions` VALUES (53, 9, 5, 5, 1);
INSERT INTO `exam_questions` VALUES (54, 9, 9, 5, 2);
INSERT INTO `exam_questions` VALUES (55, 9, 10, 5, 3);

-- ----------------------------
-- Table structure for exam_records
-- ----------------------------
DROP TABLE IF EXISTS `exam_records`;
CREATE TABLE `exam_records`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `exam_id` int NOT NULL,
  `student_id` int NOT NULL,
  `start_time` datetime NULL DEFAULT NULL,
  `submit_time` datetime NULL DEFAULT NULL,
  `status` int NULL DEFAULT NULL,
  `objective_score` int NULL DEFAULT NULL,
  `subjective_score` int NULL DEFAULT NULL,
  `total_score` int NULL DEFAULT NULL,
  `cheat_count` int NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `exam_id`(`exam_id` ASC) USING BTREE,
  INDEX `student_id`(`student_id` ASC) USING BTREE,
  INDEX `ix_exam_records_id`(`id` ASC) USING BTREE,
  CONSTRAINT `exam_records_ibfk_1` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `exam_records_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of exam_records
-- ----------------------------
INSERT INTO `exam_records` VALUES (1, 2, 1, '2026-01-13 16:28:32', '2026-01-13 16:49:13', 2, 4, 2, 6, 1, '2026-01-13 16:28:32', '2026-01-19 15:22:49');
INSERT INTO `exam_records` VALUES (2, 6, 22, '2026-01-14 15:39:06', '2026-01-14 15:39:30', 2, 4, 0, 4, 2, '2026-01-14 15:39:06', '2026-01-14 15:42:36');
INSERT INTO `exam_records` VALUES (3, 7, 1, '2026-01-15 13:47:50', '2026-01-15 13:48:13', 2, 6, 0, 6, 0, '2026-01-15 13:47:50', '2026-01-15 13:48:12');
INSERT INTO `exam_records` VALUES (4, 9, 1, '2026-01-19 17:59:15', '2026-01-19 17:59:52', 2, 0, 0, 0, 3, '2026-01-19 17:59:15', '2026-01-19 17:59:52');

-- ----------------------------
-- Table structure for exams
-- ----------------------------
DROP TABLE IF EXISTS `exams`;
CREATE TABLE `exams`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `teacher_id` int NOT NULL,
  `start_time` datetime NULL DEFAULT NULL,
  `end_time` datetime NULL DEFAULT NULL,
  `duration` int NULL DEFAULT NULL,
  `pass_score` int NULL DEFAULT NULL,
  `total_score` int NULL DEFAULT NULL,
  `status` int NULL DEFAULT NULL,
  `class_ids` json NULL,
  `mode` int NULL DEFAULT NULL,
  `random_config` json NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `teacher_id`(`teacher_id` ASC) USING BTREE,
  INDEX `ix_exams_id`(`id` ASC) USING BTREE,
  CONSTRAINT `exams_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of exams
-- ----------------------------
INSERT INTO `exams` VALUES (2, '2025期中考', 2, '2026-01-13 00:00:00', '2026-01-19 00:00:00', 120, 7, 12, 1, '[1]', 1, NULL, '2026-01-13 14:25:46', '2026-01-19 16:16:58');
INSERT INTO `exams` VALUES (6, '填空题测试', 2, '2026-01-14 00:00:00', '2026-01-14 16:00:00', 60, 3, 6, 1, '[2]', 1, NULL, '2026-01-14 15:30:20', '2026-01-14 17:12:59');
INSERT INTO `exams` VALUES (7, '测试', 2, '2026-01-15 00:00:00', '2026-01-15 13:00:00', 60, 3, 6, 1, '[1]', 1, NULL, '2026-01-15 11:46:52', '2026-01-15 11:46:52');
INSERT INTO `exams` VALUES (8, '手动组卷测试', 2, '2026-01-15 00:00:00', '2026-01-16 00:00:00', 60, 12, 20, 1, '[3]', 1, NULL, '2026-01-15 13:45:26', '2026-01-15 13:45:26');
INSERT INTO `exams` VALUES (9, '随机组卷测试', 2, '2026-01-15 00:00:00', '2026-01-20 00:00:00', 60, 12, 20, 1, '[2, 1]', 1, NULL, '2026-01-15 13:46:30', '2026-01-19 17:52:15');
INSERT INTO `exams` VALUES (10, '2025跨境电商期中考', 55, '2026-01-19 00:00:00', '2026-01-20 00:00:00', 60, 60, 100, 1, '[6]', 1, NULL, '2026-01-19 15:19:03', '2026-01-19 15:19:03');

-- ----------------------------
-- Table structure for questions
-- ----------------------------
DROP TABLE IF EXISTS `questions`;
CREATE TABLE `questions`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `teacher_id` int NOT NULL,
  `type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'single, multiple, judge, blank, essay',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '题干',
  `options` json NULL COMMENT '选项JSON',
  `answer` json NOT NULL COMMENT '参考答案JSON',
  `analysis` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '解析',
  `difficulty` int NULL DEFAULT 1 COMMENT '1易 2中 3难',
  `tags` json NULL COMMENT '标签JSON',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_questions_teacher_id`(`teacher_id` ASC) USING BTREE,
  INDEX `ix_questions_type`(`type` ASC) USING BTREE,
  CONSTRAINT `fk_questions_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 24 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of questions
-- ----------------------------
INSERT INTO `questions` VALUES (1, 2, 'single', '在 Shopee 平台的搜索广告（Keyword Ads）中，决定商品展示排名（Ad Rank）的核心因素是以下哪一项？', '[{\"text\": \"仅取决于卖家的点击出价（Bid Price）\", \"label\": \"A\"}, {\"text\": \"质量评分（Quality Score）与点击出价（Bid Price）的乘积\", \"label\": \"B\"}, {\"text\": \"店铺的整体粉丝数量与好评率\", \"label\": \"C\"}, {\"text\": \"商品的库存数量与发货速度\", \"label\": \"D\"}]', '\"B\"', 'Shopee 的广告排名并非单纯的“价高者得”，而是采用 排名 = 质量评分 × 出价 的机制。其中，质量评分受点击率（CTR）、转化率（CR）以及商品相关性的影响。这意味着卖家可以通过优化商品图片和标题提高质量分，从而以更低的出价获得靠前的排名。', 2, '[\"搜索广告\"]', '2026-01-12 14:50:29', '2026-01-12 14:50:29');
INSERT INTO `questions` VALUES (2, 2, 'single', 'Shopee 平台的 SLS 物流全称是什么？', '[{\"text\": \"Shopee Logistics Service\", \"label\": \"A\"}, {\"text\": \"Shopee Line Service\", \"label\": \"B\"}, {\"text\": \"Smart Logistics System\", \"label\": \"C\"}, {\"text\": \"Super Logistics Shopee\", \"label\": \"D\"}]', '\"A\"', 'SLS 是 Shopee 自有跨境物流服务。', 1, '[\"物流基础\"]', '2026-01-12 15:16:03', '2026-01-12 15:16:03');
INSERT INTO `questions` VALUES (3, 2, 'single', '搜索广告中，决定商品排名的核心公式是？', '[{\"text\": \"出价 + 转化率\", \"label\": \"A\"}, {\"text\": \"出价 × 质量得分\", \"label\": \"B\"}, {\"text\": \"仅取决于出价\", \"label\": \"C\"}, {\"text\": \"点击量 × 出价\", \"label\": \"D\"}]', '\"B\"', '排名由点击出价和质量得分（CTR、相关性等）共同决定。', 2, '[\"广告优化\"]', '2026-01-12 15:16:03', '2026-01-12 15:16:03');
INSERT INTO `questions` VALUES (4, 2, 'single', '卖家因违反上架规则（如重复刊登）获得的惩罚计分，会在何时清零？', '[{\"text\": \"每个月月底\", \"label\": \"A\"}, {\"text\": \"每季度第一个周一\", \"label\": \"B\"}, {\"text\": \"获得计分后的第28天\", \"label\": \"C\"}, {\"text\": \"每年12月31日\", \"label\": \"D\"}]', '\"B\"', '计分按季度循环计算，每季度第一个周一重置。', 2, '[\"卖家表现\"]', '2026-01-12 15:16:03', '2026-01-12 15:16:03');
INSERT INTO `questions` VALUES (5, 2, 'multiple', '以下哪些因素会直接影响商品的“质量得分”？', '[{\"text\": \"商品标题相关性\", \"label\": \"A\"}, {\"text\": \"图片美观度/点击率\", \"label\": \"B\"}, {\"text\": \"店铺历史表现\", \"label\": \"C\"}, {\"text\": \"客服回复速度\", \"label\": \"D\"}]', '[\"A\", \"B\", \"C\"]', '质量得分主要由相关性、点击率（CTR）及店铺/商品表现构成。', 3, '[\"广告权重\"]', '2026-01-12 15:16:03', '2026-01-12 15:16:03');
INSERT INTO `questions` VALUES (6, 2, 'multiple', 'Shopee 严禁销售的“禁售品”通常包括哪些？', '[{\"text\": \"易燃易爆品\", \"label\": \"A\"}, {\"text\": \"假冒伪劣产品\", \"label\": \"B\"}, {\"text\": \"当地国家货币\", \"label\": \"C\"}, {\"text\": \"成人用品（部分站点限制）\", \"label\": \"D\"}, {\"text\": \"成人用品（部分站点限制）\", \"label\": \"E\"}, {\"text\": \"成人用品（部分站点限制）\", \"label\": \"F\"}]', '[\"A\", \"B\", \"C\", \"D\", \"E\", \"F\"]', '禁运品和侵权产品是所有站点严格禁止的。', 1, '[\"合规运营\"]', '2026-01-12 15:16:03', '2026-01-12 15:16:03');
INSERT INTO `questions` VALUES (7, 2, 'judge', '在 Shopee 聊聊中，卖家可以引导买家到 WhatsApp 进行私下交易。', '[]', 'false', '引导线下交易会导致店铺扣分甚至永久封禁。', 1, '[\"平台规范\"]', '2026-01-12 15:16:03', '2026-01-12 15:16:03');
INSERT INTO `questions` VALUES (8, 2, 'judge', '商品设置了预售（Pre-order）后，该商品将不再享有流量扶持。', '[]', 'false', '虽然预售比例过高会限单，但单品预售并不直接等于零流量。', 2, '[\"流量规则\"]', '2026-01-12 15:16:03', '2026-01-12 15:16:03');
INSERT INTO `questions` VALUES (9, 2, 'blank', 'Shopee 的订单履约期限（DTS）通常设置为 ___ 到 ___ 个工作日。', '[]', '\"2, 3\"', '现货 DTS 为 2个工作日，预售为 3-10个工作日。', 1, '[\"发货时效\"]', '2026-01-12 15:16:03', '2026-01-12 15:16:03');
INSERT INTO `questions` VALUES (10, 2, 'blank', '东南亚市场中，最大的移动电商大促节点通常是双 ___ 大促。', '[]', '\"11, 12\"', '11.11 和 12.12 是全平台流量最高的日子。', 1, '[\"平台大促\"]', '2026-01-12 15:16:03', '2026-01-12 15:16:03');
INSERT INTO `questions` VALUES (11, 2, 'essay', '请简述如何通过“加价购”（Add-on Deal）提升客单价？', '[]', '\"\"', '答：通过主商品搭配相关附属商品并给予折扣，引导买家凑单购买。', 2, '[\"营销工具\"]', '2026-01-12 15:16:03', '2026-01-12 15:16:03');
INSERT INTO `questions` VALUES (12, 2, 'essay', '如果店铺因延迟发货率（LSR）过高导致扣分，应如何优化？', '[]', '\"\"', '答：盘点库存确保现货、优化供应链、及时转预售、提高仓库打包效率。', 3, '[\"店铺运维\"]', '2026-01-12 15:16:03', '2026-01-12 15:16:03');
INSERT INTO `questions` VALUES (13, 55, 'single', 'Shopee 平台的 SLS 物流全称是什么？', '[{\"text\": \"Shopee Logistics Service\", \"label\": \"A\"}, {\"text\": \"Shopee Line Service\", \"label\": \"B\"}, {\"text\": \"Smart Logistics System\", \"label\": \"C\"}, {\"text\": \"Super Logistics Shopee\", \"label\": \"D\"}]', '\"A\"', 'SLS 是 Shopee 自有跨境物流服务。', 1, '[\"物流基础\"]', '2026-01-19 14:41:19', '2026-01-19 14:41:19');
INSERT INTO `questions` VALUES (14, 55, 'single', '搜索广告中，决定商品排名的核心公式是？', '[{\"text\": \"出价 + 转化率\", \"label\": \"A\"}, {\"text\": \"出价 × 质量得分\", \"label\": \"B\"}, {\"text\": \"仅取决于出价\", \"label\": \"C\"}, {\"text\": \"点击量 × 出价\", \"label\": \"D\"}]', '\"B\"', '排名由点击出价和质量得分（CTR、相关性等）共同决定。', 2, '[\"广告优化\"]', '2026-01-19 14:41:19', '2026-01-19 14:41:19');
INSERT INTO `questions` VALUES (15, 55, 'single', '卖家因违反上架规则（如重复刊登）获得的惩罚计分，会在何时清零？', '[{\"text\": \"每个月月底\", \"label\": \"A\"}, {\"text\": \"每季度第一个周一\", \"label\": \"B\"}, {\"text\": \"获得计分后的第28天\", \"label\": \"C\"}, {\"text\": \"每年12月31日\", \"label\": \"D\"}]', '\"B\"', '计分按季度循环计算，每季度第一个周一重置。', 2, '[\"卖家表现\"]', '2026-01-19 14:41:19', '2026-01-19 14:41:19');
INSERT INTO `questions` VALUES (16, 55, 'multiple', '以下哪些因素会直接影响商品的“质量得分”？', '[{\"text\": \"商品标题相关性\", \"label\": \"A\"}, {\"text\": \"图片美观度/点击率\", \"label\": \"B\"}, {\"text\": \"店铺历史表现\", \"label\": \"C\"}, {\"text\": \"客服回复速度\", \"label\": \"D\"}]', '[\"A\", \"B\", \"C\"]', '质量得分主要由相关性、点击率（CTR）及店铺/商品表现构成。', 3, '[\"广告权重\"]', '2026-01-19 14:41:19', '2026-01-19 14:41:19');
INSERT INTO `questions` VALUES (17, 55, 'multiple', 'Shopee 严禁销售的“禁售品”通常包括哪些？', '[{\"text\": \"易燃易爆品\", \"label\": \"A\"}, {\"text\": \"假冒伪劣产品\", \"label\": \"B\"}, {\"text\": \"当地国家货币\", \"label\": \"C\"}, {\"text\": \"成人用品（部分站点限制）\", \"label\": \"D\"}, {\"text\": \"成人用品（部分站点限制）\", \"label\": \"E\"}, {\"text\": \"成人用品（部分站点限制）\", \"label\": \"F\"}]', '[\"A\", \"B\", \"C\", \"D\", \"E\", \"F\"]', '禁运品和侵权产品是所有站点严格禁止的。', 1, '[\"合规运营\"]', '2026-01-19 14:41:19', '2026-01-19 14:41:19');
INSERT INTO `questions` VALUES (18, 55, 'judge', '在 Shopee 聊聊中，卖家可以引导买家到 WhatsApp 进行私下交易。', '[]', 'false', '引导线下交易会导致店铺扣分甚至永久封禁。', 1, '[\"平台规范\"]', '2026-01-19 14:41:19', '2026-01-19 14:41:19');
INSERT INTO `questions` VALUES (19, 55, 'judge', '商品设置了预售（Pre-order）后，该商品将不再享有流量扶持。', '[]', 'false', '虽然预售比例过高会限单，但单品预售并不直接等于零流量。', 2, '[\"流量规则\"]', '2026-01-19 14:41:19', '2026-01-19 14:41:19');
INSERT INTO `questions` VALUES (20, 55, 'blank', 'Shopee 的订单履约期限（DTS）通常设置为 ___ 到 ___ 个工作日。', '[]', '\"2, 3\"', '现货 DTS 为 2个工作日，预售为 3-10个工作日。', 1, '[\"发货时效\"]', '2026-01-19 14:41:19', '2026-01-19 14:41:19');
INSERT INTO `questions` VALUES (21, 55, 'blank', '东南亚市场中，最大的移动电商大促节点通常是双 ___ 大促。', '[]', '\"11, 12\"', '11.11 和 12.12 是全平台流量最高的日子。', 1, '[\"平台大促\"]', '2026-01-19 14:41:19', '2026-01-19 14:41:19');
INSERT INTO `questions` VALUES (22, 55, 'essay', '请简述如何通过“加价购”（Add-on Deal）提升客单价？', '[]', '\"\"', '答：通过主商品搭配相关附属商品并给予折扣，引导买家凑单购买。', 2, '[\"营销工具\"]', '2026-01-19 14:41:19', '2026-01-19 14:41:19');
INSERT INTO `questions` VALUES (23, 55, 'essay', '如果店铺因延迟发货率（LSR）过高导致扣分，应如何优化？', '[]', '\"\"', '答：盘点库存确保现货、优化供应链、及时转预售、提高仓库打包效率。', 3, '[\"店铺运维\"]', '2026-01-19 14:41:19', '2026-01-19 14:41:19');

-- ----------------------------
-- Table structure for student_learning_progress
-- ----------------------------
DROP TABLE IF EXISTS `student_learning_progress`;
CREATE TABLE `student_learning_progress`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL COMMENT '学生ID',
  `lesson_id` int NOT NULL COMMENT '课时ID',
  `status` int NULL DEFAULT 0 COMMENT '0:未开始, 1:进行中, 2:已完成',
  `last_position` int NULL DEFAULT 1 COMMENT '最后阅读页码',
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_student_lesson`(`student_id` ASC, `lesson_id` ASC) USING BTREE,
  INDEX `fk_slp_lesson`(`lesson_id` ASC) USING BTREE,
  CONSTRAINT `fk_slp_lesson` FOREIGN KEY (`lesson_id`) REFERENCES `course_lessons` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_slp_student` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of student_learning_progress
-- ----------------------------
INSERT INTO `student_learning_progress` VALUES (1, 1, 201, 2, 1, '2026-01-06 15:35:11');
INSERT INTO `student_learning_progress` VALUES (2, 1, 203, 2, 1, '2026-01-06 15:33:14');
INSERT INTO `student_learning_progress` VALUES (3, 1, 205, 2, 0, '2026-01-06 15:41:31');
INSERT INTO `student_learning_progress` VALUES (4, 1, 207, 2, 0, '2026-01-06 15:41:41');
INSERT INTO `student_learning_progress` VALUES (5, 1, 209, 2, 0, '2026-01-06 15:58:10');
INSERT INTO `student_learning_progress` VALUES (6, 1, 211, 1, 1, '2026-01-06 15:57:45');
INSERT INTO `student_learning_progress` VALUES (7, 8, 201, 2, 0, '2026-01-06 17:05:33');
INSERT INTO `student_learning_progress` VALUES (8, 8, 203, 1, 1, '2026-01-06 17:05:38');
INSERT INTO `student_learning_progress` VALUES (9, 15, 201, 2, 0, '2026-01-09 16:47:53');
INSERT INTO `student_learning_progress` VALUES (10, 105, 201, 1, 1, '2026-01-19 13:57:01');
INSERT INTO `student_learning_progress` VALUES (11, 15, 205, 2, 0, '2026-01-19 17:16:14');
INSERT INTO `student_learning_progress` VALUES (12, 15, 203, 1, 1, '2026-01-19 17:16:51');

-- ----------------------------
-- Table structure for student_profiles
-- ----------------------------
DROP TABLE IF EXISTS `student_profiles`;
CREATE TABLE `student_profiles`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '关联的用户ID',
  `real_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '真实姓名',
  `student_number` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '学号',
  `gender` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '保密' COMMENT '性别',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '联系电话',
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '头像URL',
  `intro` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '个人简介',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_sp_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `fk_sp_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '学生详细档案表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of student_profiles
-- ----------------------------
INSERT INTO `student_profiles` VALUES (1, 1, '张十一', '22014082032', '男', '18250636865', '/static/uploads/avatars/fa8f70d0-6ce0-4b90-853b-0bdb2919bcbe.png', NULL, '2026-01-04 14:23:33', '2026-01-04 15:39:00');
INSERT INTO `student_profiles` VALUES (2, 8, '张二', '22014082033', '保密', '18250636871', '/static/uploads/avatars/36c89a39-76e6-4973-8536-4ec4837ba50c.png', NULL, '2026-01-04 15:39:40', '2026-01-04 15:39:56');
INSERT INTO `student_profiles` VALUES (3, 15, '贾一', '22014083001', '保密', '13800000001', '/static/uploads/avatars/05958dc6-7eea-4f43-bd42-85beb748c40a.png', NULL, '2026-01-04 16:58:48', '2026-01-04 17:18:55');
INSERT INTO `student_profiles` VALUES (4, 18, '贾四', '22014083004', '保密', NULL, NULL, NULL, '2026-01-04 17:56:55', '2026-01-04 17:56:55');
INSERT INTO `student_profiles` VALUES (5, 32, '林九', '22014081009', '保密', NULL, NULL, NULL, '2026-01-07 17:51:58', '2026-01-07 17:51:58');
INSERT INTO `student_profiles` VALUES (6, 9, '张七', '22014082037', '保密', NULL, NULL, NULL, '2026-01-07 17:52:13', '2026-01-07 17:52:13');
INSERT INTO `student_profiles` VALUES (7, 5, '李四', '22014082034', '保密', NULL, NULL, NULL, '2026-01-07 17:52:31', '2026-01-07 17:52:31');
INSERT INTO `student_profiles` VALUES (8, 22, '贾八', '22014083008', '保密', NULL, NULL, NULL, '2026-01-14 15:38:59', '2026-01-14 15:38:59');
INSERT INTO `student_profiles` VALUES (9, 10, '张四', '22014082021', '保密', NULL, NULL, NULL, '2026-01-16 15:49:02', '2026-01-16 15:49:02');
INSERT INTO `student_profiles` VALUES (10, 105, '50', '20250119050', '保密', NULL, NULL, NULL, '2026-01-19 13:56:35', '2026-01-19 13:56:35');

-- ----------------------------
-- Table structure for student_submissions
-- ----------------------------
DROP TABLE IF EXISTS `student_submissions`;
CREATE TABLE `student_submissions`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `assignment_id` int NOT NULL COMMENT '关联的作业ID',
  `student_id` int NOT NULL COMMENT '学生ID',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '提交内容(富文本/图片URL)',
  `score` int NULL DEFAULT NULL COMMENT '分数(0-100)',
  `feedback` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '老师评语',
  `status` int NULL DEFAULT 0 COMMENT '0:已提交/未批改, 1:已批改, 2:被打回',
  `submitted_at` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
  `graded_at` datetime NULL DEFAULT NULL COMMENT '批改时间',
  `annotated_content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '带有批注高亮的HTML内容',
  `annotations` json NULL COMMENT '批注列表数据',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_student_assign`(`assignment_id` ASC, `student_id` ASC) USING BTREE,
  INDEX `fk_sub_student`(`student_id` ASC) USING BTREE,
  CONSTRAINT `fk_sub_assign` FOREIGN KEY (`assignment_id`) REFERENCES `class_assignments` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_sub_student` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 9 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '学生作业提交表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of student_submissions
-- ----------------------------
INSERT INTO `student_submissions` VALUES (1, 1, 1, '\n\n![截图](/static/uploads/common/c77b39d8-4e52-4b65-814f-389210951c65.png)\n', 90, '', 2, '2026-01-09 10:39:57', '2026-01-09 15:03:22', NULL, NULL);
INSERT INTO `student_submissions` VALUES (2, 3, 1, '\n\n![截图](/static/uploads/common/c77b39d8-4e52-4b65-814f-389210951c65.png)\n', 80, '请补充细节。', 2, '2026-01-09 10:40:31', '2026-01-09 16:15:37', '<p><img src=\"/static/uploads/common/c77b39d8-4e52-4b65-814f-389210951c65.png\" alt=\"截图\">\r\n<span class=\"highlight-marker flash-highlight\" data-id=\"note-1767945062572\">配置</span><span class=\"highlight-marker\" data-id=\"note-1767944241875\"></span></p>\r\n', '[]');
INSERT INTO `student_submissions` VALUES (3, 5, 1, '完成首个商品上架\n完成首个商品上架\n完成首个商品上架\n完成首个商品上架\n\n![截图](/static/uploads/common/209dbd52-1577-46c9-9e75-172602c69a7e.png)', 60, '📷 图片不清晰，请重交。', 2, '2026-01-09 16:16:32', '2026-01-09 16:17:51', '<p><span class=\"highlight-marker\" data-id=\"note-1767946629852\">完成首个商品上架</span>\r\n完成首个商品上架\r\n完成首<span class=\"highlight-marker\" data-id=\"note-1767946665021\">个商品上</span>架\r\n完成首个商品上架</p>\r\n<p><img src=\"/static/uploads/common/209dbd52-1577-46c9-9e75-172602c69a7e.png\" alt=\"截图\"></p>\r\n', '[{\"id\": \"note-1767946629852\", \"text\": \"123123131231\"}, {\"id\": \"note-1767946665021\", \"text\": \"dasdasdasd\"}]');
INSERT INTO `student_submissions` VALUES (4, 5, 8, '完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架\n\n![截图](/static/uploads/common/f6d0169c-0f84-4b57-804b-7a637eb13396.png)', 80, '👍 做得很好！', 2, '2026-01-09 16:21:44', '2026-01-09 16:47:17', '<p>完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个<span class=\"highlight-marker\" data-id=\"note-1767948428518\">商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架完成首个商品上架</span></p>\n<p><img src=\"http://120.41.224.2:8000/static/uploads/common/f6d0169c-0f84-4b57-804b-7a637eb13396.png\" alt=\"截图\"></p>\n', '[{\"id\": \"note-1767948428518\", \"text\": \"很好\"}]');
INSERT INTO `student_submissions` VALUES (5, 5, 15, '123123131\n\n![截图](/static/uploads/common/98381303-3f04-4dcb-a588-ea46e0c1a1e4.png)', 99, '👍 做得很好！ 📷 图片不清晰，请重交。 📝 请补充更多细节。 💡 思路很有创意！', 2, '2026-01-09 16:48:22', '2026-01-12 09:43:52', '<p>123123131</p>\n<p><img src=\"/static/uploads/common/98381303-3f04-4dcb-a588-ea46e0c1a1e4.png\" alt=\"截图\"></p>\n', '[]');
INSERT INTO `student_submissions` VALUES (6, 8, 1, '\n\n![截图](/static/uploads/common/15aaefe2-1e2a-4919-a90c-0da90ee5e9aa.png)', 100, '📷 图片不清晰，请重交。', 2, '2026-01-12 13:51:32', '2026-01-12 13:53:56', '<p><img src=\"/static/uploads/common/15aaefe2-1e2a-4919-a90c-0da90ee5e9aa.png\" alt=\"截图\"></p>\n', '[]');
INSERT INTO `student_submissions` VALUES (7, 8, 15, 'sadadasdadsadad', NULL, NULL, 1, '2026-01-12 14:05:54', NULL, NULL, NULL);
INSERT INTO `student_submissions` VALUES (8, 10, 105, '\n步骤1：访问shopee官网，进入卖家中心\n步骤2：在注册界面，输入手机号注册，输入注册站当地手机号，例如，输入马来西亚手机号，接收并输入验证码以验证省份\n......\n![截图](/static/uploads/common/1f846366-07a2-45ff-a044-8684ed751155.png)', 70, '📝 请补充更多细节。', 2, '2026-01-19 13:59:25', '2026-01-19 14:13:28', '<p><span class=\"highlight-marker\" data-id=\"note-1768803130582\">步骤1：访问shopee官网，进入卖家中心</span>\n步骤2：在注册界面，输入手机号注册，输入注册站当地手机号，例如，输入马来西亚手机号，接收并输入验证码以验证省份\n......\n<img src=\"/static/uploads/common/1f846366-07a2-45ff-a044-8684ed751155.png\" alt=\"截图\"></p>\n', '[{\"id\": \"note-1768803130582\", \"text\": \"描述太过于简单\"}]');

-- ----------------------------
-- Table structure for teacher_course_access
-- ----------------------------
DROP TABLE IF EXISTS `teacher_course_access`;
CREATE TABLE `teacher_course_access`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `teacher_id` int NOT NULL COMMENT '教师ID',
  `course_id` int NOT NULL COMMENT '课程ID',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_teacher_course`(`teacher_id` ASC, `course_id` ASC) USING BTREE,
  INDEX `fk_tca_course`(`course_id` ASC) USING BTREE,
  CONSTRAINT `fk_tca_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_tca_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 15 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '教师课程权限表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of teacher_course_access
-- ----------------------------
INSERT INTO `teacher_course_access` VALUES (1, 2, 1, '2025-12-31 14:34:39');
INSERT INTO `teacher_course_access` VALUES (2, 2, 2, '2025-12-31 14:34:39');
INSERT INTO `teacher_course_access` VALUES (3, 2, 3, '2025-12-31 14:34:39');
INSERT INTO `teacher_course_access` VALUES (4, 2, 4, '2025-12-31 14:34:39');
INSERT INTO `teacher_course_access` VALUES (5, 2, 5, '2025-12-31 14:34:39');
INSERT INTO `teacher_course_access` VALUES (6, 2, 6, '2025-12-31 14:34:39');
INSERT INTO `teacher_course_access` VALUES (7, 4, 7, '2025-12-31 16:15:55');
INSERT INTO `teacher_course_access` VALUES (8, 4, 8, '2025-12-31 16:16:07');
INSERT INTO `teacher_course_access` VALUES (10, 55, 1, '2026-01-19 11:27:06');
INSERT INTO `teacher_course_access` VALUES (11, 55, 6, '2026-01-19 11:27:58');
INSERT INTO `teacher_course_access` VALUES (12, 2, 7, '2026-01-19 11:30:54');
INSERT INTO `teacher_course_access` VALUES (13, 55, 5, '2026-01-19 11:30:54');
INSERT INTO `teacher_course_access` VALUES (14, 55, 7, '2026-01-19 11:30:54');

-- ----------------------------
-- Table structure for teacher_profiles
-- ----------------------------
DROP TABLE IF EXISTS `teacher_profiles`;
CREATE TABLE `teacher_profiles`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '关联的用户ID',
  `real_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '真实姓名',
  `gender` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '性别',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '联系电话',
  `school` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '学校',
  `college` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '二级学院',
  `title` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '职称',
  `intro` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '个人简介',
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '头像URL',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `fk_tp_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of teacher_profiles
-- ----------------------------
INSERT INTO `teacher_profiles` VALUES (1, 2, '张三', '男', '18250636866', '南宁职业技术大学', '电子商务学院', '高级讲师', 'happy', '/static/uploads/avatars/1ee64345-a553-40ee-9ab1-c4e94ed90a75.png', '2025-12-29 11:21:18', '2025-12-31 15:21:35');
INSERT INTO `teacher_profiles` VALUES (2, 4, '陈一', '女', '18250636867', '颜值大学', '电子商务学院', '副教授', '专业的', '/static/uploads/avatars/e2a0be43-da33-4473-8961-8de59f9e6c21.png', '2025-12-31 16:13:06', '2025-12-31 16:14:09');
INSERT INTO `teacher_profiles` VALUES (3, 55, '张三三', '男', '18250636888', '南宁职业大学', '跨境电商学院', '高级讲师', '专业讲师', '/static/uploads/avatars/edea42c1-edb7-415c-9b67-239703c900aa.png', '2026-01-19 10:05:24', '2026-01-19 10:41:07');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `hashed_password` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `last_login` datetime NULL DEFAULT NULL,
  `comfyui_port` int NULL DEFAULT NULL,
  `full_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '真实姓名',
  `student_number` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '学号',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_users_username`(`username` ASC) USING BTREE,
  UNIQUE INDEX `comfyui_port`(`comfyui_port` ASC) USING BTREE,
  INDEX `ix_users_id`(`id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 106 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, '18250636865', '$2b$12$DM8zYSLV9Dt.jKfG4jykaetq3F4jmwGcSF6hJBaGDJBWQOc3ol9.y', 'student', 1, '2025-12-24 11:26:48', '2026-01-19 23:18:33', 8189, '张十一', '22014082032');
INSERT INTO `users` VALUES (2, '18250636866', '$2b$12$BbkngZyC3IaWM.cWcZKmauZxsyO3VZTe5P2mRqrbc75CC13xrMqIi', 'teacher', 1, '2025-12-24 11:27:14', '2026-01-19 23:17:18', NULL, NULL, NULL);
INSERT INTO `users` VALUES (4, '18250636867', '$2b$12$mVae3WIBNklVoxfL7qkLQ.ymZ9vRDq6vbwB2Za0cTStB1FO1DeYoa', 'teacher', 1, '2025-12-24 15:04:05', '2026-01-04 17:57:41', NULL, NULL, NULL);
INSERT INTO `users` VALUES (5, '18250636868', '$2b$12$LExgic9UmvpwwLtG5Gufs.08MAc8wx7EfZdv9CjYzn3QiLJnOUZdq', 'student', 1, '2025-12-24 17:26:36', '2026-01-07 17:52:32', 8190, '李四', '22014082034');
INSERT INTO `users` VALUES (6, '18250636969', '$2b$12$2bR.Xy.PQzAQDApnmWxdSeC.bIEs0C1kklBR751IoX4/tNFuUCyt2', 'student', 1, '2025-12-25 16:30:01', '2025-12-25 16:47:31', 8191, '王五', '22014082035');
INSERT INTO `users` VALUES (7, '18250636870', '$2b$12$JZUcksLjg6lZfnipDk.rS.Bqwgy4cH.dqmkuUgsvhQCSyw.c0wq9u', 'student', 1, '2025-12-25 16:34:04', '2025-12-25 16:51:53', 8192, '赵六', '22014082036');
INSERT INTO `users` VALUES (8, '18250636871', '$2b$12$HEqQ8pj0rTTBVi97d5wi2.juSlBWJnQ0AZaov6tlgvoxsf79j5j8m', 'student', 1, '2025-12-26 16:02:05', '2026-01-09 16:21:18', 8193, '张二', '22014082033');
INSERT INTO `users` VALUES (9, '18250636872', '$2b$12$ahylOLX4IYYfxTXg5xF72.D0V32UfPDd2WDs9B.gLUON2w0cDqw6q', 'student', 1, '2025-12-29 17:59:50', '2026-01-07 17:52:13', NULL, '张七', '22014082037');
INSERT INTO `users` VALUES (10, '18250636873', '$2b$12$oT0OqX4bUys/2obDlQtKCOxCvpB09s.AyOS83YbvQDq6GCXey5iWK', 'student', 1, '2025-12-30 14:20:52', '2026-01-16 15:49:02', NULL, '张四', '22014082021');
INSERT INTO `users` VALUES (11, '18250636874', '$2b$12$KXKRsdVENh0EmciRYox5K.OtcLcNoeR/26duy4z24TPhpj75uPe5.', 'student', 1, '2025-12-30 16:38:48', '2025-12-31 17:11:28', NULL, '张五', '22014082022');
INSERT INTO `users` VALUES (12, '18250636875', '$2b$12$pq9nEyWa41m4WKR/v.PON.artWlJPlEFgOB0sw5w.SrK0NsIfBEYG', 'student', 1, '2025-12-31 16:11:05', '2025-12-31 17:12:02', NULL, '张八', '22014082023');
INSERT INTO `users` VALUES (13, '18250636876', '$2b$12$NRSQIoCDK7ZW.1HqSy3C8uecojj7O2aFa1YX0ZMWMQ95sbbZ9u28K', 'student', 1, '2025-12-31 16:14:41', NULL, NULL, '张九', '22014082024');
INSERT INTO `users` VALUES (14, '18250636877', '$2b$12$4tZqq/x/k4LNU3hXUckHHeCkbCCIU7sN1Tab07dRj127smk8Q0a96', 'student', 1, '2025-12-31 16:15:10', NULL, NULL, '张十', '22014082025');
INSERT INTO `users` VALUES (15, '13800000001', '$2b$12$iCtsBwN3Pr72doOlHKNShuyQSHuCvsBn6mgY3Pl4dfTgu0vuHDVo2', 'student', 1, '2026-01-04 16:34:15', '2026-01-19 23:52:41', NULL, '贾一', '22014083001');
INSERT INTO `users` VALUES (16, '13800000002', '$2b$12$7iPzfP81cDM/najRnW3exeLSnlRO9pWmZSk8cYsJDU/4f1L8kWqH.', 'student', 1, '2026-01-04 16:34:15', NULL, NULL, '贾二', '22014083002');
INSERT INTO `users` VALUES (17, '13800000003', '$2b$12$cj/Apjf6zd33ysXSYJB0weIhjYhQ25xRVLPzI67ImihSnhAFJPEF2', 'student', 1, '2026-01-04 16:34:15', NULL, NULL, '贾三', '22014083003');
INSERT INTO `users` VALUES (18, '13800000004', '$2b$12$pqg9oMG/yOPa2j0mY.RJ4ub3THykA9jCF7czA6aUte4cYHfLL4Kom', 'student', 1, '2026-01-04 16:34:16', '2026-01-04 17:56:56', NULL, '贾四', '22014083004');
INSERT INTO `users` VALUES (19, '13800000005', '$2b$12$/aD6l4ZqWVBsWXwvcpvYKOyL8iV2vmmPC8gbBbVJdB.wdKz3XR0xq', 'student', 1, '2026-01-04 16:34:16', NULL, NULL, '贾五', '22014083005');
INSERT INTO `users` VALUES (20, '13800000006', '$2b$12$SOxWlzI5.vl3nLxyPjt.QeNzS1PjCGia9QY2HcMiK8dK2xPs/5m9K', 'student', 1, '2026-01-04 16:34:16', NULL, NULL, '贾六', '22014083006');
INSERT INTO `users` VALUES (21, '13800000007', '$2b$12$f7kv8nGn7AjtAh7R4fez7ubUVYu2K0zRGH72tufxLngFDaS0iifo2', 'student', 1, '2026-01-04 16:34:16', NULL, NULL, '贾七', '22014083007');
INSERT INTO `users` VALUES (22, '13800000008', '$2b$12$K0p3Tkxo0EzWtPEKPr05ROq0JOy.kEyu6vIGV1/JYmV2NQrKOurk.', 'student', 1, '2026-01-04 16:34:16', '2026-01-14 16:06:51', NULL, '贾八', '22014083008');
INSERT INTO `users` VALUES (23, '13800000009', '$2b$12$jRdwdVxJYCo0KwdAjjSwuOen61OLZ1HHrp85zLz8W0TPL7bIcXFpe', 'student', 1, '2026-01-04 16:34:17', NULL, NULL, '贾九', '22014083009');
INSERT INTO `users` VALUES (24, '13800000010', '$2b$12$kdxeNZFd0LDNmc1sBHmrbusIBjTLynGNt1K8juwZHAUWEKoc6.yyS', 'student', 1, '2026-01-04 17:27:29', NULL, NULL, '林一', '22014081001');
INSERT INTO `users` VALUES (25, '13800000011', '$2b$12$xmmkIGE75pggM1y/12yuWOmqRdtMbqCQV6miljvsjYnLHKADoo5yC', 'student', 1, '2026-01-04 17:27:29', NULL, NULL, '林二', '22014081002');
INSERT INTO `users` VALUES (26, '13800000012', '$2b$12$mMdDv04GlYkm3oLr5DmhveQ8SLQ8WcrMOLDaaZXv2S/qKjLhD8nSm', 'student', 1, '2026-01-04 17:27:29', NULL, NULL, '林三', '22014081003');
INSERT INTO `users` VALUES (27, '13800000013', '$2b$12$pQ1QlXKQXDEmlsM8UroPm.Vjcu9JARuKXK03JNzU3lAQPC2ANvhmO', 'student', 1, '2026-01-04 17:27:29', NULL, NULL, '林四', '22014081004');
INSERT INTO `users` VALUES (28, '13800000014', '$2b$12$Pjt5OyUJNCKptgKNcgD01OtmM6VEXpNKwqovY4rc7Z.R4h52PjCci', 'student', 1, '2026-01-04 17:27:29', NULL, NULL, '林五', '22014081005');
INSERT INTO `users` VALUES (29, '13800000015', '$2b$12$H3Lf13vrCHGsFvi8zv/U2eMgUu1B/atrI37HAfHJKv.HXZ9V7pzg.', 'student', 1, '2026-01-04 17:27:30', NULL, NULL, '林六', '22014081006');
INSERT INTO `users` VALUES (30, '13800000016', '$2b$12$aZSlMSN7kfe3Wn48JZeQIOyDiJl.Xf.ZWAq9j6sBV7imlBRcfkUZS', 'student', 1, '2026-01-04 17:27:30', NULL, NULL, '林七', '22014081007');
INSERT INTO `users` VALUES (31, '13800000017', '$2b$12$DxaQwZaHqCW9Aw5E.J0yxueDN.LLtoDnnsVKgrRZd8ZQ4GESu289i', 'student', 1, '2026-01-04 17:27:30', NULL, NULL, '林八', '22014081008');
INSERT INTO `users` VALUES (32, '13800000018', '$2b$12$FE/5oNww5N9VysAy1LDlJuzCK2e6oRkCNugw8zl3YjRI.hD.8vtE2', 'student', 1, '2026-01-04 17:27:30', '2026-01-07 17:51:59', NULL, '林九', '22014081009');
INSERT INTO `users` VALUES (33, '13800000019', '$2b$12$Agwl04gvXuv8BRw19YuRUO3EyWHmwr7dRv.5Duc62WlQKbWA7jo3G', 'student', 1, '2026-01-04 17:31:26', NULL, NULL, '林十', '22014081010');
INSERT INTO `users` VALUES (34, '13800000020', '$2b$12$RpF0w9w7S.zodMghFyfERuyl9jXqe4spjfInfqFdTHyUd87TEhuoS', 'student', 1, '2026-01-04 17:31:26', NULL, NULL, '林十一', '22014081011');
INSERT INTO `users` VALUES (35, '13800000021', '$2b$12$IqnnLclMHEiPNVTH69segesRMRTBrcncraySJ14Adbk.iX9ivRvlq', 'student', 1, '2026-01-04 17:31:26', NULL, NULL, '林十二', '22014081012');
INSERT INTO `users` VALUES (36, '13800000022', '$2b$12$nRj4SQ7vcaXks.el7Y.AQ.ySAIp54e2OUf2TeVrA6NqCnyjklaoHq', 'student', 1, '2026-01-04 17:31:26', NULL, NULL, '林十三', '22014081013');
INSERT INTO `users` VALUES (37, '13800000023', '$2b$12$AodUPHoU2eXai7NM/E6D6eiwmVRxhKueaJgJZtYP980/W4MAq0A0m', 'student', 1, '2026-01-04 17:31:27', NULL, NULL, '林十四', '22014081014');
INSERT INTO `users` VALUES (38, '13800000024', '$2b$12$uuy3iXuLuBjV0QKf.szuIO4miYajgLOcb0yfoLyotmF.xN8foYkWO', 'student', 1, '2026-01-04 17:31:27', NULL, NULL, '林十五', '22014081015');
INSERT INTO `users` VALUES (39, '13800000025', '$2b$12$V9cHKRRxy7b0cYE0LOXE3OmJ9wtf7O1.vrn7wlmSHvh4sH55/CmUi', 'student', 1, '2026-01-04 17:31:27', NULL, NULL, '林十六', '22014081016');
INSERT INTO `users` VALUES (40, '13800000026', '$2b$12$KrJ6nfzG3MrDpmmQyEP/Ee1DQwLmZu5A5AY1efFFMw1nU2SOKvggK', 'student', 1, '2026-01-04 17:31:27', NULL, NULL, '林十七', '22014081017');
INSERT INTO `users` VALUES (41, '13800000027', '$2b$12$syr2Oad/bL34pz3z1Dsv6OdG/7IJ9jn84vFF9ALN.kAI2QXG1JiaK', 'student', 1, '2026-01-04 17:31:27', NULL, NULL, '林十八', '22014081018');
INSERT INTO `users` VALUES (42, '13800000028', '$2b$12$grSqoR.wyJZCUAfosCWU4eh2J2u.MxcplQf/EIn8xdAzDC4o3LPEy', 'student', 1, '2026-01-04 17:31:28', NULL, NULL, '林十九', '22014081019');
INSERT INTO `users` VALUES (43, '13800000029', '$2b$12$x34iQapfJaZKSCk0RlAleuluzWmxMbTxN8Bq/hUATBIsL104MI9j2', 'student', 1, '2026-01-04 17:31:28', NULL, NULL, '林二十', '22014081020');
INSERT INTO `users` VALUES (44, '13800000030', '$2b$12$Z5XGW06NY6Jr6Hq8pma4hOaj3HJQsxol84YqSw94GhHZVF4PcDBSS', 'student', 1, '2026-01-04 17:31:28', NULL, NULL, '林二一', '22014081021');
INSERT INTO `users` VALUES (45, '13800000031', '$2b$12$2Y9Z9OAflHC0nU9XWe4b7.ZLl2ICFIyWL3MO1ryuPEqm4ykpBvK26', 'student', 1, '2026-01-04 17:31:28', NULL, NULL, '林二二', '22014081022');
INSERT INTO `users` VALUES (46, '13800000032', '$2b$12$8Qigss2aPjhSocZU2VUTDuMYxenr5ZI35W4iPVChqgtAfImSso.wO', 'student', 1, '2026-01-04 17:31:28', NULL, NULL, '林二三', '22014081023');
INSERT INTO `users` VALUES (47, '13800000033', '$2b$12$KfpQjv7GzYEpFVfVuD6dKO6PxlFsHSeYnYNF6wtIqCDfFHHdvp26u', 'student', 1, '2026-01-04 17:31:29', NULL, NULL, '林二四', '22014081024');
INSERT INTO `users` VALUES (48, '13800000034', '$2b$12$s8NZyY78KzBNLxvfCE0VlO2ztDCLH1DHBbJ2HGfp7PQxWkRdDhINe', 'student', 1, '2026-01-04 17:31:29', NULL, NULL, '林二五', '22014081025');
INSERT INTO `users` VALUES (49, '13800000035', '$2b$12$vjdvfA9DlhHn.S9HiASyIOHp59hFpwCepI1.h6cciJ3C5szrJntZm', 'student', 1, '2026-01-04 17:31:29', NULL, NULL, '林二六', '22014081026');
INSERT INTO `users` VALUES (50, '13800000036', '$2b$12$CeweWNm7Czy31hdXCC8nzO3tNC2P/t20wE1C/DA.KGtZo6p13yyaC', 'student', 1, '2026-01-04 17:31:29', NULL, NULL, '林二七', '22014081027');
INSERT INTO `users` VALUES (51, '13800000037', '$2b$12$u0y0lHRvoPOL3jQuvElg/.bbUchvuVipScCJTzCJSp3x2xROqWcKS', 'student', 1, '2026-01-04 17:31:29', NULL, NULL, '林二八', '22014081028');
INSERT INTO `users` VALUES (52, '13800000038', '$2b$12$JMyPT.nR8dDcVYf7USc3L.Ipe3MwqC1GpReWu90Y5YY9h/gVGVnRi', 'student', 1, '2026-01-04 17:31:30', NULL, NULL, '林二九', '22014081029');
INSERT INTO `users` VALUES (53, '13800000039', '$2b$12$tsiBrw.e6HxcI7Kqji/tyOLwGrLBwvp4cXpSJJigxJ4jFK8C8y3H2', 'student', 1, '2026-01-04 17:31:30', NULL, NULL, '林三十', '22014081030');
INSERT INTO `users` VALUES (54, '13800000040', '$2b$12$yYepo.TXgUm6DUElB0wgM.9Yi82wu98csJifWgpJHH9/FjMkW8GjC', 'student', 1, '2026-01-04 17:31:30', NULL, NULL, '林三一', '22014081031');
INSERT INTO `users` VALUES (55, '18250636888', '$2b$12$GHFiwnbK8ACafBt2pf84RuH7SrnjmT5ljJZTRAPMw7hm/737E7bui', 'teacher', 1, '2026-01-19 09:54:49', '2026-01-19 16:37:26', NULL, '张三三', NULL);
INSERT INTO `users` VALUES (56, '13656560001', '$2b$12$A7c4GCqd5c5eJ33qPiTB2.2pXp6dc5HF4USJwSzVWeAwV9EZLC6Vm', 'student', 1, '2026-01-19 10:26:28', NULL, NULL, '1', '20250119001');
INSERT INTO `users` VALUES (57, '13656560002', '$2b$12$5t9mIvskVRNgI.Bg3eK6ce.wdFu0NT8y.fgpapUjmEORySHCA.L8u', 'student', 1, '2026-01-19 10:26:29', NULL, NULL, '2', '20250119002');
INSERT INTO `users` VALUES (58, '13656560003', '$2b$12$vWsk3hc1FPJs03aK0WMHn.labIsumOjBogeFauye3rtmag8IyedRa', 'student', 1, '2026-01-19 10:26:29', NULL, NULL, '3', '20250119003');
INSERT INTO `users` VALUES (59, '13656560004', '$2b$12$rH85qyAxCWqQF6IB1JcBQOgfds6awNiZKkfoVJyq1iwoljQo8hmki', 'student', 1, '2026-01-19 10:26:29', NULL, NULL, '4', '20250119004');
INSERT INTO `users` VALUES (60, '13656560005', '$2b$12$DZLJV2YX6LXE3j1IMwpOS.StIVykG3V5oLKPjfLRIXVUm3GSeFSJm', 'student', 1, '2026-01-19 10:26:29', NULL, NULL, '5', '20250119005');
INSERT INTO `users` VALUES (61, '13656560006', '$2b$12$/YKYJJb4tX3c2fsrw/b.tuyHl2MHfnPPFhLntY4.F/64XP34os2QS', 'student', 1, '2026-01-19 10:26:30', NULL, NULL, '6', '20250119006');
INSERT INTO `users` VALUES (62, '13656560007', '$2b$12$iekA0LayHDdwGOjxpXvEOuTmMT6CfWclhxysBzsC2y//fFZthwEkK', 'student', 1, '2026-01-19 10:26:30', NULL, NULL, '7', '20250119007');
INSERT INTO `users` VALUES (63, '13656560008', '$2b$12$P0yR5FPOs1KG0ZO5hLBcTuUh3HQitkG43nqlzzt60DWtJH71t4GJ2', 'student', 1, '2026-01-19 10:26:30', NULL, NULL, '8', '20250119008');
INSERT INTO `users` VALUES (64, '13656560009', '$2b$12$L8.jFvH4Yo9p9P6/yg.b.OfgusqJWz8EhkLxoL5TQOxzoColFGEFa', 'student', 1, '2026-01-19 10:26:30', NULL, NULL, '9', '20250119009');
INSERT INTO `users` VALUES (65, '13656560010', '$2b$12$nFvwQp7uAboulj03l4l4W.QaRxCNhdyrxABxcp995eqZTQXfPdtEK', 'student', 1, '2026-01-19 10:26:31', NULL, NULL, '10', '20250119010');
INSERT INTO `users` VALUES (66, '13656560011', '$2b$12$fxmtpEfDNrbTuxtsQ6MuC.1rS/6YjNSGRY3uUL5qjxQcEz34eRmmq', 'student', 1, '2026-01-19 10:26:31', NULL, NULL, '11', '20250119011');
INSERT INTO `users` VALUES (67, '13656560012', '$2b$12$SLQnJEDkfvkDNoJ/S2B9We8hKRiLENbZzVJr3TSUiTyMsG1226dLS', 'student', 1, '2026-01-19 10:26:31', NULL, NULL, '12', '20250119012');
INSERT INTO `users` VALUES (68, '13656560013', '$2b$12$pN1JBLjXmS1xfSVDVLzA8.4b74WCQkGsYBDAKahM8ggMj3zNWGujK', 'student', 1, '2026-01-19 10:26:31', NULL, NULL, '13', '20250119013');
INSERT INTO `users` VALUES (69, '13656560014', '$2b$12$9HrLtvyiQScoua.BkDzlR.S8WNI02Zb5uic/GgFzu.WF5MRcf2PyG', 'student', 1, '2026-01-19 10:26:32', NULL, NULL, '14', '20250119014');
INSERT INTO `users` VALUES (70, '13656560015', '$2b$12$NZRy1cvQmX8W223lzGhjQ.3v2HouNGekXgZE9DrS3CcP7M52sbwUa', 'student', 1, '2026-01-19 10:26:32', NULL, NULL, '15', '20250119015');
INSERT INTO `users` VALUES (71, '13656560016', '$2b$12$zyRmgOPSyBZYjH0MGE95mO65brcQ0z.Uz3YtHYFgJqR6KUAkQulJe', 'student', 1, '2026-01-19 10:26:32', NULL, NULL, '16', '20250119016');
INSERT INTO `users` VALUES (72, '13656560017', '$2b$12$TZqYWCnVYHN8mIvJrjKOIOsZSNFHFIPtmFQlbVlQmMEoFt0547ZHm', 'student', 1, '2026-01-19 10:26:32', NULL, NULL, '17', '20250119017');
INSERT INTO `users` VALUES (73, '13656560018', '$2b$12$9qOz/zG0stb4MWTnQEMaJe3vfQTR1R7ZIE.rIY.P2WGPP92M1QIvu', 'student', 1, '2026-01-19 10:26:32', NULL, NULL, '18', '20250119018');
INSERT INTO `users` VALUES (74, '13656560019', '$2b$12$/YKpovwVxdZYHzQ3Hbv/2.l1EXpZ1qyLalf.n7aMFfxrMcr3W0ldi', 'student', 1, '2026-01-19 10:26:33', NULL, NULL, '19', '20250119019');
INSERT INTO `users` VALUES (75, '13656560020', '$2b$12$vbT5l9GbTS4S6y2syJh3gu9GJNwMewJbTRLdgHtz27HFgO6ScqisG', 'student', 1, '2026-01-19 10:26:33', NULL, NULL, '20', '20250119020');
INSERT INTO `users` VALUES (76, '13656560021', '$2b$12$kASpzKDnxZQlO23e7ojl6ur4HYCWSQEU85vugTYzLoxQXqilofLru', 'student', 1, '2026-01-19 10:26:33', NULL, NULL, '21', '20250119021');
INSERT INTO `users` VALUES (77, '13656560022', '$2b$12$LbmgDfchsG1Kc1yHZ..0ue6B0WzDzjIbz47IjJL2mmV0I5GtOBcXO', 'student', 1, '2026-01-19 10:26:33', NULL, NULL, '22', '20250119022');
INSERT INTO `users` VALUES (78, '13656560023', '$2b$12$vWaQNcSuCCuQUEay7NMH6uU0uTHVWkRBKEzv50kZwcnzSENqn.lZC', 'student', 1, '2026-01-19 10:26:33', NULL, NULL, '23', '20250119023');
INSERT INTO `users` VALUES (79, '13656560024', '$2b$12$39inH00QiXPLe6wukaZl/uUfGNmczddxXY6kHP7PbIPWTjpqLaL5G', 'student', 1, '2026-01-19 10:26:34', NULL, NULL, '24', '20250119024');
INSERT INTO `users` VALUES (80, '13656560025', '$2b$12$XrqGnjD0eP68z4N0vnJFY.lUtidwG//PqP0Q1mAxIqKGPNBoN7pvC', 'student', 1, '2026-01-19 10:26:34', NULL, NULL, '25', '20250119025');
INSERT INTO `users` VALUES (81, '13656560026', '$2b$12$QQS577alKEyIAz2pyfQh6uCFE8r.jVGykNBZttksphcbNwxBOFMEi', 'student', 1, '2026-01-19 10:26:34', NULL, NULL, '26', '20250119026');
INSERT INTO `users` VALUES (82, '13656560027', '$2b$12$Kno5nL7Hnvb6C58njlszk.h/aZfAltomI1kge8XrqLMKCV8L3eG6O', 'student', 1, '2026-01-19 10:26:34', NULL, NULL, '27', '20250119027');
INSERT INTO `users` VALUES (83, '13656560028', '$2b$12$kVPIS/TfHnriAMa.L7mAmeTxMvPjzfNTYbgvaceHHhOfkfr3432QG', 'student', 1, '2026-01-19 10:26:34', NULL, NULL, '28', '20250119028');
INSERT INTO `users` VALUES (84, '13656560029', '$2b$12$8Ob/MUQeyGgbcXEVVmcT.uUcMfm7LQmra2sEPEeWpcxFobORZ9aJq', 'student', 1, '2026-01-19 10:26:35', NULL, NULL, '29', '20250119029');
INSERT INTO `users` VALUES (85, '13656560030', '$2b$12$7UOyshOMEJjo0sPqvglppu1afSfPu/K4ruME50O1aIPSLMgNQvjlS', 'student', 1, '2026-01-19 10:26:35', NULL, NULL, '30', '20250119030');
INSERT INTO `users` VALUES (86, '13656560031', '$2b$12$g5.QZ7ngkUGWV9wl7v.u.O.RTRomswzWGlQbJ0HSS9jVt7NX0NYUq', 'student', 1, '2026-01-19 10:26:35', NULL, NULL, '31', '20250119031');
INSERT INTO `users` VALUES (87, '13656560032', '$2b$12$NMSP8ryv3LG5rZzEdwnFP.E.GPkgWeTAtvlVesl2Mm0LdffvlJFCC', 'student', 1, '2026-01-19 10:26:35', NULL, NULL, '32', '20250119032');
INSERT INTO `users` VALUES (88, '13656560033', '$2b$12$VEz5c2OphjrnGO1DosLHR.fbcVszK5PLoYq1jVRZpLIm92Hb4Uiie', 'student', 1, '2026-01-19 10:26:35', NULL, NULL, '33', '20250119033');
INSERT INTO `users` VALUES (89, '13656560034', '$2b$12$uGRQbsq7a5seEDdMu0cS8eEwLVm6NleB4E7uz3YZ7kxCZAQTNeIIe', 'student', 1, '2026-01-19 10:26:36', NULL, NULL, '34', '20250119034');
INSERT INTO `users` VALUES (90, '13656560035', '$2b$12$AW9B11tZUTcp/J1xTQBlVO3ZrQAEyiDJI/cRIdnAeh3w1LJJ64hRu', 'student', 1, '2026-01-19 10:26:36', NULL, NULL, '35', '20250119035');
INSERT INTO `users` VALUES (91, '13656560036', '$2b$12$UZtoiDjGGB1o0Omt6xCX2eCfouT1IBdGdcEAMoS8arbuOgMi5tx2.', 'student', 1, '2026-01-19 10:26:36', NULL, NULL, '36', '20250119036');
INSERT INTO `users` VALUES (92, '13656560037', '$2b$12$b7sz80IQx6Bhs.MZHKnUa.PRkOfYHSxqY7a1WV/Ix1W3.Odid8eaa', 'student', 1, '2026-01-19 10:26:36', NULL, NULL, '37', '20250119037');
INSERT INTO `users` VALUES (93, '13656560038', '$2b$12$3t4DPg333Y5smo3pehiY0O41Q6H0TIgMGAJCr2STc35NEF2q0x1/6', 'student', 1, '2026-01-19 10:26:36', NULL, NULL, '38', '20250119038');
INSERT INTO `users` VALUES (94, '13656560039', '$2b$12$7UWRjbjSBu3XA8fq56mmt./MVcAegqTfBDliqu0q7I6RGOBpcGFjC', 'student', 1, '2026-01-19 10:26:37', NULL, NULL, '39', '20250119039');
INSERT INTO `users` VALUES (95, '13656560040', '$2b$12$NqQ1T7nNpIqKf/cgnkBi9.GZtY0OzjE6mukUbL0qKEG4SqPB0IvIW', 'student', 1, '2026-01-19 10:26:37', NULL, NULL, '40', '20250119040');
INSERT INTO `users` VALUES (96, '13656560041', '$2b$12$DF4wNfqLOQWdSqMFRz7S8.6NAJv4wjeE7oBCjGrD0xzWjUUgz.HrC', 'student', 1, '2026-01-19 10:26:37', NULL, NULL, '41', '20250119041');
INSERT INTO `users` VALUES (97, '13656560042', '$2b$12$9o1DLGtgfNFXKqluiAs3oeMZGs2VvupJeFjL4A4e7r.N0vwlFHO6S', 'student', 1, '2026-01-19 10:26:37', NULL, NULL, '42', '20250119042');
INSERT INTO `users` VALUES (98, '13656560043', '$2b$12$4K.PU2WyC8aAdrVz/9thaeu9xk9FsfUS.E2JhZJJmg3khLoQtHhOy', 'student', 1, '2026-01-19 10:26:37', NULL, NULL, '43', '20250119043');
INSERT INTO `users` VALUES (99, '13656560044', '$2b$12$XCF0/q/RHKZqYGat1vLWT.UMBl0g.UDl4CKktoViJcMFkw1awwPse', 'student', 1, '2026-01-19 10:26:38', NULL, NULL, '44', '20250119044');
INSERT INTO `users` VALUES (100, '13656560045', '$2b$12$S1Tkh6koSwH/31/32NsnU.yg2jJxBlBCMzqcmV6CRLiX7ZcqeLGOm', 'student', 1, '2026-01-19 10:26:38', NULL, NULL, '45', '20250119045');
INSERT INTO `users` VALUES (101, '13656560046', '$2b$12$2hswKOibSNxnaO/5YF6Z6unKDX2dGdJvtjW7FuPFj.mLfoD1kMQpa', 'student', 1, '2026-01-19 10:26:38', NULL, NULL, '46', '20250119046');
INSERT INTO `users` VALUES (102, '13656560047', '$2b$12$nuPtKM5U2GMMQ/2Mg19Ks.6M29MvoseNfPcOtEyHELg5pnSxZC3XW', 'student', 1, '2026-01-19 10:26:38', NULL, NULL, '47', '20250119047');
INSERT INTO `users` VALUES (103, '13656560048', '$2b$12$pI3jtMf1AWt9jYu13xBbkO7KdTTuLJykicOmjHO9pDJBvVjwwdJse', 'student', 1, '2026-01-19 10:26:38', NULL, NULL, '48', '20250119048');
INSERT INTO `users` VALUES (104, '13656560049', '$2b$12$QfpdiWbXzD3CUn4QWtcipOrLoVSYXtDy3heiRiXlj/l9LdFIAj5JG', 'student', 1, '2026-01-19 10:26:39', NULL, NULL, '49', '20250119049');
INSERT INTO `users` VALUES (105, '13656560050', '$2b$12$3AZcczH2eUQDQQCqETCH1OEfyYOhh7IK1iEPS33oLWbM8SopXp5gi', 'student', 1, '2026-01-19 10:26:39', '2026-01-19 13:56:35', NULL, '50', '20250119050');

SET FOREIGN_KEY_CHECKS = 1;

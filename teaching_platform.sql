/*
 Navicat Premium Data Transfer

 Source Server         : localhost_3308
 Source Server Type    : MySQL
 Source Server Version : 80042 (8.0.42)
 Source Host           : localhost:3308
 Source Schema         : teaching_platform

 Target Server Type    : MySQL
 Target Server Version : 80042 (8.0.42)
 File Encoding         : 65001

 Date: 05/01/2026 17:50:49
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

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
) ENGINE = InnoDB AUTO_INCREMENT = 32 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of class_course_bindings
-- ----------------------------
INSERT INTO `class_course_bindings` VALUES (6, 3, 1, '2025-12-30 14:49:24');
INSERT INTO `class_course_bindings` VALUES (10, 2, 2, '2025-12-30 17:08:11');
INSERT INTO `class_course_bindings` VALUES (11, 2, 1, '2025-12-30 17:08:11');
INSERT INTO `class_course_bindings` VALUES (12, 2, 3, '2025-12-30 17:08:11');
INSERT INTO `class_course_bindings` VALUES (15, 4, 7, '2025-12-31 16:09:21');
INSERT INTO `class_course_bindings` VALUES (16, 5, 8, '2025-12-31 16:10:00');
INSERT INTO `class_course_bindings` VALUES (28, 1, 1, '2025-12-31 17:19:22');
INSERT INTO `class_course_bindings` VALUES (29, 1, 2, '2025-12-31 17:19:22');
INSERT INTO `class_course_bindings` VALUES (30, 1, 3, '2025-12-31 17:19:22');
INSERT INTO `class_course_bindings` VALUES (31, 1, 4, '2025-12-31 17:19:22');

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
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `teacher_id`(`teacher_id` ASC) USING BTREE,
  INDEX `ix_classes_id`(`id` ASC) USING BTREE,
  CONSTRAINT `classes_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of classes
-- ----------------------------
INSERT INTO `classes` VALUES (1, '25跨境电商1班', '', 2, '2025-12-26 16:01:20', 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?q=80&w=300&auto=format&fit=crop', '2025-12-10 16:00:00', '2025-12-22 16:00:00');
INSERT INTO `classes` VALUES (2, '25电子商务1班', '电商', 2, '2025-12-29 10:21:33', 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=300&auto=format&fit=crop', '2025-12-29 10:18:00', '2025-12-31 15:47:00');
INSERT INTO `classes` VALUES (3, '25商务英语1班', '商务英语1班', 2, '2025-12-29 16:28:53', 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=300&auto=format&fit=crop', '2025-12-29 08:28:00', '2025-12-30 16:00:00');
INSERT INTO `classes` VALUES (4, '25电子商务2班', '', 4, '2025-12-31 16:09:21', 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=300&auto=format&fit=crop', '2025-12-31 08:08:00', '2026-02-25 16:00:00');
INSERT INTO `classes` VALUES (5, '25跨境电商2班', '', 4, '2025-12-31 16:10:00', 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=300&auto=format&fit=crop', '2025-12-30 16:00:00', '2026-02-11 16:00:00');

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
) ENGINE = InnoDB AUTO_INCREMENT = 22 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '课程章节表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of course_chapters
-- ----------------------------
INSERT INTO `course_chapters` VALUES (18, 6, '第01章 平台入驻与基础建设', 1, '2026-01-05 17:44:07');
INSERT INTO `course_chapters` VALUES (19, 6, '第02章 商品运营与店铺装修', 2, '2026-01-05 17:44:08');
INSERT INTO `course_chapters` VALUES (20, 6, '第03章 营销推广与流量获取', 3, '2026-01-05 17:44:08');
INSERT INTO `course_chapters` VALUES (21, 6, '第04章 订单履约与售后服务', 4, '2026-01-05 17:44:08');

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
) ENGINE = InnoDB AUTO_INCREMENT = 161 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '课时资源表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of course_lessons
-- ----------------------------
INSERT INTO `course_lessons` VALUES (121, 18, '任务1 Shopee平台店铺入驻指导', 'pdf', '/static/uploads/materials/course_6/chapter_18/任务1 Shopee平台店铺入驻指导.pdf', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (122, 18, '任务1 Shopee平台店铺入驻指导', 'ppt', '/static/uploads/materials/course_6/chapter_18/任务1 Shopee平台店铺入驻指导.pptx', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (123, 18, '任务2 Shopee平台卖家端功能介绍', 'pdf', '/static/uploads/materials/course_6/chapter_18/任务2 Shopee平台卖家端功能介绍.pdf', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (124, 18, '任务2 Shopee平台卖家端功能介绍', 'ppt', '/static/uploads/materials/course_6/chapter_18/任务2 Shopee平台卖家端功能介绍.pptx', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (125, 18, '任务3 Shopee平台店铺基础设置', 'pdf', '/static/uploads/materials/course_6/chapter_18/任务3 Shopee平台店铺基础设置.pdf', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (126, 18, '任务3 Shopee平台店铺基础设置', 'ppt', '/static/uploads/materials/course_6/chapter_18/任务3 Shopee平台店铺基础设置.pptx', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (127, 18, '任务4 Shopee平台物流设置指导', 'pdf', '/static/uploads/materials/course_6/chapter_18/任务4 Shopee平台物流设置指导.pdf', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (128, 18, '任务4 Shopee平台物流设置指导', 'ppt', '/static/uploads/materials/course_6/chapter_18/任务4 Shopee平台物流设置指导.pptx', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (129, 19, '任务5 如何在Shopee平台进行商品上架', 'pdf', '/static/uploads/materials/course_6/chapter_19/任务5 如何在Shopee平台进行商品上架.pdf', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (130, 19, '任务5 如何在Shopee平台进行商品上架', 'ppt', '/static/uploads/materials/course_6/chapter_19/任务5 如何在Shopee平台进行商品上架.pptx', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (131, 19, '任务6 Shopee平台商品优化技巧（标题、类目、属性）', 'pdf', '/static/uploads/materials/course_6/chapter_19/任务6 Shopee平台商品优化技巧（标题、类目、属性）.pdf', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (132, 19, '任务6 Shopee平台商品优化技巧（标题、类目、属性）', 'ppt', '/static/uploads/materials/course_6/chapter_19/任务6 Shopee平台商品优化技巧（标题、类目、属性）.pptx', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (133, 19, '任务7 Shopee平台商品优化技巧（描述、图片、视频）', 'pdf', '/static/uploads/materials/course_6/chapter_19/任务7 Shopee平台商品优化技巧（描述、图片、视频）.pdf', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (134, 19, '任务7 Shopee平台商品优化技巧（描述、图片、视频）', 'ppt', '/static/uploads/materials/course_6/chapter_19/任务7 Shopee平台商品优化技巧（描述、图片、视频）.pptx', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (135, 19, '任务8 Shopee平台商店介绍设置流程', 'pdf', '/static/uploads/materials/course_6/chapter_19/任务8 Shopee平台商店介绍设置流程.pdf', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (136, 19, '任务8 Shopee平台商店介绍设置流程', 'ppt', '/static/uploads/materials/course_6/chapter_19/任务8 Shopee平台商店介绍设置流程.pptx', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (137, 19, '任务9 Shopee平台店铺装修指南', 'pdf', '/static/uploads/materials/course_6/chapter_19/任务9 Shopee平台店铺装修指南.pdf', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (138, 19, '任务9 Shopee平台店铺装修指南', 'ppt', '/static/uploads/materials/course_6/chapter_19/任务9 Shopee平台店铺装修指南.pptx', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (139, 19, '任务10 Shopee平台店铺装修：装饰组件的运用', 'pdf', '/static/uploads/materials/course_6/chapter_19/任务10 Shopee平台店铺装修：装饰组件的运用.pdf', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (140, 19, '任务10 Shopee平台店铺装修：装饰组件的运用', 'ppt', '/static/uploads/materials/course_6/chapter_19/任务10 Shopee平台店铺装修：装饰组件的运用.pptx', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (141, 20, '任务11 Shopee平台如何设置优惠券', 'pdf', '/static/uploads/materials/course_6/chapter_20/任务11 Shopee平台如何设置优惠券.pdf', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (142, 20, '任务11 Shopee平台如何设置优惠券', 'ppt', '/static/uploads/materials/course_6/chapter_20/任务11 Shopee平台如何设置优惠券.pptx', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (143, 20, '任务12 Shopee平台折扣活动设置流程', 'pdf', '/static/uploads/materials/course_6/chapter_20/任务12 Shopee平台折扣活动设置流程.pdf', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (144, 20, '任务12 Shopee平台折扣活动设置流程', 'ppt', '/static/uploads/materials/course_6/chapter_20/任务12 Shopee平台折扣活动设置流程.pptx', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (145, 20, '任务13 Shopee平台套装优惠设置流程 (Bundle Deal)', 'pdf', '/static/uploads/materials/course_6/chapter_20/任务13 Shopee平台套装优惠设置流程 (Bundle Deal).pdf', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (146, 20, '任务13 Shopee平台套装优惠设置流程 (Bundle Deal)', 'ppt', '/static/uploads/materials/course_6/chapter_20/任务13 Shopee平台套装优惠设置流程 (Bundle Deal).pptx', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (147, 20, '任务14 Shopee平台设置限时选购使用方法 (Flash Deal)', 'pdf', '/static/uploads/materials/course_6/chapter_20/任务14 Shopee平台设置限时选购使用方法 (Flash Deal).pdf', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (148, 20, '任务14 Shopee平台设置限时选购使用方法 (Flash Deal)', 'ppt', '/static/uploads/materials/course_6/chapter_20/任务14 Shopee平台设置限时选购使用方法 (Flash Deal).pptx', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (149, 20, '任务15 Shopee平台广告 (Ads) 投放流程', 'pdf', '/static/uploads/materials/course_6/chapter_20/任务15 Shopee平台广告 (Ads) 投放流程.pdf', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (150, 20, '任务15 Shopee平台广告 (Ads) 投放流程', 'ppt', '/static/uploads/materials/course_6/chapter_20/任务15 Shopee平台广告 (Ads) 投放流程.pptx', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (151, 20, '任务16 Shopee平台站外渠道广告功能介绍', 'pdf', '/static/uploads/materials/course_6/chapter_20/任务16 Shopee平台站外渠道广告功能介绍.pdf', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (152, 20, '任务16 Shopee平台站外渠道广告功能介绍', 'ppt', '/static/uploads/materials/course_6/chapter_20/任务16 Shopee平台站外渠道广告功能介绍.pptx', '15页', 0, 0, '2026-01-05 17:44:08');
INSERT INTO `course_lessons` VALUES (153, 21, '任务17 Shopee平台订单发货流程', 'pdf', '/static/uploads/materials/course_6/chapter_21/任务17 Shopee平台订单发货流程.pdf', '15页', 0, 0, '2026-01-05 17:44:09');
INSERT INTO `course_lessons` VALUES (154, 21, '任务17 Shopee平台订单发货流程', 'ppt', '/static/uploads/materials/course_6/chapter_21/任务17 Shopee平台订单发货流程.pptx', '15页', 0, 0, '2026-01-05 17:44:09');
INSERT INTO `course_lessons` VALUES (155, 21, '任务18 Shopee平台退货退款处理流程', 'pdf', '/static/uploads/materials/course_6/chapter_21/任务18 Shopee平台退货退款处理流程.pdf', '15页', 0, 0, '2026-01-05 17:44:09');
INSERT INTO `course_lessons` VALUES (156, 21, '任务18 Shopee平台退货退款处理流程', 'ppt', '/static/uploads/materials/course_6/chapter_21/任务18 Shopee平台退货退款处理流程.pptx', '15页', 0, 0, '2026-01-05 17:44:09');
INSERT INTO `course_lessons` VALUES (157, 21, '任务19 关于Shopee平台售前、售中、售后咨询服务', 'pdf', '/static/uploads/materials/course_6/chapter_21/任务19 关于Shopee平台售前、售中、售后咨询服务.pdf', '15页', 0, 0, '2026-01-05 17:44:09');
INSERT INTO `course_lessons` VALUES (158, 21, '任务19 关于Shopee平台售前、售中、售后咨询服务', 'ppt', '/static/uploads/materials/course_6/chapter_21/任务19 关于Shopee平台售前、售中、售后咨询服务.pptx', '15页', 0, 0, '2026-01-05 17:44:09');
INSERT INTO `course_lessons` VALUES (159, 21, '任务20 Shopee平台如何使用运费测算工具', 'pdf', '/static/uploads/materials/course_6/chapter_21/任务20 Shopee平台如何使用运费测算工具.pdf', '15页', 0, 0, '2026-01-05 17:44:09');
INSERT INTO `course_lessons` VALUES (160, 21, '任务20 Shopee平台如何使用运费测算工具', 'ppt', '/static/uploads/materials/course_6/chapter_21/任务20 Shopee平台如何使用运费测算工具.pptx', '15页', 0, 0, '2026-01-05 17:44:09');

-- ----------------------------
-- Table structure for courses
-- ----------------------------
DROP TABLE IF EXISTS `courses`;
CREATE TABLE `courses`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '课程名称',
  `cover` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '课程封面URL',
  `intro` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '课程简介',
  `owner_id` int NOT NULL COMMENT '创建者/老师ID',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `task_count` int NULL DEFAULT 0 COMMENT '本课程任务数量',
  `total_duration` int NULL DEFAULT 0 COMMENT '总时长(分钟)',
  `lesson_count` int NULL DEFAULT 0 COMMENT '本课程课时数',
  `course_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '实训课程' COMMENT '课程类型',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_courses_owner`(`owner_id` ASC) USING BTREE,
  CONSTRAINT `fk_courses_owner` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 9 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of courses
-- ----------------------------
INSERT INTO `courses` VALUES (1, '【01】AI+(跨境)电商视觉营销设计', '/static/uploads/courses/f48d9e7d-4d3b-4b67-846b-663341a632ab.webp', '本课程专为跨境电商行业量身打造，从零开始系统学习如何使用ComfyUI打造电商商品图、场景图、模特图等视觉内容生产流程。面对传统拍摄成本高昂、制作周期长达3-7天影响新品上线的行业痛点，本课程通过节点式可视化工作流，让运营人员、设计师、讲师无需美术基础即可实现专业级图像生成。', 2, '2025-12-29 16:27:59', 30, 800, 20, '实训课程');
INSERT INTO `courses` VALUES (2, '【02】AI+智能体跨境客服应用', '/static/uploads/courses/121a8ee1-6756-4f38-9617-305fd69f97bc.png', '可视化节点编排AI电商自动化工作流', 2, '2025-12-29 16:31:28', 0, 0, 0, '实训课程');
INSERT INTO `courses` VALUES (3, '【03】AI提示词工程与跨境电商运营实务', '/static/uploads/courses/824528c9-caff-49cb-85df-4e5e46277d17.png', 'AI提示词工程与跨境电商运营实务', 2, '2025-12-29 16:32:12', 0, 0, 0, '实训课程');
INSERT INTO `courses` VALUES (4, '【04】跨境AI+短视频运营实战', '/static/uploads/courses/829cd3c3-d1b1-4b0d-8a7e-63c543a9f588.png', '', 2, '2025-12-30 17:11:50', 0, 0, 0, '实训课程');
INSERT INTO `courses` VALUES (5, '【05】AI+跨境电商数据分析实务', '/static/uploads/courses/0486fddf-3fbc-4907-a7ed-ce9ec8c925c6.png', '', 2, '2025-12-30 17:12:10', 0, 0, 0, '实训课程');
INSERT INTO `courses` VALUES (6, '【06】Shopee虚拟仿真与实战应用（东盟市场）', '/static/uploads/courses/379724bb-5ef3-47a5-b1b4-84dc219f8f7d.png', 'Shopee电商平台实训课程以典型工作任务驱 ，该课程涵盖卖家开店与经营的完整业务流程。在本课程中，学生将学习如何卖家完成账号注册、业务信息设置、运费模板设置、商品管理、营销活动、广告活动、订单管理等平台任务操作，使学生具备Shopee店铺的开设与营销、客服服务等能力。', 2, '2025-12-30 17:12:33', 20, 510, 50, '实训课程');
INSERT INTO `courses` VALUES (7, '【07】Ozon虚拟仿真与实战应用（中亚市场）', '/static/uploads/courses/3f48e3fb-130e-4acf-b059-0406583edf67.png', '', 2, '2025-12-30 17:12:49', 0, 0, 0, '实训课程');
INSERT INTO `courses` VALUES (8, '【08】东盟语种跨境直播实战', '/static/uploads/courses/e7c2c671-aa9b-4e1f-80d4-b0ff47e8c927.png', '', 2, '2025-12-30 17:13:34', 0, 0, 0, '实训课程');

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
) ENGINE = InnoDB AUTO_INCREMENT = 62 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

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
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '学生详细档案表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of student_profiles
-- ----------------------------
INSERT INTO `student_profiles` VALUES (1, 1, '张十一', '22014082032', '男', '18250636865', '/static/uploads/avatars/fa8f70d0-6ce0-4b90-853b-0bdb2919bcbe.png', NULL, '2026-01-04 14:23:33', '2026-01-04 15:39:00');
INSERT INTO `student_profiles` VALUES (2, 8, '张二', '22014082033', '保密', '18250636871', '/static/uploads/avatars/36c89a39-76e6-4973-8536-4ec4837ba50c.png', NULL, '2026-01-04 15:39:40', '2026-01-04 15:39:56');
INSERT INTO `student_profiles` VALUES (3, 15, '贾一', '22014083001', '保密', '13800000001', '/static/uploads/avatars/05958dc6-7eea-4f43-bd42-85beb748c40a.png', NULL, '2026-01-04 16:58:48', '2026-01-04 17:18:55');
INSERT INTO `student_profiles` VALUES (4, 18, '贾四', '22014083004', '保密', NULL, NULL, NULL, '2026-01-04 17:56:55', '2026-01-04 17:56:55');

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
) ENGINE = InnoDB AUTO_INCREMENT = 9 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '教师课程权限表' ROW_FORMAT = Dynamic;

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
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of teacher_profiles
-- ----------------------------
INSERT INTO `teacher_profiles` VALUES (1, 2, '张三', '男', '18250636866', '南宁职业技术大学', '电子商务学院', '高级讲师', 'happy', '/static/uploads/avatars/1ee64345-a553-40ee-9ab1-c4e94ed90a75.png', '2025-12-29 11:21:18', '2025-12-31 15:21:35');
INSERT INTO `teacher_profiles` VALUES (2, 4, '陈一', '女', '18250636867', '颜值大学', '电子商务学院', '副教授', '专业的', '/static/uploads/avatars/e2a0be43-da33-4473-8961-8de59f9e6c21.png', '2025-12-31 16:13:06', '2025-12-31 16:14:09');

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
) ENGINE = InnoDB AUTO_INCREMENT = 55 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, '18250636865', '$2b$12$jwxhQX9peRLmh0wxVq7xreuheYZDiDAIAIIzokZOnMsMr/R/RbVMS', 'student', 1, '2025-12-24 11:26:48', '2026-01-05 08:53:43', 8189, '张十一', '22014082032');
INSERT INTO `users` VALUES (2, '18250636866', '$2b$12$OFGjgw52J9TWeZzKeG6gPOHUKKhi7EM3YYfUh2R1n7e43azYclPWy', 'teacher', 1, '2025-12-24 11:27:14', '2026-01-05 17:43:28', NULL, NULL, NULL);
INSERT INTO `users` VALUES (4, '18250636867', '$2b$12$mVae3WIBNklVoxfL7qkLQ.ymZ9vRDq6vbwB2Za0cTStB1FO1DeYoa', 'teacher', 1, '2025-12-24 15:04:05', '2026-01-04 17:57:41', NULL, NULL, NULL);
INSERT INTO `users` VALUES (5, '18250636868', '$2b$12$LExgic9UmvpwwLtG5Gufs.08MAc8wx7EfZdv9CjYzn3QiLJnOUZdq', 'student', 1, '2025-12-24 17:26:36', '2025-12-25 17:38:52', 8190, '李四', '22014082034');
INSERT INTO `users` VALUES (6, '18250636969', '$2b$12$2bR.Xy.PQzAQDApnmWxdSeC.bIEs0C1kklBR751IoX4/tNFuUCyt2', 'student', 1, '2025-12-25 16:30:01', '2025-12-25 16:47:31', 8191, '王五', '22014082035');
INSERT INTO `users` VALUES (7, '18250636870', '$2b$12$JZUcksLjg6lZfnipDk.rS.Bqwgy4cH.dqmkuUgsvhQCSyw.c0wq9u', 'student', 1, '2025-12-25 16:34:04', '2025-12-25 16:51:53', 8192, '赵六', '22014082036');
INSERT INTO `users` VALUES (8, '18250636871', '$2b$12$HEqQ8pj0rTTBVi97d5wi2.juSlBWJnQ0AZaov6tlgvoxsf79j5j8m', 'student', 1, '2025-12-26 16:02:05', '2026-01-04 16:01:07', 8193, '张二', '22014082033');
INSERT INTO `users` VALUES (9, '18250636872', '$2b$12$ahylOLX4IYYfxTXg5xF72.D0V32UfPDd2WDs9B.gLUON2w0cDqw6q', 'student', 1, '2025-12-29 17:59:50', NULL, NULL, '张七', '22014082037');
INSERT INTO `users` VALUES (10, '18250636873', '$2b$12$oT0OqX4bUys/2obDlQtKCOxCvpB09s.AyOS83YbvQDq6GCXey5iWK', 'student', 1, '2025-12-30 14:20:52', NULL, NULL, '张四', '22014082021');
INSERT INTO `users` VALUES (11, '18250636874', '$2b$12$KXKRsdVENh0EmciRYox5K.OtcLcNoeR/26duy4z24TPhpj75uPe5.', 'student', 1, '2025-12-30 16:38:48', '2025-12-31 17:11:28', NULL, '张五', '22014082022');
INSERT INTO `users` VALUES (12, '18250636875', '$2b$12$pq9nEyWa41m4WKR/v.PON.artWlJPlEFgOB0sw5w.SrK0NsIfBEYG', 'student', 1, '2025-12-31 16:11:05', '2025-12-31 17:12:02', NULL, '张八', '22014082023');
INSERT INTO `users` VALUES (13, '18250636876', '$2b$12$NRSQIoCDK7ZW.1HqSy3C8uecojj7O2aFa1YX0ZMWMQ95sbbZ9u28K', 'student', 1, '2025-12-31 16:14:41', NULL, NULL, '张九', '22014082024');
INSERT INTO `users` VALUES (14, '18250636877', '$2b$12$4tZqq/x/k4LNU3hXUckHHeCkbCCIU7sN1Tab07dRj127smk8Q0a96', 'student', 1, '2025-12-31 16:15:10', NULL, NULL, '张十', '22014082025');
INSERT INTO `users` VALUES (15, '13800000001', '$2b$12$iCtsBwN3Pr72doOlHKNShuyQSHuCvsBn6mgY3Pl4dfTgu0vuHDVo2', 'student', 1, '2026-01-04 16:34:15', '2026-01-04 16:58:48', NULL, '贾一', '22014083001');
INSERT INTO `users` VALUES (16, '13800000002', '$2b$12$7iPzfP81cDM/najRnW3exeLSnlRO9pWmZSk8cYsJDU/4f1L8kWqH.', 'student', 1, '2026-01-04 16:34:15', NULL, NULL, '贾二', '22014083002');
INSERT INTO `users` VALUES (17, '13800000003', '$2b$12$cj/Apjf6zd33ysXSYJB0weIhjYhQ25xRVLPzI67ImihSnhAFJPEF2', 'student', 1, '2026-01-04 16:34:15', NULL, NULL, '贾三', '22014083003');
INSERT INTO `users` VALUES (18, '13800000004', '$2b$12$pqg9oMG/yOPa2j0mY.RJ4ub3THykA9jCF7czA6aUte4cYHfLL4Kom', 'student', 1, '2026-01-04 16:34:16', '2026-01-04 17:56:56', NULL, '贾四', '22014083004');
INSERT INTO `users` VALUES (19, '13800000005', '$2b$12$/aD6l4ZqWVBsWXwvcpvYKOyL8iV2vmmPC8gbBbVJdB.wdKz3XR0xq', 'student', 1, '2026-01-04 16:34:16', NULL, NULL, '贾五', '22014083005');
INSERT INTO `users` VALUES (20, '13800000006', '$2b$12$SOxWlzI5.vl3nLxyPjt.QeNzS1PjCGia9QY2HcMiK8dK2xPs/5m9K', 'student', 1, '2026-01-04 16:34:16', NULL, NULL, '贾六', '22014083006');
INSERT INTO `users` VALUES (21, '13800000007', '$2b$12$f7kv8nGn7AjtAh7R4fez7ubUVYu2K0zRGH72tufxLngFDaS0iifo2', 'student', 1, '2026-01-04 16:34:16', NULL, NULL, '贾七', '22014083007');
INSERT INTO `users` VALUES (22, '13800000008', '$2b$12$K0p3Tkxo0EzWtPEKPr05ROq0JOy.kEyu6vIGV1/JYmV2NQrKOurk.', 'student', 1, '2026-01-04 16:34:16', NULL, NULL, '贾八', '22014083008');
INSERT INTO `users` VALUES (23, '13800000009', '$2b$12$jRdwdVxJYCo0KwdAjjSwuOen61OLZ1HHrp85zLz8W0TPL7bIcXFpe', 'student', 1, '2026-01-04 16:34:17', NULL, NULL, '贾九', '22014083009');
INSERT INTO `users` VALUES (24, '13800000010', '$2b$12$kdxeNZFd0LDNmc1sBHmrbusIBjTLynGNt1K8juwZHAUWEKoc6.yyS', 'student', 1, '2026-01-04 17:27:29', NULL, NULL, '林一', '22014081001');
INSERT INTO `users` VALUES (25, '13800000011', '$2b$12$xmmkIGE75pggM1y/12yuWOmqRdtMbqCQV6miljvsjYnLHKADoo5yC', 'student', 1, '2026-01-04 17:27:29', NULL, NULL, '林二', '22014081002');
INSERT INTO `users` VALUES (26, '13800000012', '$2b$12$mMdDv04GlYkm3oLr5DmhveQ8SLQ8WcrMOLDaaZXv2S/qKjLhD8nSm', 'student', 1, '2026-01-04 17:27:29', NULL, NULL, '林三', '22014081003');
INSERT INTO `users` VALUES (27, '13800000013', '$2b$12$pQ1QlXKQXDEmlsM8UroPm.Vjcu9JARuKXK03JNzU3lAQPC2ANvhmO', 'student', 1, '2026-01-04 17:27:29', NULL, NULL, '林四', '22014081004');
INSERT INTO `users` VALUES (28, '13800000014', '$2b$12$Pjt5OyUJNCKptgKNcgD01OtmM6VEXpNKwqovY4rc7Z.R4h52PjCci', 'student', 1, '2026-01-04 17:27:29', NULL, NULL, '林五', '22014081005');
INSERT INTO `users` VALUES (29, '13800000015', '$2b$12$H3Lf13vrCHGsFvi8zv/U2eMgUu1B/atrI37HAfHJKv.HXZ9V7pzg.', 'student', 1, '2026-01-04 17:27:30', NULL, NULL, '林六', '22014081006');
INSERT INTO `users` VALUES (30, '13800000016', '$2b$12$aZSlMSN7kfe3Wn48JZeQIOyDiJl.Xf.ZWAq9j6sBV7imlBRcfkUZS', 'student', 1, '2026-01-04 17:27:30', NULL, NULL, '林七', '22014081007');
INSERT INTO `users` VALUES (31, '13800000017', '$2b$12$DxaQwZaHqCW9Aw5E.J0yxueDN.LLtoDnnsVKgrRZd8ZQ4GESu289i', 'student', 1, '2026-01-04 17:27:30', NULL, NULL, '林八', '22014081008');
INSERT INTO `users` VALUES (32, '13800000018', '$2b$12$FE/5oNww5N9VysAy1LDlJuzCK2e6oRkCNugw8zl3YjRI.hD.8vtE2', 'student', 1, '2026-01-04 17:27:30', NULL, NULL, '林九', '22014081009');
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
INSERT INTO `users` VALUES (51, '13800000037', '$2b$12$JFfX9d5uhbb2DUi/L45/X.ur5sYgyY2XTMlfPqnuWcZskEszpEu3i', 'student', 1, '2026-01-04 17:31:29', NULL, NULL, '林二八', '22014081028');
INSERT INTO `users` VALUES (52, '13800000038', '$2b$12$JMyPT.nR8dDcVYf7USc3L.Ipe3MwqC1GpReWu90Y5YY9h/gVGVnRi', 'student', 1, '2026-01-04 17:31:30', NULL, NULL, '林二九', '22014081029');
INSERT INTO `users` VALUES (53, '13800000039', '$2b$12$tsiBrw.e6HxcI7Kqji/tyOLwGrLBwvp4cXpSJJigxJ4jFK8C8y3H2', 'student', 1, '2026-01-04 17:31:30', NULL, NULL, '林三十', '22014081030');
INSERT INTO `users` VALUES (54, '13800000040', '$2b$12$yYepo.TXgUm6DUElB0wgM.9Yi82wu98csJifWgpJHH9/FjMkW8GjC', 'student', 1, '2026-01-04 17:31:30', NULL, NULL, '林三一', '22014081031');

SET FOREIGN_KEY_CHECKS = 1;

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

 Date: 29/12/2025 20:52:48
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
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of class_course_bindings
-- ----------------------------
INSERT INTO `class_course_bindings` VALUES (1, 3, 1, '2025-12-29 16:28:53');

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
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of classes
-- ----------------------------
INSERT INTO `classes` VALUES (1, '2025实训1班', 'comfyui', 2, '2025-12-26 16:01:20', NULL, NULL, NULL);
INSERT INTO `classes` VALUES (2, '2025comfyui2班', '跨境电商', 2, '2025-12-29 10:21:33', 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=300&auto=format&fit=crop', '2025-12-29 10:18:00', '2025-12-31 15:47:00');
INSERT INTO `classes` VALUES (3, '2025 实训3班', '商务英语1班', 2, '2025-12-29 16:28:53', 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=300&auto=format&fit=crop', '2025-12-29 08:28:00', '2025-12-30 16:00:00');

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
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_courses_owner`(`owner_id` ASC) USING BTREE,
  CONSTRAINT `fk_courses_owner` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of courses
-- ----------------------------
INSERT INTO `courses` VALUES (1, 'comfyui电商课程', 'http://127.0.0.1:8000/static/uploads/courses/f48d9e7d-4d3b-4b67-846b-663341a632ab.webp', 'AI生图技术在电商场景中的应用', 2, '2025-12-29 16:27:59');
INSERT INTO `courses` VALUES (2, 'dify 课程', 'http://127.0.0.1:8000/static/uploads/courses/121a8ee1-6756-4f38-9617-305fd69f97bc.png', '可视化节点编排AI电商自动化工作流', 2, '2025-12-29 16:31:28');
INSERT INTO `courses` VALUES (3, 'shopee 实战课程', 'http://127.0.0.1:8000/static/uploads/courses/4a816389-698b-469d-a958-2b3762d2d075.png', 'shopee虚拟仿真平台实战', 2, '2025-12-29 16:32:12');

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
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of enrollments
-- ----------------------------
INSERT INTO `enrollments` VALUES (1, 1, 8, '2025-12-26 16:02:05');
INSERT INTO `enrollments` VALUES (2, 1, 1, '2025-12-26 16:28:51');
INSERT INTO `enrollments` VALUES (3, 2, 5, '2025-12-29 16:35:07');
INSERT INTO `enrollments` VALUES (4, 2, 6, '2025-12-29 16:35:29');
INSERT INTO `enrollments` VALUES (5, 2, 7, '2025-12-29 16:35:46');
INSERT INTO `enrollments` VALUES (6, 3, 9, '2025-12-29 17:59:50');

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
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of teacher_profiles
-- ----------------------------
INSERT INTO `teacher_profiles` VALUES (1, 2, '张三', '男', '18250636866', '南宁职业技术大学', '电子商务学院', '高级讲师', 'happy', 'http://127.0.0.1:8000/static/uploads/avatars/1ee64345-a553-40ee-9ab1-c4e94ed90a75.png', '2025-12-29 11:21:18', '2025-12-29 14:11:46');

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
  INDEX `ix_users_id`(`id` ASC) USING BTREE,
  UNIQUE INDEX `comfyui_port`(`comfyui_port` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, '18250636865', '$2b$12$jwxhQX9peRLmh0wxVq7xreuheYZDiDAIAIIzokZOnMsMr/R/RbVMS', 'student', 1, '2025-12-24 11:26:48', '2025-12-29 17:55:51', 8189, '张凯', '22014082032');
INSERT INTO `users` VALUES (2, '18250636866', '$2b$12$OFGjgw52J9TWeZzKeG6gPOHUKKhi7EM3YYfUh2R1n7e43azYclPWy', 'teacher', 1, '2025-12-24 11:27:14', '2025-12-29 17:56:04', NULL, NULL, NULL);
INSERT INTO `users` VALUES (4, '18250636867', '$2b$12$mVae3WIBNklVoxfL7qkLQ.ymZ9vRDq6vbwB2Za0cTStB1FO1DeYoa', 'teacher', 1, '2025-12-24 15:04:05', '2025-12-25 17:21:29', NULL, NULL, NULL);
INSERT INTO `users` VALUES (5, '18250636868', '$2b$12$LExgic9UmvpwwLtG5Gufs.08MAc8wx7EfZdv9CjYzn3QiLJnOUZdq', 'student', 1, '2025-12-24 17:26:36', '2025-12-25 17:38:52', 8190, '李四', '22014082034');
INSERT INTO `users` VALUES (6, '18250636969', '$2b$12$2bR.Xy.PQzAQDApnmWxdSeC.bIEs0C1kklBR751IoX4/tNFuUCyt2', 'student', 1, '2025-12-25 16:30:01', '2025-12-25 16:47:31', 8191, '王五', '22014082035');
INSERT INTO `users` VALUES (7, '18250636870', '$2b$12$JZUcksLjg6lZfnipDk.rS.Bqwgy4cH.dqmkuUgsvhQCSyw.c0wq9u', 'student', 1, '2025-12-25 16:34:04', '2025-12-25 16:51:53', 8192, '赵六', '22014082036');
INSERT INTO `users` VALUES (8, '18250636871', '$2b$12$HEqQ8pj0rTTBVi97d5wi2.juSlBWJnQ0AZaov6tlgvoxsf79j5j8m', 'student', 1, '2025-12-26 16:02:05', '2025-12-26 17:00:26', 8193, '张龙', '22014082033');
INSERT INTO `users` VALUES (9, '18250636872', '$2b$12$ahylOLX4IYYfxTXg5xF72.D0V32UfPDd2WDs9B.gLUON2w0cDqw6q', 'student', 1, '2025-12-29 17:59:50', NULL, NULL, '张七', '22014082037');

SET FOREIGN_KEY_CHECKS = 1;

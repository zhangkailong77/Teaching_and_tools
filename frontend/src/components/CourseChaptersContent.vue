<template>
  <div class="course-chapters-content" :class="{ 'drawer-mode': isDrawerMode }">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>

    <!-- 章节列表 -->
    <div v-else class="chapters-list">
      <div
        v-for="(chapter, index) in chapterList"
        :key="chapter.id"
        class="chapter-item"
        :class="{ 'is-open': chapter.isOpen }"
      >
        <!-- 章节头部 -->
        <div class="chapter-header" @click="toggleChapter(index)">
          <div class="left">
            <svg class="arrow-icon" :class="{ rotated: chapter.isOpen }" width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="title">{{ chapter.title }}</span>
          </div>
          <div class="right">
            <span class="count">{{ chapter.lessons.length }} 节课</span>
          </div>
        </div>

        <!-- 课时列表 -->
        <div class="lesson-group" v-show="chapter.isOpen">
          <div
            v-for="lesson in chapter.lessons"
            :key="lesson.id"
            class="lesson-item"
            @click="handleLessonClick(lesson)"
          >
            <div class="lesson-left">
              <!-- 类型图标 -->
              <span class="type-icon" v-html="getTypeIcon(lesson.type)"></span>
              <span class="lesson-title">{{ lesson.title }}</span>
            </div>
            <div class="lesson-right">
              <!-- 状态按钮 -->
              <button
                v-if="lesson.status === 2"
                class="status-btn finished"
                @click.stop="handleLessonClick(lesson)"
              >
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path d="M10 3L4.5 8.5L2 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                已完成
              </button>
              <button
                v-else-if="lesson.status === 1"
                class="status-btn learning"
                @click.stop="handleLessonClick(lesson)"
              >
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <circle cx="6" cy="6" r="4" stroke="currentColor" stroke-width="1.5"/>
                  <path d="M6 3V6L7.5 7.5" stroke="currentColor" stroke-width="1" stroke-linecap="round"/>
                </svg>
                继续学习
              </button>
              <button
                v-else
                class="status-btn start"
                @click.stop="handleLessonClick(lesson)"
              >
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <polygon points="3 2 3 10 10 6" fill="currentColor"/>
                </svg>
                开始学习
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="chapterList.length === 0" class="empty-state">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
          <rect x="8" y="8" width="32" height="32" rx="4" stroke="#ddd" stroke-width="2"/>
          <path d="M16 20h16M16 24h16M16 28h10" stroke="#ddd" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <p>暂无课程内容</p>
      </div>
    </div>

    <!-- PDF 查看弹窗 -->
    <el-dialog
      v-model="pdfDialogVisible"
      title="课程资料"
      :width="900"
      :modal="isDrawerMode ? false : true"
      :append-to-body="true"
      :close-on-click-modal="true"
      class="pdf-dialog"
      destroy-on-close
    >
      <div class="pdf-viewer-container">
        <VuePdfEmbed
          v-if="currentPdfUrl"
          :source="currentPdfUrl"
          class="pdf-canvas"
        />
        <div v-else class="pdf-placeholder">
          <p>正在加载 PDF...</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import VuePdfEmbed from 'vue-pdf-embed';
import { getImgUrl } from '@/utils/index';
import type { CourseChapterItem, CourseLessonItem } from '@/api/content';

interface Props {
  chapterList: CourseChapterItem[];
  loading?: boolean;
  error?: string;
  isDrawerMode?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  error: '',
  isDrawerMode: false
});

const emit = defineEmits<{
  lessonClick: [lesson: CourseLessonItem];
}>();

// PDF 弹窗状态
const pdfDialogVisible = ref(false);
const currentPdfUrl = ref('');

// 切换章节展开/收起
const toggleChapter = (index: number) => {
  props.chapterList[index].isOpen = !props.chapterList[index].isOpen;
};

// 获取类型图标 SVG
const getTypeIcon = (type: string) => {
  switch (type) {
    case 'pdf':
      return `<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M4 2h6l3 3v9a1 1 0 01-1 1H4a1 1 0 01-1-1V3a1 1 0 011-1z" stroke="#ff6b6b" stroke-width="1.5" fill="none"/>
        <path d="M10 2v3h3" stroke="#ff6b6b" stroke-width="1.5" fill="none"/>
        <text x="8" y="11" text-anchor="middle" font-size="5" fill="#ff6b6b" font-weight="bold">PDF</text>
      </svg>`;
    case 'video':
      return `<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <circle cx="8" cy="8" r="6" stroke="#667eea" stroke-width="1.5" fill="none"/>
        <polygon points="6.5 5.5 6.5 10.5 11 8" fill="#667eea"/>
      </svg>`;
    default:
      return `<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <circle cx="8" cy="8" r="6" stroke="#999" stroke-width="1.5" fill="none"/>
        <circle cx="8" cy="8" r="2" fill="#999"/>
      </svg>`;
  }
};

// 处理课时点击
const handleLessonClick = (lesson: CourseLessonItem) => {
  if (!lesson.file_url) {
    return;
  }

  // 如果是 PDF 类型，在弹窗中打开
  if (lesson.type === 'pdf') {
    currentPdfUrl.value = getImgUrl(lesson.file_url);
    pdfDialogVisible.value = true;
  } else {
    // 其他类型（如视频）通过事件传递给父组件处理
    emit('lessonClick', lesson);
  }
};
</script>

<style scoped lang="scss">
.course-chapters-content {
  // 抽屉模式样式优化
  &.drawer-mode {
    .chapter-item {
      border-radius: 8px;
      margin-bottom: 8px;
    }

    .chapter-header {
      padding: 12px 16px;
    }

    .lesson-item {
      padding: 10px 16px 10px 40px;
    }

    .status-btn {
      font-size: 12px;
      padding: 4px 10px;
    }
  }
}

// 加载状态
.loading-state {
  padding: 20px;
}

// 错误状态
.error-state {
  padding: 40px 20px;
  text-align: center;
  color: #999;
  font-size: 14px;
}

// 章节列表
.chapters-list {
  display: flex;
  flex-direction: column;
  gap: 12px;

  .chapter-item {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;
    background: white;

    &.is-open {
      border-color: #667eea;
      box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);

      .chapter-header .arrow-icon {
        transform: rotate(0deg);
      }
    }

    .chapter-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 20px;
      background-color: #fafafa;
      cursor: pointer;
      user-select: none;
      transition: background-color 0.2s ease;

      &:hover {
        background-color: #f5f5f5;
      }

      .left {
        display: flex;
        align-items: center;
        gap: 10px;

        .arrow-icon {
          color: #999;
          transition: transform 0.3s ease;
          transform: rotate(-90deg);
          flex-shrink: 0;

          &.rotated {
            transform: rotate(0deg);
          }
        }

        .title {
          font-size: 15px;
          font-weight: 600;
          color: #1a1a1a;
        }
      }

      .right {
        .count {
          font-size: 12px;
          color: #999;
          background: #f5f5f5;
          padding: 2px 8px;
          border-radius: 10px;
        }
      }
    }

    .lesson-group {
      border-top: 1px solid #e5e7eb;
      background: white;

      .lesson-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 20px 14px 48px;
        border-bottom: 1px solid #f9f9f9;
        cursor: pointer;
        transition: all 0.2s ease;

        &:last-child {
          border-bottom: none;
        }

        &:hover {
          background-color: #fafafa;

          .lesson-title {
            color: #667eea;
          }

          .status-btn.start {
            border-color: #667eea;
            color: #667eea;
          }
        }

        .lesson-left {
          display: flex;
          align-items: center;
          gap: 10px;
          flex: 1;
          min-width: 0;

          .type-icon {
            flex-shrink: 0;
            display: flex;
            align-items: center;
          }

          .lesson-title {
            font-size: 14px;
            color: #555;
            transition: color 0.2s ease;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
        }

        .lesson-right {
          flex-shrink: 0;
        }
      }
    }
  }
}

// 状态按钮
.status-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  padding: 5px 12px;
  border-radius: 20px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;

  &.start {
    background-color: transparent;
    border-color: #e5e7eb;
    color: #666;

    &:hover {
      border-color: #667eea;
      color: #667eea;
      background-color: rgba(102, 126, 234, 0.05);
    }
  }

  &.learning {
    background-color: #fff7e6;
    color: #fa8c16;
    border-color: #ffd591;

    &:hover {
      background-color: #fa8c16;
      color: white;
      border-color: #fa8c16;
    }
  }

  &.finished {
    background-color: #e6fffb;
    color: #00c9a7;
    border-color: transparent;

    &:hover {
      background-color: #00c9a7;
      color: white;
    }
  }
}

// 空状态
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #999;

  p {
    margin-top: 16px;
    font-size: 14px;
  }
}

// PDF 对话框样式
:deep(.pdf-dialog) {
  .el-dialog__header {
    padding: 16px 20px;
    border-bottom: 1px solid #e5e7eb;
  }

  .el-dialog__body {
    padding: 0;
  }

  .el-dialog__close {
    &:hover {
      color: #667eea;
    }
  }
}

.pdf-viewer-container {
  width: 100%;
  height: 70vh;
  overflow: auto;
  background: #f5f5f5;
  display: flex;
  justify-content: center;
  padding: 20px;

  .pdf-canvas {
    background: white;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

    :deep(.vue-pdf-embed__page) {
      margin-bottom: 20px;
    }
  }

  .pdf-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;

    p {
      color: #999;
      font-size: 14px;
    }
  }
}
</style>

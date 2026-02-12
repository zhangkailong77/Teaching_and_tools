<template>
  <div class="training-platforms-section">
    <div class="section-header">
      <h3>实训平台入口</h3>
    </div>
    <div class="platforms-grid">
      <div
        v-for="platform in TRAINING_PLATFORMS"
        :key="platform.id"
        class="platform-card"
        :class="[
          { disabled: platform.status === 'coming-soon' },
          platform.id
        ]"
        @click="handlePlatformClick(platform)"
      >
        <!-- 图标区域 -->
        <div class="card-icon" :style="{ background: platform.gradient }">
          <template v-if="platform.iconType === 'emoji'">
            <span class="emoji-icon">{{ platform.icon }}</span>
          </template>
          <template v-else-if="platform.iconType === 'image'">
            <img :src="platform.icon" :alt="platform.name" class="image-icon" />
          </template>
          <template v-else>
            <!-- SVG 图标 -->
            <svg v-if="platform.id === 'shopee'" viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
            </svg>
            <svg v-else-if="platform.id === 'tiktok'" viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
              <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z"/>
            </svg>
          </template>
        </div>

        <!-- 内容区域 -->
        <div class="card-content">
          <span class="platform-name">{{ platform.name }}</span>
          <span class="platform-desc">{{ platform.description }}</span>
        </div>

        <!-- 状态标识 -->
        <span v-if="platform.status === 'coming-soon'" class="coming-soon-badge">敬请期待</span>

        <!-- 箭头图标 -->
        <div class="card-arrow">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { TRAINING_PLATFORMS } from '@/config/training-platforms';

const router = useRouter();

const handlePlatformClick = (platform: any) => {
  if (platform.status === 'coming-soon') {
    ElMessage.info(`${platform.name} 实训功能开发中，敬请期待！`);
    return;
  }

  if (platform.route) {
    router.push(platform.route);
  }
};
</script>

<style scoped lang="scss">
.training-platforms-section {
  margin-bottom: 30px;
}

.section-header {
  margin-bottom: 16px;

  h3 {
    font-size: 18px;
    color: #2d3436;
    font-weight: 600;
    margin: 0;
  }
}

.platforms-grid {
  display: flex;
  gap: 20px;
}

.platform-card {
  flex: 1;
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
  border: 1px solid #f5f7fa;
  position: relative;
  overflow: hidden;

  &:hover:not(.disabled) {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    border-color: #00c9a7;

    .card-arrow {
      transform: translateX(4px);
      color: #00c9a7;
    }
  }

  &.disabled {
    opacity: 0.7;
    cursor: not-allowed;

    &:hover {
      transform: none;
    }

    .card-arrow {
      color: #ccc;
    }
  }
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: #f5f7fa;

  .emoji-icon {
    font-size: 28px;
  }

  .image-icon {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 14px;
  }

  svg {
    color: white;
  }
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 0;

  .platform-name {
    font-size: 16px;
    font-weight: 600;
    color: #2d3436;
  }

  .platform-desc {
    font-size: 13px;
    color: #999;
  }
}

.coming-soon-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255, 107, 53, 0.1);
  color: #FF6B35;
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.card-arrow {
  color: #00c9a7;
  transition: transform 0.2s ease, color 0.2s ease;
  flex-shrink: 0;
}

// ComfyUI - 图片图标带渐变背景
.platform-card.comfyui .card-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

// Shopee - 橙色渐变（已在配置中定义）

// TikTok - 渐变（已在配置中定义）

// AI+智能体编排 - 图片图标
.platform-card.ai-agent .card-icon {
  background: transparent;
  padding: 0;
}
</style>

/**
 * 实训平台配置
 *
 * 定义系统中所有实训平台的入口信息
 */

export interface TrainingPlatform {
  id: string;                    // 平台唯一标识
  name: string;                  // 平台名称
  description: string;           // 平台描述
  icon: string;                  // 图标（emoji或图片URL）
  iconType?: 'emoji' | 'svg' | 'image'; // 图标类型
  gradient?: string;             // 渐变背景（可选）
  route?: string;                // 路由路径（已实现的平台）
  status: 'available' | 'coming-soon'; // 状态：可用/即将推出
  courseKeyword?: string;        // 对应课程关键词（用于关联课程）
}

/**
 * 4个实训平台配置列表
 *
 * ComfyUI 已实现，其他3个平台标记为"敬请期待"
 */
export const TRAINING_PLATFORMS: TrainingPlatform[] = [
  {
    id: 'comfyui',
    name: 'ComfyUI',
    description: 'AI+跨境电商视觉营销设计',
    icon: new URL('@/assets/comfyui.png', import.meta.url).href,
    iconType: 'image',
    route: '/dashboard/teacher/comfyui',
    status: 'available',
    courseKeyword: 'AI'
  },
  {
    id: 'shopee',
    name: 'Shopee',
    description: '跨境电商实训',
    icon: '',
    iconType: 'svg',
    gradient: 'linear-gradient(135deg, #FF6B35 0%, #F7931E 100%)',
    status: 'coming-soon'
  },
  {
    id: 'tiktok',
    name: 'TikTok',
    description: '短视频运营实训',
    icon: '',
    iconType: 'svg',
    gradient: 'linear-gradient(135deg, #00F2EA 0%, #1a1a2e 50%, #FF0050 100%)',
    status: 'coming-soon'
  },
  {
    id: 'ai-agent',
    name: 'AI+智能体编排',
    description: '跨境客服应用',
    icon: new URL('@/assets/dify-color.png', import.meta.url).href,
    iconType: 'image',
    status: 'coming-soon'
  }
];

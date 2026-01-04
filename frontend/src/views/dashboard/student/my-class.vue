<template>
  <div class="dashboard-container">
    <StudentSidebar />

    <main class="main-content">
      <header class="top-bar">
        <div class="breadcrumb">
          <span>工作台</span> / <span class="current">我的班级</span>
        </div>
      </header>

      <div v-if="myClasses.length === 0" class="empty-state">
        <p>📭 你还没有加入任何班级</p>
        <p>请联系教师分发账号或添加班级。</p>
      </div>

      <!-- 遍历学生加入的所有班级 -->
      <div class="class-card-wrapper" v-for="cls in myClasses" :key="cls.id">
        
        <!-- 1. 班级名片 (顶部大图 + 信息) -->
        <div class="class-header-card" :style="{ backgroundImage: `url(${getImgUrl(cls.cover_image)})` }">
          <div class="header-overlay">
            <h1>{{ cls.name }}</h1>
            <p class="description">{{ cls.description || '这是该班级的简介，了解班级情况。' }}</p>
            <div class="class-meta">
              <span>📅 {{ formatDuration(cls.start_date, cls.end_date) }}</span>
              <span>👥 共 {{ cls.student_count }} 位同学</span>
            </div>
          </div>
        </div>

        <!-- 2. 授课教师信息 -->
        <div class="teacher-profile-card">
          <div class="left">
            <img 
              v-if="cls.teacher_avatar" 
              :src="getImgUrl(cls.teacher_avatar)" 
              class="t-avatar" 
              alt="Teacher"
            />
            <div v-else class="t-avatar text-placeholder">
              {{ getFirstChar(cls.teacher_name) }}
            </div>
            <div class="info">
              <h3>{{ cls.teacher_name }}</h3>
              <p class="title">{{ cls.teacher_title }}</p>
            </div>
          </div>
          <div class="right">
            <p class="school-info">{{ cls.teacher_school }} · {{ cls.teacher_college }}</p>
            <p class="intro">{{ cls.teacher_intro || '该老师暂无个人简介' }}</p>
          </div>
        </div>

        <!-- 3. 同学风采 (头像墙) -->
        <div class="classmates-section">
          <h2>同班同学 (共 {{ classmates.length }} 人)</h2>
          <div class="classmates-grid">
            <div class="mate-item" v-for="mate in classmates" :key="mate.name">
              <img 
                v-if="mate.avatar" 
                :src="getImgUrl(mate.avatar)" 
                class="mate-avatar" 
                alt="Mate" 
              />
              <div v-else class="mate-avatar text-placeholder">
                {{ getFirstChar(mate.name) }}
              </div>
              <span>{{ mate.name }}</span>
            </div>
          </div>
        </div>

      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/modules/user';
import StudentSidebar from '@/components/StudentSidebar.vue';
import { getMyEnrolledClasses, getClassmates, type ClassItem, type ClassmateItem } from '@/api/course'; // ✅ 引入所有API
import { getImgUrl } from '@/utils/index';

const router = useRouter();
const userStore = useUserStore();

const myClasses = ref<ClassItem[]>([]);
const classmates = ref<ClassmateItem[]>([]); // 存储同学列表

const defaultTeacherAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png';
const getFirstChar = (name?: string) => {
  return name ? name.charAt(0).toUpperCase() : '?';
};

onMounted(() => {
  userStore.fetchUserInfo(); // 获取学生自己信息
  fetchMyClassData();
});

const fetchMyClassData = async () => {
  try {
    const classes = await getMyEnrolledClasses(); // 获取学生加入的班级
    myClasses.value = classes;

    // 如果加入了班级，就获取第一个班的同学列表 (简单处理，假设学生只有一个主班)
    if (classes.length > 0) {
      const firstClassId = classes[0].id;
      const mates = await getClassmates(firstClassId);
      classmates.value = mates;
    }
  } catch (error) {
    console.error("加载我的班级数据失败", error);
  }
};

// 格式化时间段
const formatDuration = (start?: string, end?: string) => {
  if (!start) return '时间待定';
  const s = start.split('T')[0];
  if (end) {
    const e = end.split('T')[0];
    return `${s} 至 ${e}`;
  }
  return `${s} 开课`;
};
</script>

<style scoped lang="scss">
$sidebar-width: 240px;
$primary-color: #00c9a7;
$bg-color: #f5f6fa;
$text-dark: #2d3436;
$text-gray: #a4b0be;

.dashboard-container { display: flex; width: 100vw; height: 100vh; background-color: $bg-color; font-family: 'Inter', sans-serif; overflow: hidden; }
.main-content { flex: 1; padding: 30px 40px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; }

.top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
  .breadcrumb { font-size: 14px; color: $text-gray; .current { color: $text-dark; font-weight: 600; } }
  .btn-primary { background: $primary-color; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; transition: filter 0.2s; &:hover { filter: brightness(0.9); } }
}

/* 空状态 */
.empty-state { text-align: center; padding: 80px; color: #999; border: 2px dashed #eee; border-radius: 15px; margin-top: 30px; }

/* 班级卡片整体包装 */
.class-card-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 20px;
}

/* 1. 班级名片顶部卡片 */
.class-header-card {
  width: 100%;
  height: 200px; /* 固定高度，大气 */
  background-color: #f0f2f5;
  background-size: cover;
  background-position: center;
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 10px 30px rgba(0,0,0,0.08);

  .header-overlay {
    position: absolute; inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 100%);
    display: flex; flex-direction: column; justify-content: flex-end;
    padding: 25px;
    color: white;

    h1 { font-size: 28px; margin-bottom: 10px; line-height: 1.2; }
    .description { font-size: 14px; opacity: 0.9; margin-bottom: 15px; }
    .class-meta { font-size: 13px; opacity: 0.8; display: flex; gap: 20px; }
  }
}

/* 2. 授课教师名片 */
.teacher-profile-card {
  background: white;
  border-radius: 16px;
  padding: 25px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.02);
  display: flex;
  align-items: center;
  gap: 30px;
  
  .left {
    display: flex; align-items: center; gap: 15px;
    .t-avatar { width: 60px; height: 60px; border-radius: 50%; object-fit: cover; border: 3px solid #e0f2f1; }
    .info {
      h3 { font-size: 18px; color: $text-dark; margin-bottom: 5px; }
      .title { font-size: 13px; color: $primary-color; font-weight: 600; }
    }
  }

  .right {
    flex: 1;
    .school-info { font-size: 13px; color: #666; margin-bottom: 5px; }
    .intro { font-size: 13px; color: #999; line-height: 1.5; }
  }
}

/* 3. 同学风采 */
.classmates-section {
  background: white;
  border-radius: 16px;
  padding: 25px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.02);
  
  h2 { font-size: 18px; color: $text-dark; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; }

  .classmates-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); /* 每行 100px，自动填充 */
    gap: 20px;
    
    .mate-item {
      display: flex; flex-direction: column; align-items: center; text-align: center;
      .mate-avatar { width: 70px; height: 70px; border-radius: 50%; object-fit: cover; border: 2px solid #f0f2f5; margin-bottom: 8px; }
      span { font-size: 13px; color: $text-dark; }
    }
  }
}

.text-placeholder {
  background-color: #e0f2f1; /* 浅青色背景 */
  color: $primary-color;     /* 深青色文字 */
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  /* 移除图片特有的 object-fit，防止冲突 */
  object-fit: unset; 
}

/* 针对老师文字头像微调字体 */
.t-avatar.text-placeholder {
  font-size: 24px;
}

/* 针对同学文字头像微调字体 */
.mate-avatar.text-placeholder {
  font-size: 28px;
}
</style>
<template>
  <div class="layout-wrapper">
    <el-menu
      :default-active="activeIndex"
      class="top-menu"
      mode="horizontal"
      @select="handleSelect"
      background-color="#545c64"
      text-color="#fff"
      active-text-color="#ffd04b"
      :ellipsis="false"
      router
    >
      <el-menu-item index="/">
        <img
          src="https://vuejs.org/images/logo.png"
          style="width: 30px; margin-right: 10px"
        />
        <span>管理系統</span>
      </el-menu-item>

      <el-sub-menu index="erp">
        <template #title>ERP 管理</template>
        <el-menu-item index="/materials/list"> 材料管理 </el-menu-item>
      </el-sub-menu>

      <div class="flex-grow" />

      <div class="menu-right-items">
        <Notice />

        <el-dropdown @command="handleCommand" trigger="click">
          <div class="user-menu">
            <el-avatar
              :size="30"
              src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
              style="margin-left: 20px"
            />
            <span class="username">{{ username }}</span>
          </div>

          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">個人資訊</el-dropdown-item>
              <el-dropdown-item divided command="logout">
                安全登出
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-menu>

    <main class="page-content">
      <router-view />
    </main>

    <footer class="status-bar">
      <div class="status-left">
        <el-tag size="small" type="success" effect="dark">系統連線中</el-tag>
        <span class="status-item">環境：Production</span>
        <span class="status-item">伺服器：IIS-Server-01</span>
      </div>
      <div class="status-right">
        <span class="status-item">目前使用者：{{ username }} ({{ role }})</span>
        <el-divider direction="vertical" />
        <span class="status-item">系統版本：v1.0.53</span>
        <el-divider direction="vertical" />
        <span class="status-item">系統時間：{{ currentTime }}</span>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessageBox, ElMessage } from "element-plus";
import Notice from "../components/Notice.vue";
import { clearAuthSession, getStoredUser } from "../api/http";

const route = useRoute();
const router = useRouter();
const activeIndex = ref("/");
const currentTime = ref(new Date().toLocaleString());
const storedUser = getStoredUser();
const username = ref(storedUser?.username || "Guest");
const role = ref(storedUser?.role || "-");
let timer: ReturnType<typeof setInterval> | undefined;

watch(
  () => route.path,
  (newPath) => {
    activeIndex.value = newPath;
  },
  { immediate: true },
);

const handleSelect = (key: string) => {
  activeIndex.value = key;
};

onMounted(() => {
  timer = setInterval(() => {
    currentTime.value = new Date().toLocaleString();
  }, 1000);
});

onUnmounted(() => {
  if (timer) {
    clearInterval(timer);
  }
});

const handleCommand = (command: string) => {
  if (command === "logout") {
    ElMessageBox.confirm("您確定要退出系統嗎？", "提示", {
      confirmButtonText: "確定",
      cancelButtonText: "取消",
      type: "warning",
    })
      .then(() => {
        clearAuthSession();
        ElMessage.success("已成功登出");
        router.push("/login");
      })
      .catch(() => {});
  }
};
</script>

<style scoped>
.layout-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.top-menu {
  display: flex;
  align-items: center;
  width: 100%;
  flex-shrink: 0;
}

.flex-grow {
  flex-grow: 1;
}

.menu-right-items {
  display: flex;
  align-items: center;
  padding: 0 25px;
  color: white;
}

.user-menu {
  display: flex;
  align-items: center;
  cursor: pointer;
  outline: none;
}

.username {
  margin-left: 8px;
  font-size: 14px;
}

.page-content {
  flex: 1;
  padding: 20px;
  background-color: #f5f7fa;
  overflow-y: auto;
}

.status-bar {
  height: 28px;
  background-color: #333333;
  border-top: 1px solid #1a1a1a;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 15px;
  font-size: 12px;
  color: #cccccc;
  flex-shrink: 0;
  user-select: none;
}

.status-item {
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  color: #bbbbbb;
}

.el-divider--vertical {
  border-left: 1px solid #555555;
}

.status-left,
.status-right {
  display: flex;
  align-items: center;
  gap: 15px;
}
</style>

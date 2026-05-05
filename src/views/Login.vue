<template>
  <div class="login-wrapper">
    <el-card class="login-card">
      <template #header>
        <div class="login-header">
          <img
            src="https://vuejs.org/images/logo.png"
            alt="Logo"
            class="logo"
          />
          <h2>系統管理後台</h2>
        </div>
      </template>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-width="0px"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="請輸入帳號"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="請輸入密碼"
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            立即登入
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, type FormInstance } from "element-plus";
import { apiClient, saveAuthSession, type AuthUser } from "../api/http";

type LoginResponse = {
  status: string;
  token: string;
  user: AuthUser;
};

const router = useRouter();
const loginFormRef = ref<FormInstance>();
const loading = ref(false);

const loginForm = reactive({
  username: "",
  password: "",
});

const loginRules = reactive({
  username: [{ required: true, message: "請輸入帳號", trigger: "blur" }],
  password: [
    { required: true, message: "請輸入密碼", trigger: "blur" },
    { min: 6, message: "密碼長度不能小於 6 位", trigger: "blur" },
  ],
});

const handleLogin = async () => {
  if (!loginFormRef.value) {
    return;
  }

  await loginFormRef.value.validate();
  loading.value = true;

  try {
    const res = await apiClient.post<LoginResponse>("/api/auth/login", {
      username: loginForm.username,
      password: loginForm.password,
    });

    saveAuthSession(res.data.token, res.data.user);
    ElMessage.success("登入成功");
    router.push("/");
  } catch {
    ElMessage.error("帳號或密碼錯誤");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-wrapper {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #2d3a4b;
  background-image: radial-gradient(
    circle at 50% 50%,
    #3e4e5e 0%,
    #2d3a4b 100%
  );
}

.login-card {
  width: 400px;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.login-header {
  text-align: center;
}

.logo {
  width: 50px;
  margin-bottom: 10px;
}

.login-header h2 {
  margin: 0;
  color: #333;
  font-size: 22px;
}

.login-btn {
  width: 100%;
  padding: 20px 0;
  font-size: 16px;
  margin-top: 10px;
}
</style>

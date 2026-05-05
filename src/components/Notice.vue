<template>
  <el-popover placement="bottom" :width="400" trigger="click">
    <template #reference>
      <el-badge :value="9" class="item" style="cursor: pointer">
        <el-icon :size="20"><Bell /></el-icon>
      </el-badge>
    </template>

    <el-tabs v-model="activeName">
      <el-tab-pane label="消息(3)" name="msg">
        <div class="notice-item">系統升級通知：服務器將於今晚12點...</div>
        <div class="notice-item">新功能發布：現在支持多語言...</div>
        <div class="notice-item">重要提醒：請定期更改密碼...</div>
      </el-tab-pane>
      <el-tab-pane label="通知(3)" name="notice">
        <div class="notice-item">系統升級通知：123</div>
        <div class="notice-item">新功能發布：123</div>
        <div class="notice-item">重要提醒：123</div>
      </el-tab-pane>

      <el-tab-pane label="待辦(3)" name="todo"
        ><div class="notice-item">系統升級通知：A</div>
        <div class="notice-item">新功能發布：B</div>
        <div class="notice-item">重要提醒：C</div>
      </el-tab-pane>
    </el-tabs>

    <div
      style="
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
        border-top: 1px solid #eee;
        padding-top: 10px;
      "
    >
      <el-button link>查看更多 ></el-button>
      <el-button link>全部已讀</el-button>
    </div>
  </el-popover>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Bell } from "@element-plus/icons-vue"; // 記得導入圖示
const activeName = ref("msg");
</script>

<style scoped>
.notice-item {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}
</style>

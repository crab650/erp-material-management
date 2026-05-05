<template>
  <div>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>會員管理</el-breadcrumb-item>
      <el-breadcrumb-item>會員列表</el-breadcrumb-item>
    </el-breadcrumb>
    <div style="margin-top: 20px">
      <h2>會員清單</h2>
      <el-table :data="[]" style="width: 100%" border>
        <el-table-column prop="id" label="編號" width="80" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column label="操作" width="120">
          <template #default>
            <el-button link type="primary">編輯</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

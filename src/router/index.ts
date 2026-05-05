import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import MainLayout from "../layout/MainLayout.vue";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    component: MainLayout,
    children: [
      {
        path: "",
        name: "Home",
        component: () => import("../views/Home.vue"),
      },
      {
        path: "member/list",
        name: "MemberList",
        component: () => import("../views/Member/List.vue"),
      },
      {
        path: "materials/list",
        name: "MaterialList",
        component: () => import("../views/materials/List.vue"),
      },
    ],
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/Login.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

<template>
  <div class="material-page">
    <div class="erp-title-bar">
      <div>
        <span class="window-title">ERP 材料主檔維護</span>
        <span class="window-subtitle">MFBA110 - Material Basic Data</span>
      </div>
      <div class="window-status">F2 Query | F4 Add | F5 Refresh</div>
    </div>

    <div class="erp-toolbar">
      <el-button type="primary" @click="fetchMaterials">查詢</el-button>
      <el-button type="primary" @click="openCreateDialog">新增</el-button>
      <el-button @click="fetchMaterials">重新整理</el-button>
    </div>

    <el-card class="search-card" shadow="never">
      <template #header>
        <div class="section-header">查詢條件</div>
      </template>

      <el-form :model="queryForm" label-width="72px" class="query-form">
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="關鍵字">
              <el-input
                v-model="queryForm.keyword"
                placeholder="件號 / 名稱 / 英文名稱 / 規格 / 圖號"
                clearable
                @keyup.enter="fetchMaterials"
              />
            </el-form-item>
          </el-col>
          <el-col :span="5">
            <el-form-item label="狀態">
              <el-select v-model="queryForm.status" style="width: 100%">
                <el-option label="全部" value="" />
                <el-option label="啟用" value="active" />
                <el-option label="停用" value="inactive" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="類別">
              <el-input v-model="queryForm.category" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <div class="record-count">筆數：{{ materials.length }}</div>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <div class="grid-shell">
      <div class="section-header">材料清單</div>
      <el-table
        v-loading="loading"
        :data="materials"
        border
        height="510"
        class="data-table"
        highlight-current-row
      >
        <el-table-column type="index" label="序" width="52" fixed />
        <el-table-column prop="materialCode" label="件號" width="150" fixed />
        <el-table-column prop="materialName" label="名稱" min-width="180" />
        <el-table-column prop="englishName" label="英文名稱" min-width="180" />
        <el-table-column prop="specification" label="規格說明" min-width="180" show-overflow-tooltip />
        <el-table-column prop="productLine" label="產品線" width="110" />
        <el-table-column prop="stockCategory" label="庫存分類" width="116" />
        <el-table-column prop="unit" label="單位" width="74" />
        <el-table-column prop="currentStock" label="目前庫存" width="110" align="right" />
        <el-table-column prop="safetyStock" label="安全庫存" width="110" align="right" />
        <el-table-column label="狀態" width="82">
          <template #default="{ row }">
            <span class="erp-badge" :class="row.status === 'active' ? 'ok' : 'muted'">
              {{ row.status === "active" ? "啟用" : "停用" }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="230" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEditDialog(row)">編輯</el-button>
            <el-button link type="primary" @click="openTransactionDialog(row)">異動</el-button>
            <el-button
              link
              :type="row.status === 'active' ? 'warning' : 'success'"
              @click="toggleStatus(row)"
            >
              {{ row.status === "active" ? "停用" : "啟用" }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="materialDialogVisible"
      :title="editingMaterialId ? '材料主檔維護 - 編輯' : '材料主檔維護 - 新增'"
      width="880px"
      class="erp-dialog"
    >
      <div class="form-window">
        <el-tabs v-model="activeTab" type="card" class="erp-tabs">
          <el-tab-pane label="General" name="general" />
          <el-tab-pane label="計劃" name="plan" />
          <el-tab-pane label="庫存" name="stock" />
          <el-tab-pane label="採購" name="purchase" />
          <el-tab-pane label="成本" name="cost" />
          <el-tab-pane label="自訂" name="custom" />
        </el-tabs>

        <el-form
          ref="materialFormRef"
          :model="materialForm"
          :rules="materialRules"
          label-width="106px"
          class="master-form"
          @click.capture="setHelpFromLabelClick"
        >
          <div class="form-body">
            <div class="form-main">
          <div v-show="activeTab === 'general'" class="form-section">
            <div class="section-header compact">一般屬性</div>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="件號" prop="materialCode">
                  <el-input v-model="materialForm.materialCode" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="狀態">
                  <el-select v-model="materialForm.status" style="width: 100%">
                    <el-option label="啟用" value="active" />
                    <el-option label="停用" value="inactive" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="名稱" prop="materialName">
                  <el-input v-model="materialForm.materialName" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="英文名稱">
                  <el-input v-model="materialForm.englishName" />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="規格說明">
                  <el-input v-model="materialForm.specification" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="中文詳細規格">
                  <el-input v-model="materialForm.chineseSpec" type="textarea" :rows="3" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="英文詳細規格">
                  <el-input v-model="materialForm.englishSpec" type="textarea" :rows="3" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <div v-show="activeTab === 'plan'" class="form-section">
            <div class="section-header compact">Plan Attributes</div>
            <el-row :gutter="12">
              <el-col :span="8">
                <el-form-item label="Source">
                  <el-select v-model="materialForm.sourceType" style="width: 100%">
                    <el-option label="In-house" value="in_house" />
                    <el-option label="Purchase" value="purchase" />
                    <el-option label="Subcontract" value="subcontract" />
                    <el-option label="Transfer" value="transfer" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="MRP Plan">
                  <el-select v-model="materialForm.isPlanned" style="width: 100%">
                    <el-option label="yes" value="yes" />
                    <el-option label="no" value="no" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="Stock Ctrl">
                  <el-select v-model="materialForm.isInventoryControlled" style="width: 100%">
                    <el-option label="yes" value="yes" />
                    <el-option label="no" value="no" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="Virtual Part">
                  <el-select v-model="materialForm.isVirtualPart" style="width: 100%">
                    <el-option label="no" value="no" />
                    <el-option label="yes" value="yes" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="Order Policy">
                  <el-input v-model="materialForm.orderPolicy" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="Lot Rule">
                  <el-input v-model="materialForm.lotRule" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Lead Days">
                  <el-input v-model.number="materialForm.leadTimeDays" type="number" min="0" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Mfg Days">
                  <el-input v-model.number="materialForm.manufacturingLeadDays" type="number" min="0" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Safety Days">
                  <el-input v-model.number="materialForm.safetyTimeDays" type="number" min="0" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Order Cycle">
                  <el-input v-model.number="materialForm.orderCycleDays" type="number" min="0" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Max Qty">
                  <el-input v-model.number="materialForm.maxOrderQty" type="number" min="0" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Fixed Qty">
                  <el-input v-model.number="materialForm.fixedOrderQty" type="number" min="0" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="EOQ">
                  <el-input v-model.number="materialForm.economicOrderQty" type="number" min="0" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Multiple Qty">
                  <el-input v-model.number="materialForm.multipleQty" type="number" min="0" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Reserved Qty">
                  <el-input v-model.number="materialForm.reservedQty" type="number" min="0" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Warehouse">
                  <el-input v-model="materialForm.warehousePlanner" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Buyer">
                  <el-input v-model="materialForm.buyer" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Planner">
                  <el-input v-model="materialForm.productionPlanner" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Subcontract">
                  <el-input v-model="materialForm.subcontractPlanner" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Substitute">
                  <el-input v-model="materialForm.substituteCode" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Process">
                  <el-input v-model="materialForm.processCode" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="Start Dept">
                  <el-input v-model="materialForm.startupDepartment" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <div v-show="activeTab === 'stock'" class="form-section">
            <div class="section-header compact">分類與庫存</div>
            <el-row :gutter="12">
              <el-col :span="8">
                <el-form-item label="計量單位" prop="unit">
                  <el-input v-model="materialForm.unit" placeholder="PCS / KG / M" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="產品線">
                  <el-input v-model="materialForm.productLine" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="次產品線">
                  <el-input v-model="materialForm.subProductLine" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="庫存分類">
                  <el-input v-model="materialForm.stockCategory" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="庫存次分類">
                  <el-input v-model="materialForm.stockSubcategory" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="庫存自定分類">
                  <el-input v-model="materialForm.stockCustomCategory" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="原類別">
                  <el-input v-model="materialForm.category" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="安全庫存">
                  <el-input-number
                    v-model="materialForm.safetyStock"
                    :min="0"
                    :precision="2"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <div v-show="activeTab === 'custom'" class="form-section">
            <div class="section-header compact">工程與維護</div>
            <el-row :gutter="12">
              <el-col :span="8">
                <el-form-item label="工程圖號">
                  <el-input v-model="materialForm.drawingNo" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="設變編號">
                  <el-input v-model="materialForm.engineeringChangeNo" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="維護人員">
                  <el-input v-model="materialForm.maintainer" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
          <div v-show="activeTab === 'purchase'" class="empty-tab">
            Purchase attributes will be maintained here.
          </div>
          <div v-show="activeTab === 'cost'" class="empty-tab">
            Cost attributes will be maintained here.
          </div>
            </div>

          </div>
          <aside class="field-help-panel">
            <div class="help-title">欄位說明</div>
            <div class="help-head">
              <span class="help-code">{{ activeFieldHelp.code }}</span>
              <span class="help-name">{{ activeFieldHelp.title }}</span>
            </div>
            <div class="help-grid">
              <div>
                <span>用途</span>
                <p>{{ activeFieldHelp.description }}</p>
              </div>
              <div>
                <span>影響</span>
                <p>{{ activeFieldHelp.impact }}</p>
              </div>
              <div>
                <span>範例</span>
                <p>{{ activeFieldHelp.example }}</p>
              </div>
            </div>
          </aside>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="materialDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveMaterial">
          儲存
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="transactionDialogVisible"
      title="庫存異動"
      width="520px"
      class="erp-dialog"
    >
      <el-descriptions v-if="selectedMaterial" :column="1" border size="small">
        <el-descriptions-item label="材料">
          {{ selectedMaterial.materialCode }} - {{ selectedMaterial.materialName }}
        </el-descriptions-item>
        <el-descriptions-item label="目前庫存">
          {{ selectedMaterial.currentStock }} {{ selectedMaterial.unit }}
        </el-descriptions-item>
      </el-descriptions>

      <el-form
        ref="transactionFormRef"
        :model="transactionForm"
        :rules="transactionRules"
        label-width="90px"
        class="transaction-form"
      >
        <el-form-item label="異動類型" prop="transactionType">
          <el-select v-model="transactionForm.transactionType" style="width: 100%">
            <el-option label="入庫" value="in" />
            <el-option label="出庫" value="out" />
            <el-option label="調整" value="adjust" />
          </el-select>
        </el-form-item>
        <el-form-item label="數量" prop="quantity">
          <el-input-number
            v-model="transactionForm.quantity"
            :min="0"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="倉庫">
          <el-input v-model="transactionForm.warehouse" />
        </el-form-item>
        <el-form-item label="參考單號">
          <el-input v-model="transactionForm.referenceNo" />
        </el-form-item>
        <el-form-item label="備註">
          <el-input v-model="transactionForm.remark" type="textarea" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="transactionDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveTransaction">
          儲存異動
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox, type FormInstance } from "element-plus";
import { apiClient } from "../../api/http";

type Material = {
  id: number;
  materialCode: string;
  materialName: string;
  englishName: string;
  specification: string;
  chineseSpec: string;
  englishSpec: string;
  unit: string;
  category: string;
  productLine: string;
  subProductLine: string;
  stockCategory: string;
  stockSubcategory: string;
  stockCustomCategory: string;
  drawingNo: string;
  engineeringChangeNo: string;
  maintainer: string;
  sourceType: string;
  isPlanned: string;
  isInventoryControlled: string;
  isVirtualPart: string;
  orderPolicy: string;
  lotRule: string;
  leadTimeDays: number;
  manufacturingLeadDays: number;
  safetyTimeDays: number;
  maxOrderQty: number;
  fixedOrderQty: number;
  economicOrderQty: number;
  orderCycleDays: number;
  multipleQty: number;
  reservedQty: number;
  warehousePlanner: string;
  buyer: string;
  productionPlanner: string;
  subcontractPlanner: string;
  substituteCode: string;
  processCode: string;
  startupDepartment: string;
  safetyStock: number;
  currentStock: number;
  status: "active" | "inactive";
};

const loading = ref(false);
const saving = ref(false);
const materials = ref<Material[]>([]);
const materialDialogVisible = ref(false);
const transactionDialogVisible = ref(false);
const editingMaterialId = ref<number | null>(null);
const selectedMaterial = ref<Material | null>(null);
const materialFormRef = ref<FormInstance>();
const transactionFormRef = ref<FormInstance>();
const activeTab = ref("general");

const queryForm = reactive({
  keyword: "",
  status: "",
  category: "",
});

const materialForm = reactive({
  materialCode: "",
  materialName: "",
  englishName: "",
  specification: "",
  chineseSpec: "",
  englishSpec: "",
  unit: "",
  category: "",
  productLine: "",
  subProductLine: "",
  stockCategory: "",
  stockSubcategory: "",
  stockCustomCategory: "",
  drawingNo: "",
  engineeringChangeNo: "",
  maintainer: "",
  sourceType: "purchase",
  isPlanned: "yes",
  isInventoryControlled: "yes",
  isVirtualPart: "no",
  orderPolicy: "",
  lotRule: "",
  leadTimeDays: 0,
  manufacturingLeadDays: 0,
  safetyTimeDays: 0,
  maxOrderQty: 0,
  fixedOrderQty: 0,
  economicOrderQty: 0,
  orderCycleDays: 0,
  multipleQty: 0,
  reservedQty: 0,
  warehousePlanner: "",
  buyer: "",
  productionPlanner: "",
  subcontractPlanner: "",
  substituteCode: "",
  processCode: "",
  startupDepartment: "",
  safetyStock: 0,
  status: "active" as "active" | "inactive",
});

const transactionForm = reactive({
  transactionType: "in" as "in" | "out" | "adjust",
  quantity: 0,
  warehouse: "MAIN",
  referenceNo: "",
  remark: "",
});

const materialRules = reactive({
  materialCode: [{ required: true, message: "請輸入件號", trigger: "blur" }],
  materialName: [{ required: true, message: "請輸入名稱", trigger: "blur" }],
  unit: [{ required: true, message: "請輸入計量單位", trigger: "blur" }],
});

type FieldHelp = {
  code: string;
  title: string;
  description: string;
  impact: string;
  example: string;
};

const defaultFieldHelp: FieldHelp = {
  code: "ERP-FIELD",
  title: "Field Help",
  description: "Click a field label in the form to view its ERP purpose.",
  impact: "This panel explains how the selected field affects material, stock, purchasing, planning, or MRP behavior.",
  example: "Select Source, MRP Plan, Lead Days, Safety Stock, Buyer, or other labels.",
};

const fieldHelpMap: Record<string, FieldHelp> = {
  Source: {
    code: "sourceType",
    title: "Source / 來源別",
    description: "Defines how this material is supplied: in-house production, purchase, subcontract, or transfer.",
    impact: "MRP uses this to decide whether demand becomes a production suggestion, purchase request, subcontract order, or transfer request.",
    example: "Purchase = buy from supplier; In-house = create production order.",
  },
  "MRP Plan": {
    code: "isPlanned",
    title: "MRP Plan / 計劃否",
    description: "Controls whether this material participates in MRP demand planning.",
    impact: "If set to no, the material is ignored by MRP planning suggestions.",
    example: "yes for raw materials and components; no for non-planned service items.",
  },
  "Stock Ctrl": {
    code: "isInventoryControlled",
    title: "Stock Control / 庫存管制",
    description: "Controls whether the system tracks on-hand inventory for this material.",
    impact: "Stock-controlled materials affect available quantity, issue, receipt, and shortage checks.",
    example: "yes for steel sheet; no for a service charge item.",
  },
  "Virtual Part": {
    code: "isVirtualPart",
    title: "Virtual Part / 虛擬件",
    description: "Marks a non-stocked BOM grouping item used to organize lower-level components.",
    impact: "MRP can explode through virtual parts without treating them as stocked inventory.",
    example: "A phantom assembly in BOM structure.",
  },
  "Order Policy": {
    code: "orderPolicy",
    title: "Order Policy / 訂購政策",
    description: "Defines the replenishment strategy for this material.",
    impact: "Affects when and how purchase or production suggestions are generated.",
    example: "ROP, Periodic, Lot-for-lot, Fixed quantity.",
  },
  "Lot Rule": {
    code: "lotRule",
    title: "Lot Rule / 批量法則",
    description: "Defines how suggested order quantities are rounded or calculated.",
    impact: "MRP uses this with fixed quantity, multiple quantity, and EOQ settings.",
    example: "Fixed lot, multiple lot, economic lot.",
  },
  "Lead Days": {
    code: "leadTimeDays",
    title: "Lead Days / 前置時間",
    description: "The expected days from order release to material availability.",
    impact: "MRP offsets planned orders earlier by this number of days.",
    example: "Supplier delivery takes 14 days.",
  },
  "Mfg Days": {
    code: "manufacturingLeadDays",
    title: "Mfg Days / 製令前置日",
    description: "The expected manufacturing days for in-house production items.",
    impact: "Production planning uses it to schedule start and finish dates.",
    example: "Assembly requires 3 working days.",
  },
  "Safety Days": {
    code: "safetyTimeDays",
    title: "Safety Days / 安全時間",
    description: "Extra buffer days added before the required date.",
    impact: "Helps reduce late delivery risk by moving planned supply earlier.",
    example: "Add 2 days for supplier uncertainty.",
  },
  "Order Cycle": {
    code: "orderCycleDays",
    title: "Order Cycle / 訂購週期",
    description: "Defines how often replenishment should be reviewed or grouped.",
    impact: "Periodic planning can combine requirements within this cycle.",
    example: "Review purchase needs every 7 days.",
  },
  "Max Qty": {
    code: "maxOrderQty",
    title: "Max Qty / 最大訂購量",
    description: "Maximum recommended order quantity for one replenishment.",
    impact: "Prevents MRP from suggesting too large a single order.",
    example: "Do not order more than 500 PCS at once.",
  },
  "Fixed Qty": {
    code: "fixedOrderQty",
    title: "Fixed Qty / 固定訂購量",
    description: "Fixed quantity used for each replenishment suggestion.",
    impact: "MRP may suggest this amount instead of the exact shortage quantity.",
    example: "Always order 100 PCS.",
  },
  EOQ: {
    code: "economicOrderQty",
    title: "EOQ / 經濟訂購量",
    description: "Economic order quantity balancing order cost and holding cost.",
    impact: "Can be used as the preferred replenishment quantity.",
    example: "Suggested economic lot is 250 PCS.",
  },
  "Multiple Qty": {
    code: "multipleQty",
    title: "Multiple Qty / 倍數",
    description: "Order quantity must be rounded to this multiple.",
    impact: "Useful when supplier sells by carton, roll, pallet, or pack size.",
    example: "Order 24, 48, 72 when carton size is 24.",
  },
  "Reserved Qty": {
    code: "reservedQty",
    title: "Reserved Qty / 預訂量",
    description: "Quantity already reserved for demand, sales orders, or production.",
    impact: "Reduces available-to-promise and available stock.",
    example: "5 PCS reserved for an urgent order.",
  },
  Warehouse: {
    code: "warehousePlanner",
    title: "Warehouse Planner / 庫開員",
    description: "Person responsible for warehouse planning or stock document handling.",
    impact: "Used for responsibility assignment and workflow routing.",
    example: "WH01.",
  },
  Buyer: {
    code: "buyer",
    title: "Buyer / 採購員",
    description: "Purchasing owner responsible for this material.",
    impact: "Purchase suggestions can be assigned or filtered by buyer.",
    example: "PUR01.",
  },
  Planner: {
    code: "productionPlanner",
    title: "Planner / 生管員",
    description: "Production planner responsible for this material.",
    impact: "Production suggestions and shortages can be assigned to this planner.",
    example: "PC01.",
  },
  Subcontract: {
    code: "subcontractPlanner",
    title: "Subcontract Planner / 外包員",
    description: "Owner responsible for subcontract processing.",
    impact: "Used when source type is subcontract.",
    example: "SUB01.",
  },
  Substitute: {
    code: "substituteCode",
    title: "Substitute / 替代代碼",
    description: "Code or group used to identify replacement materials.",
    impact: "Can support shortage handling and alternative material selection.",
    example: "ALT-001.",
  },
  Process: {
    code: "processCode",
    title: "Process / 製程代碼",
    description: "Manufacturing process or routing code related to this item.",
    impact: "Production planning can use it to connect material with routing steps.",
    example: "PROC-001.",
  },
  "Start Dept": {
    code: "startupDepartment",
    title: "Start Dept / 開台部門",
    description: "Department responsible for starting or releasing production.",
    impact: "Helps route work to the correct shop-floor department.",
    example: "DEPT-A.",
  },
};

Object.assign(fieldHelpMap, {
  Source: {
    code: "sourceType",
    title: "Source / 來源別",
    description: "定義這個材料的取得方式，例如自製、市購、外包或調撥。",
    impact: "MRP 會依來源別決定需求要轉成生產建議、採購建議、外包建議或調撥建議。",
    example: "Purchase 表示向供應商採購；In-house 表示廠內自製。",
  },
  "MRP Plan": {
    code: "isPlanned",
    title: "MRP Plan / 計劃否",
    description: "控制這個材料是否參與 MRP 需求計算。",
    impact: "若設定為 no，MRP 不會針對此材料產生採購或生產建議。",
    example: "原料、零件通常設 yes；不需計劃的服務項目可設 no。",
  },
  "Stock Ctrl": {
    code: "isInventoryControlled",
    title: "Stock Ctrl / 庫存管制",
    description: "控制系統是否追蹤這個材料的庫存數量。",
    impact: "庫存管制材料會影響可用量、入庫、出庫與缺料檢查。",
    example: "鋼板、螺絲設 yes；服務費、加工費可設 no。",
  },
  "Virtual Part": {
    code: "isVirtualPart",
    title: "Virtual Part / 虛擬件",
    description: "表示此項目是 BOM 結構中的虛擬組件，通常不實際入庫。",
    impact: "MRP 展開 BOM 時會穿透虛擬件，直接計算下階材料需求。",
    example: "用來整理 BOM 的 phantom assembly。",
  },
  "Order Policy": {
    code: "orderPolicy",
    title: "Order Policy / 訂購政策",
    description: "定義材料的補貨策略。",
    impact: "會影響系統何時產生採購或生產建議，以及建議方式。",
    example: "ROP、週期補貨、逐批補貨、固定量補貨。",
  },
  "Lot Rule": {
    code: "lotRule",
    title: "Lot Rule / 批量法則",
    description: "定義系統計算建議訂購量時如何取批量。",
    impact: "會搭配固定訂購量、倍數、EOQ 等欄位影響 MRP 建議數量。",
    example: "固定批量、倍數批量、經濟批量。",
  },
  "Lead Days": {
    code: "leadTimeDays",
    title: "Lead Days / 前置時間",
    description: "從下單或發出需求到材料可用所需的天數。",
    impact: "MRP 會依此前置時間把建議下單日期往前推。",
    example: "供應商交期 14 天，則填 14。",
  },
  "Mfg Days": {
    code: "manufacturingLeadDays",
    title: "Mfg Days / 製令前置日",
    description: "自製品從開工到完工預估需要的天數。",
    impact: "生產排程會用它推算製令開始與完成日期。",
    example: "組裝需要 3 個工作天，則填 3。",
  },
  "Safety Days": {
    code: "safetyTimeDays",
    title: "Safety Days / 安全時間",
    description: "在需求日前額外預留的緩衝天數。",
    impact: "可降低供應延遲風險，讓系統提早安排供應。",
    example: "供應商常延遲，可額外預留 2 天。",
  },
  "Order Cycle": {
    code: "orderCycleDays",
    title: "Order Cycle / 訂購週期",
    description: "定義多久檢查或彙總一次補貨需求。",
    impact: "週期式計劃會將週期內需求合併成建議單。",
    example: "每 7 天檢查一次採購需求。",
  },
  "Max Qty": {
    code: "maxOrderQty",
    title: "Max Qty / 最大訂購量",
    description: "限制單次建議採購或生產的最大數量。",
    impact: "避免系統一次建議過大的訂購量。",
    example: "單次最多訂購 500 PCS。",
  },
  "Fixed Qty": {
    code: "fixedOrderQty",
    title: "Fixed Qty / 固定訂購量",
    description: "每次補貨固定使用的數量。",
    impact: "MRP 可能以固定量取代實際短缺量作為建議數量。",
    example: "每次固定訂購 100 PCS。",
  },
  EOQ: {
    code: "economicOrderQty",
    title: "EOQ / 經濟訂購量",
    description: "用來平衡訂購成本與庫存持有成本的建議批量。",
    impact: "可作為系統建議補貨數量的參考。",
    example: "經濟批量為 250 PCS。",
  },
  "Multiple Qty": {
    code: "multipleQty",
    title: "Multiple Qty / 倍數",
    description: "訂購數量必須依此倍數取整。",
    impact: "適用於整箱、整捲、整棧板採購。",
    example: "一箱 24 PCS，只能訂 24、48、72。",
  },
  "Reserved Qty": {
    code: "reservedQty",
    title: "Reserved Qty / 預訂量",
    description: "已被銷售、製令或需求保留的數量。",
    impact: "會降低可用庫存與可承諾數量。",
    example: "已有 5 PCS 被急單保留。",
  },
  Warehouse: {
    code: "warehousePlanner",
    title: "Warehouse / 庫開員",
    description: "負責庫存開單或倉庫計劃的人員。",
    impact: "用於責任歸屬、查詢過濾與流程分派。",
    example: "WH01。",
  },
  Buyer: {
    code: "buyer",
    title: "Buyer / 採購員",
    description: "負責此材料採購作業的人員。",
    impact: "採購建議可依採購員分派或查詢。",
    example: "PUR01。",
  },
  Planner: {
    code: "productionPlanner",
    title: "Planner / 生管員",
    description: "負責此材料或自製品生產計劃的人員。",
    impact: "製令建議、缺料和排程可分派給此人員。",
    example: "PC01。",
  },
  Subcontract: {
    code: "subcontractPlanner",
    title: "Subcontract / 外包員",
    description: "負責外包加工或外包採購的人員。",
    impact: "來源別為外包時，系統可依此外包員分派作業。",
    example: "SUB01。",
  },
  Substitute: {
    code: "substituteCode",
    title: "Substitute / 替代代碼",
    description: "用來標示可替代使用的材料或替代群組。",
    impact: "缺料時可作為替代料選擇依據。",
    example: "ALT-001。",
  },
  Process: {
    code: "processCode",
    title: "Process / 製程代碼",
    description: "材料或半成品對應的製程或途程代碼。",
    impact: "生產排程可用它連結製程步驟。",
    example: "PROC-001。",
  },
  "Start Dept": {
    code: "startupDepartment",
    title: "Start Dept / 開台部門",
    description: "負責開工、開台或啟動生產的部門。",
    impact: "可協助製令分派到正確的現場部門。",
    example: "DEPT-A。",
  },
});

const activeFieldKey = ref("MRP Plan");
const activeFieldHelp = computed(() => fieldHelpMap[activeFieldKey.value] || defaultFieldHelp);

const setHelpFromLabelClick = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  const label = target.closest(".el-form-item__label");

  if (!label) {
    return;
  }

  const labelText = label.textContent?.trim() || "";

  if (fieldHelpMap[labelText]) {
    activeFieldKey.value = labelText;
  }
};

const transactionRules = reactive({
  transactionType: [{ required: true, message: "請選擇異動類型", trigger: "change" }],
  quantity: [{ required: true, message: "請輸入數量", trigger: "blur" }],
});

const resetMaterialForm = () => {
  editingMaterialId.value = null;
  activeTab.value = "general";
  Object.assign(materialForm, {
    materialCode: "",
    materialName: "",
    englishName: "",
    specification: "",
    chineseSpec: "",
    englishSpec: "",
    unit: "",
    category: "",
    productLine: "",
    subProductLine: "",
    stockCategory: "",
    stockSubcategory: "",
    stockCustomCategory: "",
    drawingNo: "",
    engineeringChangeNo: "",
    maintainer: "",
    sourceType: "purchase",
    isPlanned: "yes",
    isInventoryControlled: "yes",
    isVirtualPart: "no",
    orderPolicy: "",
    lotRule: "",
    leadTimeDays: 0,
    manufacturingLeadDays: 0,
    safetyTimeDays: 0,
    maxOrderQty: 0,
    fixedOrderQty: 0,
    economicOrderQty: 0,
    orderCycleDays: 0,
    multipleQty: 0,
    reservedQty: 0,
    warehousePlanner: "",
    buyer: "",
    productionPlanner: "",
    subcontractPlanner: "",
    substituteCode: "",
    processCode: "",
    startupDepartment: "",
    safetyStock: 0,
    status: "active",
  });
};

const fetchMaterials = async () => {
  loading.value = true;

  try {
    const res = await apiClient.get<{ data: Material[] }>("/api/materials", {
      params: queryForm,
    });
    materials.value = res.data.data;
  } catch {
    ElMessage.error("材料資料讀取失敗");
  } finally {
    loading.value = false;
  }
};

const openCreateDialog = () => {
  resetMaterialForm();
  materialDialogVisible.value = true;
};

const openEditDialog = (row: Material) => {
  editingMaterialId.value = row.id;
  activeTab.value = "general";
  Object.assign(materialForm, {
    materialCode: row.materialCode,
    materialName: row.materialName,
    englishName: row.englishName || "",
    specification: row.specification || "",
    chineseSpec: row.chineseSpec || "",
    englishSpec: row.englishSpec || "",
    unit: row.unit,
    category: row.category || "",
    productLine: row.productLine || "",
    subProductLine: row.subProductLine || "",
    stockCategory: row.stockCategory || "",
    stockSubcategory: row.stockSubcategory || "",
    stockCustomCategory: row.stockCustomCategory || "",
    drawingNo: row.drawingNo || "",
    engineeringChangeNo: row.engineeringChangeNo || "",
    maintainer: row.maintainer || "",
    sourceType: row.sourceType || "purchase",
    isPlanned: row.isPlanned || "yes",
    isInventoryControlled: row.isInventoryControlled || "yes",
    isVirtualPart: row.isVirtualPart || "no",
    orderPolicy: row.orderPolicy || "",
    lotRule: row.lotRule || "",
    leadTimeDays: Number(row.leadTimeDays || 0),
    manufacturingLeadDays: Number(row.manufacturingLeadDays || 0),
    safetyTimeDays: Number(row.safetyTimeDays || 0),
    maxOrderQty: Number(row.maxOrderQty || 0),
    fixedOrderQty: Number(row.fixedOrderQty || 0),
    economicOrderQty: Number(row.economicOrderQty || 0),
    orderCycleDays: Number(row.orderCycleDays || 0),
    multipleQty: Number(row.multipleQty || 0),
    reservedQty: Number(row.reservedQty || 0),
    warehousePlanner: row.warehousePlanner || "",
    buyer: row.buyer || "",
    productionPlanner: row.productionPlanner || "",
    subcontractPlanner: row.subcontractPlanner || "",
    substituteCode: row.substituteCode || "",
    processCode: row.processCode || "",
    startupDepartment: row.startupDepartment || "",
    safetyStock: Number(row.safetyStock || 0),
    status: row.status,
  });
  materialDialogVisible.value = true;
};

const saveMaterial = async () => {
  if (!materialFormRef.value) {
    return;
  }

  await materialFormRef.value.validate();
  saving.value = true;

  try {
    if (editingMaterialId.value) {
      await apiClient.put(`/api/materials/${editingMaterialId.value}`, materialForm);
      ElMessage.success("材料已更新");
    } else {
      await apiClient.post("/api/materials", materialForm);
      ElMessage.success("材料已新增");
    }

    materialDialogVisible.value = false;
    fetchMaterials();
  } catch (error: any) {
    const message = error?.response?.data?.message || "材料儲存失敗";
    ElMessage.error(message);
  } finally {
    saving.value = false;
  }
};

const toggleStatus = async (row: Material) => {
  const nextStatus = row.status === "active" ? "inactive" : "active";
  const label = nextStatus === "active" ? "啟用" : "停用";

  await ElMessageBox.confirm(`確定要${label}這筆材料嗎？`, "確認", {
    type: "warning",
  });

  await apiClient.patch(`/api/materials/${row.id}/status`, {
    status: nextStatus,
  });

  ElMessage.success(`材料已${label}`);
  fetchMaterials();
};

const openTransactionDialog = (row: Material) => {
  selectedMaterial.value = row;
  transactionForm.transactionType = "in";
  transactionForm.quantity = 0;
  transactionForm.warehouse = "MAIN";
  transactionForm.referenceNo = "";
  transactionForm.remark = "";
  transactionDialogVisible.value = true;
};

const saveTransaction = async () => {
  if (!transactionFormRef.value || !selectedMaterial.value) {
    return;
  }

  await transactionFormRef.value.validate();
  saving.value = true;

  try {
    await apiClient.post("/api/material-transactions", {
      materialId: selectedMaterial.value.id,
      ...transactionForm,
    });
    ElMessage.success("庫存異動已建立");
    transactionDialogVisible.value = false;
    fetchMaterials();
  } catch (error: any) {
    const message = error?.response?.data?.message || "庫存異動失敗";
    ElMessage.error(message);
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  fetchMaterials();
});
</script>

<style scoped>
.material-page {
  min-width: 1060px;
  min-height: calc(100vh - 128px);
  padding: 0;
  background: #cfcfcf;
  color: #222;
  font-family: "Segoe UI", Arial, sans-serif;
}

.erp-title-bar {
  height: 36px;
  padding: 0 10px;
  border: 1px solid #777;
  background: linear-gradient(to bottom, #ebe8f3, #b8aecf);
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: inset 0 1px 0 #fff;
}

.window-title {
  font-size: 18px;
  font-weight: 700;
  color: #3f2c68;
}

.window-subtitle {
  margin-left: 12px;
  color: #4b4b4b;
  font-size: 12px;
}

.window-status {
  font-size: 12px;
  color: #333;
}

.erp-toolbar {
  height: 34px;
  padding: 4px 8px;
  border-left: 1px solid #777;
  border-right: 1px solid #777;
  border-bottom: 1px solid #888;
  background: linear-gradient(to bottom, #f8f8f8, #d6d6d6);
  display: flex;
  align-items: center;
  gap: 6px;
}

.search-card {
  margin: 8px 0;
  border: 1px solid #8f8f8f;
  border-radius: 0;
  background: #dedede;
}

.section-header {
  height: 24px;
  padding: 3px 8px;
  border-bottom: 1px solid #888;
  background: linear-gradient(to bottom, #7f6aa8, #5c477f);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  line-height: 18px;
}

.section-header.compact {
  margin: 0 0 10px;
}

.query-form {
  padding: 10px 10px 0;
}

.record-count {
  height: 32px;
  display: flex;
  align-items: center;
  color: #333;
  font-size: 13px;
  font-weight: 700;
}

.grid-shell {
  border: 1px solid #777;
  background: #fff;
}

.data-table {
  font-size: 13px;
}

.erp-badge {
  display: inline-block;
  min-width: 54px;
  padding: 1px 6px;
  border: 1px solid #777;
  background: #efefef;
  color: #222;
  text-align: center;
  font-size: 12px;
  line-height: 18px;
}

.erp-badge.ok {
  border-color: #3f7d3f;
  background: #dff0d8;
  color: #245724;
}

.erp-badge.muted {
  border-color: #777;
  background: #e5e5e5;
  color: #555;
}

.form-window {
  border: 1px solid #777;
  background: #c9c9c9;
}

.erp-tabs {
  padding: 8px 8px 0;
}

.master-form {
  padding: 0 10px 10px;
}

.form-section {
  margin-top: 8px;
  border: 1px solid #999;
  background: #dedede;
}

.form-body {
  display: block;
}

.form-main {
  min-width: 0;
}

.field-help-panel {
  margin-top: 8px;
  border: 1px solid #777;
  background: #f1f1e6;
  color: #222;
  box-shadow: inset 0 1px 0 #fff;
}

.help-title {
  padding: 5px 8px;
  border-bottom: 1px solid #777;
  background: linear-gradient(to bottom, #e7e7e7, #c9c9c9);
  color: #3f2c68;
  font-weight: 700;
  font-size: 13px;
}

.help-head {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 7px 10px 4px;
}

.help-code {
  color: #666;
  font-family: Consolas, monospace;
  font-size: 12px;
}

.help-name {
  color: #111;
  font-weight: 700;
  font-size: 14px;
}

.help-grid {
  display: grid;
  grid-template-columns: 1.1fr 1.1fr 0.8fr;
  gap: 10px;
  padding: 0 10px 10px;
}

.help-grid div {
  border: 1px solid #c0c0b0;
  background: #fffdf0;
  padding: 6px 8px;
}

.help-grid span {
  display: block;
  margin-bottom: 3px;
  color: #5b477f;
  font-weight: 700;
  font-size: 12px;
}

.help-grid p {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
}

.empty-tab {
  margin-top: 8px;
  min-height: 220px;
  padding: 18px;
  border: 1px solid #999;
  background: #dedede;
  color: #555;
  font-weight: 700;
}

.transaction-form {
  margin-top: 16px;
}

:deep(.el-tabs__header) {
  margin: 0;
}

:deep(.el-tabs__item) {
  height: 28px;
  border-radius: 0 !important;
  font-weight: 700;
}

:deep(.el-card__header) {
  padding: 0;
  border-bottom: 0;
}

:deep(.el-card__body) {
  padding: 0;
}

:deep(.el-form-item) {
  margin-bottom: 10px;
}

:deep(.el-form-item__label) {
  color: #222;
  font-weight: 700;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper),
:deep(.el-textarea__inner),
:deep(.el-input-number .el-input__wrapper) {
  border-radius: 0 !important;
  border: 1px solid #8a8a8a;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.12);
  background: #fff;
}

:deep(.el-button) {
  border-radius: 0;
  min-width: 72px;
  height: 26px;
  padding: 4px 10px;
  font-weight: 700;
}

:deep(.el-button--primary) {
  border-color: #4d387a;
  background: linear-gradient(to bottom, #8d76bd, #5f4796);
}

:deep(.el-table) {
  --el-table-border-color: #999;
  --el-table-row-hover-bg-color: #fff6c9;
  color: #111;
}

:deep(.el-table th) {
  height: 30px;
  background: linear-gradient(to bottom, #78629e, #5b477f) !important;
  color: #fff !important;
  font-weight: 700;
  border-right: 1px solid #8f8f8f;
}

:deep(.el-table td) {
  height: 29px;
  padding: 3px 0;
  border-right: 1px solid #d0d0d0;
}

:deep(.el-table__row:nth-child(even) td) {
  background: #f5f5f5;
}

:deep(.el-table__row.current-row td) {
  background: #dbe8ff !important;
}

:deep(.el-dialog) {
  border-radius: 0;
  border: 1px solid #666;
}

:deep(.el-dialog__header) {
  margin: 0;
  padding: 8px 12px;
  background: linear-gradient(to bottom, #78629e, #5b477f);
}

:deep(.el-dialog__title) {
  color: #fff;
  font-size: 15px;
  font-weight: 700;
}

:deep(.el-dialog__body) {
  padding: 14px 16px;
  background: #dedede;
}

:deep(.el-dialog__footer) {
  padding: 8px 16px 12px;
  background: #d4d4d4;
  border-top: 1px solid #aaa;
}
</style>

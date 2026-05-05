# ERP 物料管理資料欄位文件

本文整理目前系統的資料表欄位、欄位用途，以及材料主檔在 ERP 實務中的應用。資料來源以 `backend/app.py` 的 SQLite schema 與 `src/views/materials/List.vue` 的前端表單為準。

## 資料表總覽

| 資料表 | 中文名稱 | 主要用途 |
| --- | --- | --- |
| `material_master` | 材料主檔 | 定義每一個材料、零件、半成品或成品的基本資料、分類、計劃與庫存控制屬性。 |
| `material_stock` | 材料庫存 | 記錄材料在各倉庫的目前庫存數量。 |
| `material_transaction` | 材料異動紀錄 | 記錄入庫、出庫、庫存調整等庫存異動歷史。 |

## 關聯說明

```text
material_master.id
  ├─ material_stock.material_id
  └─ material_transaction.material_id
```

- `material_master` 是主檔，一筆材料只有一個主檔。
- `material_stock` 是庫存餘額，同一材料可存在不同倉庫。
- `material_transaction` 是異動明細，用來追蹤庫存如何增加、減少或被調整。

## material_master 材料主檔欄位

| DB 欄位 | API/前端欄位 | 型別 | 必填 | 說明 |
| --- | --- | --- | --- | --- |
| `id` | `id` | INTEGER | 系統 | 主鍵，系統自動產生。 |
| `material_code` | `materialCode` | TEXT | 是 | 件號或料號，必須唯一。 |
| `material_name` | `materialName` | TEXT | 是 | 材料中文名稱或主要名稱。 |
| `english_name` | `englishName` | TEXT | 否 | 英文名稱。 |
| `specification` | `specification` | TEXT | 否 | 簡短規格說明。 |
| `chinese_spec` | `chineseSpec` | TEXT | 否 | 中文詳細規格。 |
| `english_spec` | `englishSpec` | TEXT | 否 | 英文詳細規格。 |
| `unit` | `unit` | TEXT | 是 | 計量單位，例如 PCS、KG、M。 |
| `category` | `category` | TEXT | 否 | 原始或一般類別。 |
| `product_line` | `productLine` | TEXT | 否 | 所屬產品線。 |
| `sub_product_line` | `subProductLine` | TEXT | 否 | 所屬次產品線。 |
| `stock_category` | `stockCategory` | TEXT | 否 | 庫存分類。 |
| `stock_subcategory` | `stockSubcategory` | TEXT | 否 | 庫存次分類。 |
| `stock_custom_category` | `stockCustomCategory` | TEXT | 否 | 自訂庫存分類。 |
| `drawing_no` | `drawingNo` | TEXT | 否 | 工程圖號。 |
| `engineering_change_no` | `engineeringChangeNo` | TEXT | 否 | 工程變更或設變編號。 |
| `maintainer` | `maintainer` | TEXT | 否 | 主檔維護人員。 |
| `source_type` | `sourceType` | TEXT | 否 | 來源別，例如 purchase、in_house、subcontract、transfer。 |
| `is_planned` | `isPlanned` | TEXT | 否 | 是否納入 MRP 計劃，yes/no。 |
| `is_inventory_controlled` | `isInventoryControlled` | TEXT | 否 | 是否做庫存管制，yes/no。 |
| `is_virtual_part` | `isVirtualPart` | TEXT | 否 | 是否為虛擬料件，yes/no。 |
| `order_policy` | `orderPolicy` | TEXT | 否 | 訂購政策。 |
| `lot_rule` | `lotRule` | TEXT | 否 | 批量法則。 |
| `lead_time_days` | `leadTimeDays` | REAL | 否 | 採購或供應前置天數。 |
| `manufacturing_lead_days` | `manufacturingLeadDays` | REAL | 否 | 自製或生產前置天數。 |
| `safety_time_days` | `safetyTimeDays` | REAL | 否 | 安全時間。 |
| `max_order_qty` | `maxOrderQty` | REAL | 否 | 最大訂購量。 |
| `fixed_order_qty` | `fixedOrderQty` | REAL | 否 | 固定訂購量。 |
| `economic_order_qty` | `economicOrderQty` | REAL | 否 | 經濟訂購量 EOQ。 |
| `order_cycle_days` | `orderCycleDays` | REAL | 否 | 訂購週期天數。 |
| `multiple_qty` | `multipleQty` | REAL | 否 | 訂購倍數。 |
| `reserved_qty` | `reservedQty` | REAL | 否 | 預留數量。 |
| `warehouse_planner` | `warehousePlanner` | TEXT | 否 | 倉管或庫存計劃負責人。 |
| `buyer` | `buyer` | TEXT | 否 | 採購負責人。 |
| `production_planner` | `productionPlanner` | TEXT | 否 | 生產計劃負責人。 |
| `subcontract_planner` | `subcontractPlanner` | TEXT | 否 | 外包或委外負責人。 |
| `substitute_code` | `substituteCode` | TEXT | 否 | 替代料號或替代群組。 |
| `process_code` | `processCode` | TEXT | 否 | 製程代碼。 |
| `startup_department` | `startupDepartment` | TEXT | 否 | 開工或啟動部門。 |
| `safety_stock` | `safetyStock` | REAL | 否 | 安全庫存量，預設 0。 |
| `status` | `status` | TEXT | 是 | 狀態，active 或 inactive。 |
| `created_by` | `createdBy` | TEXT | 系統 | 建立人員。 |
| `created_at` | `createdAt` | TEXT | 系統 | 建立時間。 |
| `updated_at` | `updatedAt` | TEXT | 系統 | 更新時間。 |
| 無 | `currentStock` | 衍生欄位 | 系統 | 由 `material_stock.quantity` 加總而來，不直接存在 `material_master`。 |

## material_stock 材料庫存欄位

| DB 欄位 | API/前端欄位 | 型別 | 必填 | 說明 |
| --- | --- | --- | --- | --- |
| `id` | `id` | INTEGER | 系統 | 主鍵，系統自動產生。 |
| `material_id` | `materialId` | INTEGER | 是 | 對應 `material_master.id`。 |
| `warehouse` | `warehouse` | TEXT | 是 | 倉庫代碼，預設 MAIN。 |
| `quantity` | `quantity` | REAL | 是 | 目前庫存量。 |
| `updated_at` | `updatedAt` | TEXT | 系統 | 最後更新時間。 |

實務上 `material_stock` 通常是「庫存餘額表」。它回答的是「某材料現在在某倉庫有多少」，不是「為什麼變成這個數量」。

## material_transaction 材料異動欄位

| DB 欄位 | API/前端欄位 | 型別 | 必填 | 說明 |
| --- | --- | --- | --- | --- |
| `id` | `id` | INTEGER | 系統 | 主鍵，系統自動產生。 |
| `material_id` | `materialId` | INTEGER | 是 | 對應 `material_master.id`。 |
| `transaction_type` | `transactionType` | TEXT | 是 | 異動類型：in、out、adjust。 |
| `quantity` | `quantity` | REAL | 是 | 異動數量。入庫為正數，出庫會記為負數，調整為差異量。 |
| `warehouse` | `warehouse` | TEXT | 是 | 異動倉庫，預設 MAIN。 |
| `reference_no` | `referenceNo` | TEXT | 否 | 參考單號，例如採購單、領料單、盤點單。 |
| `remark` | `remark` | TEXT | 否 | 備註。 |
| `created_by` | `createdBy` | TEXT | 系統 | 建立異動的人員。 |
| `created_at` | `createdAt` | TEXT | 系統 | 異動建立時間。 |

實務上 `material_transaction` 是「庫存流水帳」。它回答的是「庫存為什麼增加或減少」，是庫存稽核與追溯的依據。

## 材料主檔欄位實務應用

### 基本識別欄位

| 欄位 | 說明與應用 | 實務注意事項 |
| --- | --- | --- |
| `materialCode` 件號 | ERP 中識別材料的唯一代碼，是採購、庫存、BOM、製令與成本計算的共同鍵。 | 編碼規則應穩定，不建議把容易變動的資訊放進料號。 |
| `materialName` 名稱 | 讓使用者快速辨識材料內容，常出現在查詢、單據與報表。 | 名稱要簡潔，詳細規格應放在規格欄位。 |
| `englishName` 英文名稱 | 用於海外供應商、出口文件、多語系報表或跨國 ERP 流程。 | 若公司沒有外語流程，可以先非必填。 |
| `specification` 規格說明 | 記錄尺寸、材質、型號、版本等簡短規格。 | 應避免只靠名稱描述規格，否則採購與倉庫容易拿錯料。 |
| `chineseSpec` 中文詳細規格 | 保存較完整的中文技術描述。 | 適合放檢驗條件、尺寸範圍、包裝要求。 |
| `englishSpec` 英文詳細規格 | 保存英文規格，常用於國外採購或客戶文件。 | 若與中文規格不同步，需建立維護責任。 |

### 分類與庫存欄位

| 欄位 | 說明與應用 | 實務注意事項 |
| --- | --- | --- |
| `unit` 計量單位 | 庫存、採購、領料與異動都依此單位計算。 | 單位一旦有庫存交易就不應隨意改動，否則歷史數量會失真。 |
| `category` 原類別 | 一般分類，可用於舊系統或簡單查詢。 | 若已有庫存分類，應明確區分兩者用途。 |
| `productLine` 產品線 | 用於分析材料屬於哪個產品系列。 | 常用於成本分析、庫存分析與權責歸屬。 |
| `subProductLine` 次產品線 | 產品線下的更細分類。 | 分類層級不宜太多，否則維護成本會變高。 |
| `stockCategory` 庫存分類 | 以庫存管理角度分類，例如原料、半成品、成品、耗材。 | 會影響庫存報表、盤點範圍與倉庫管理策略。 |
| `stockSubcategory` 庫存次分類 | 庫存分類下的細項。 | 適合用於 ABC 分析或細分物料族群。 |
| `stockCustomCategory` 自訂分類 | 保留給公司自訂管理需求。 | 建議先定義清楚代碼表，避免自由輸入造成資料混亂。 |
| `safetyStock` 安全庫存 | 為了避免缺料而保留的最低庫存量。 | 太低會缺料，太高會佔庫存資金，需要依需求波動與交期調整。 |
| `reservedQty` 預留數量 | 已被訂單、製令或特殊需求保留的數量。 | 實務上會影響可用庫存，不等於實體庫存減少。 |
| `currentStock` 目前庫存 | 系統由庫存餘額加總顯示，方便快速查看現有量。 | 這是衍生欄位，不應手動寫入材料主檔。 |

### 計劃與 MRP 欄位

| 欄位 | 說明與應用 | 實務注意事項 |
| --- | --- | --- |
| `sourceType` 來源別 | 決定材料需求要走採購、自製、委外或轉撥。 | MRP 會依來源別產生不同類型的建議單。 |
| `isPlanned` MRP 計劃否 | 控制材料是否參與物料需求計劃。 | 常備料、原料、半成品通常為 yes；服務費或非庫存項目可為 no。 |
| `isInventoryControlled` 庫存管制否 | 決定此材料是否需要管理庫存數量。 | 不管庫存的項目通常不應做入出庫管控。 |
| `isVirtualPart` 虛擬料件 | 用於 BOM 群組或製程中不實際入庫的料件。 | 虛擬料通常不應有實體庫存。 |
| `orderPolicy` 訂購政策 | 定義補貨邏輯，例如按需求、定期補貨、再訂購點。 | 不同材料可有不同補貨策略，不能全公司一套規則硬套。 |
| `lotRule` 批量法則 | 定義建議採購或生產數量如何取批量。 | 常與固定量、EOQ、倍數欄位一起使用。 |
| `leadTimeDays` 採購前置天數 | 從下單到材料可用的預估天數。 | MRP 會用它倒推建議下單日期。 |
| `manufacturingLeadDays` 製造前置天數 | 自製品從開工到完成所需時間。 | 對生產排程與製令開工日很重要。 |
| `safetyTimeDays` 安全時間 | 在需求日前額外預留的時間緩衝。 | 用於降低供應延遲風險，但太高會讓物料過早到貨。 |
| `orderCycleDays` 訂購週期 | 多久彙整或檢查一次補貨需求。 | 適合週期性採購，例如每週或每月集中下單。 |
| `maxOrderQty` 最大訂購量 | 限制單次採購或生產建議上限。 | 可避免一次下單太多造成庫存壓力。 |
| `fixedOrderQty` 固定訂購量 | 每次補貨固定使用的數量。 | 適用供應商 MOQ 或固定包裝量。 |
| `economicOrderQty` EOQ | 經濟訂購量，用於平衡訂購成本與持有成本。 | 是建議值，不一定每次都必須照做。 |
| `multipleQty` 訂購倍數 | 訂購量必須依倍數取整。 | 例如一箱 24 PCS，只能訂 24、48、72。 |

### 權責與流程欄位

| 欄位 | 說明與應用 | 實務注意事項 |
| --- | --- | --- |
| `warehousePlanner` 倉管或庫存計劃員 | 負責庫存、倉庫或補貨協調的人員。 | 可用於報表分派與責任追蹤。 |
| `buyer` 採購員 | 負責此材料採購作業的人員。 | 採購建議、缺料通知可依此分派。 |
| `productionPlanner` 生管員 | 負責自製品或半成品的生產計劃人員。 | 影響製令建議與排程責任歸屬。 |
| `subcontractPlanner` 委外負責人 | 負責委外加工或外包採購的人員。 | 來源別為 subcontract 時特別重要。 |
| `startupDepartment` 開工部門 | 負責啟動或執行生產的部門。 | 可用於製令派工或跨部門協作。 |

### 工程與替代欄位

| 欄位 | 說明與應用 | 實務注意事項 |
| --- | --- | --- |
| `drawingNo` 工程圖號 | 對應工程圖、設計圖或規格文件。 | 採購、品保與製造應使用同一版圖面。 |
| `engineeringChangeNo` 設變編號 | 記錄材料經過哪個工程變更。 | 可追蹤新舊版本切換與客訴問題。 |
| `substituteCode` 替代料號 | 標示可替代使用的料號或替代群組。 | 替代料需確認規格、品質與客戶承認條件。 |
| `processCode` 製程代碼 | 對應材料或半成品的製程路線。 | 可與工藝路線、工作中心、製令排程連動。 |
| `maintainer` 維護人員 | 負責維護這筆材料主檔的人。 | 實務上主檔資料要有 owner，否則資料品質會下降。 |

### 狀態與稽核欄位

| 欄位 | 說明與應用 | 實務注意事項 |
| --- | --- | --- |
| `status` 狀態 | `active` 表示可使用，`inactive` 表示停用。 | 停用通常代表不再採購、生產或異動，但歷史資料仍保留。 |
| `createdBy` 建立人員 | 記錄誰建立此材料。 | 用於資料稽核。 |
| `createdAt` 建立時間 | 記錄建立時間。 | 可追蹤材料導入時間。 |
| `updatedAt` 更新時間 | 記錄最後修改時間。 | 可判斷主檔是否長期未維護。 |

## 建議的資料維護原則

- 料號、名稱、單位是主檔品質的核心，建立前應先確認是否已有相同或相似料號。
- 單位與來源別一旦有交易或計劃資料，就不應隨意修改。
- 安全庫存、前置天數、訂購批量會直接影響缺料與庫存金額，應定期檢討。
- 採購員、生管員、倉管等責任欄位應維護完整，後續才能做工作分派與例外追蹤。
- 工程圖號與設變編號對品質追溯很重要，特別是製造業或有版本控管的材料。
- 停用材料不要刪除，應保留歷史資料並透過 `status` 控制是否可再使用。

## ERP 學習重點

材料主檔不是單純的「材料清單」，它是 ERP 中很多模組共用的基礎資料：

- 採購模組用它判斷供應來源、採購員、訂購量與交期。
- 庫存模組用它判斷單位、分類、安全庫存與庫存管制。
- 生產模組用它判斷是否自製、製造前置時間、製程與生管負責人。
- MRP 用它把需求轉成採購建議、製令建議或委外建議。
- 成本與報表用它做分類彙總、產品線分析與庫存價值分析。

因此材料主檔的資料品質會直接影響 ERP 後續流程的準確度。

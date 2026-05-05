from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sqlite3
import base64
import hashlib
import hmac
import json
import time
from datetime import datetime


def load_env_file(path=".env"):
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()

app = Flask(__name__)
CORS(app)

DB_NAME = os.getenv("DB_NAME", "gateflow.db")

API_USERNAME = os.getenv("API_USERNAME", "")
API_PASSWORD = os.getenv("API_PASSWORD", "")
AUTH_SECRET = os.getenv("AUTH_SECRET", "change-this-dev-secret")
TOKEN_EXPIRES_SECONDS = int(os.getenv("TOKEN_EXPIRES_SECONDS", "28800"))



def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS material_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_code TEXT NOT NULL UNIQUE,
            material_name TEXT NOT NULL,
            english_name TEXT,
            specification TEXT,
            chinese_spec TEXT,
            english_spec TEXT,
            unit TEXT NOT NULL,
            category TEXT,
            product_line TEXT,
            sub_product_line TEXT,
            stock_category TEXT,
            stock_subcategory TEXT,
            stock_custom_category TEXT,
            drawing_no TEXT,
            engineering_change_no TEXT,
            maintainer TEXT,
            source_type TEXT,
            is_planned TEXT,
            is_inventory_controlled TEXT,
            is_virtual_part TEXT,
            order_policy TEXT,
            lot_rule TEXT,
            lead_time_days REAL DEFAULT 0,
            manufacturing_lead_days REAL DEFAULT 0,
            safety_time_days REAL DEFAULT 0,
            max_order_qty REAL DEFAULT 0,
            fixed_order_qty REAL DEFAULT 0,
            economic_order_qty REAL DEFAULT 0,
            order_cycle_days REAL DEFAULT 0,
            multiple_qty REAL DEFAULT 0,
            reserved_qty REAL DEFAULT 0,
            warehouse_planner TEXT,
            buyer TEXT,
            production_planner TEXT,
            subcontract_planner TEXT,
            substitute_code TEXT,
            process_code TEXT,
            startup_department TEXT,
            safety_stock REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'active',
            created_by TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS material_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_id INTEGER NOT NULL,
            warehouse TEXT NOT NULL DEFAULT 'MAIN',
            quantity REAL NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL,
            UNIQUE(material_id, warehouse),
            FOREIGN KEY(material_id) REFERENCES material_master(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS material_transaction (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            quantity REAL NOT NULL,
            warehouse TEXT NOT NULL DEFAULT 'MAIN',
            reference_no TEXT,
            remark TEXT,
            created_by TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(material_id) REFERENCES material_master(id)
        )
    """)
    existing_columns = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(material_master)").fetchall()
    }
    column_defs = {
        "english_name": "TEXT",
        "chinese_spec": "TEXT",
        "english_spec": "TEXT",
        "product_line": "TEXT",
        "sub_product_line": "TEXT",
        "stock_category": "TEXT",
        "stock_subcategory": "TEXT",
        "stock_custom_category": "TEXT",
        "drawing_no": "TEXT",
        "engineering_change_no": "TEXT",
        "maintainer": "TEXT",
        "source_type": "TEXT",
        "is_planned": "TEXT",
        "is_inventory_controlled": "TEXT",
        "is_virtual_part": "TEXT",
        "order_policy": "TEXT",
        "lot_rule": "TEXT",
        "lead_time_days": "REAL DEFAULT 0",
        "manufacturing_lead_days": "REAL DEFAULT 0",
        "safety_time_days": "REAL DEFAULT 0",
        "max_order_qty": "REAL DEFAULT 0",
        "fixed_order_qty": "REAL DEFAULT 0",
        "economic_order_qty": "REAL DEFAULT 0",
        "order_cycle_days": "REAL DEFAULT 0",
        "multiple_qty": "REAL DEFAULT 0",
        "reserved_qty": "REAL DEFAULT 0",
        "warehouse_planner": "TEXT",
        "buyer": "TEXT",
        "production_planner": "TEXT",
        "subcontract_planner": "TEXT",
        "substitute_code": "TEXT",
        "process_code": "TEXT",
        "startup_department": "TEXT",
    }

    for column_name, column_type in column_defs.items():
        if column_name not in existing_columns:
            conn.execute(f"ALTER TABLE material_master ADD COLUMN {column_name} {column_type}")

    conn.commit()
    conn.close()


init_db()

def base64url_encode(value):
    return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")

def base64url_decode(value):
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)

def sign_payload(payload):
    message = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = hmac.new(AUTH_SECRET.encode("utf-8"), message, hashlib.sha256).digest()
    return f"{base64url_encode(message)}.{base64url_encode(signature)}"

def verify_token(token):
    try:
        payload_part, signature_part = token.split(".", 1)
        payload_bytes = base64url_decode(payload_part)
        expected_signature = hmac.new(
            AUTH_SECRET.encode("utf-8"),
            payload_bytes,
            hashlib.sha256
        ).digest()

        if not hmac.compare_digest(base64url_decode(signature_part), expected_signature):
            return None

        payload = json.loads(payload_bytes.decode("utf-8"))

        if payload.get("exp", 0) < int(time.time()):
            return None

        return payload
    except Exception:
        return None

def create_access_token(username):
    now = int(time.time())
    payload = {
        "sub": username,
        "role": "admin",
        "iat": now,
        "exp": now + TOKEN_EXPIRES_SECONDS
    }

    return sign_payload(payload), payload

def current_user_from_bearer_token():
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.replace("Bearer ", "", 1).strip()
    return verify_token(token)

def require_auth():
    user = current_user_from_bearer_token()

    if user is None:
        return None, error_response(
            401,
            "UNAUTHORIZED",
            "Missing, invalid, or expired access token."
        )

    return user, None

def error_response(http_status, error_code, message):
    return jsonify({
        "status": "error",
        "error_code": error_code,
        "message": message
    }), http_status

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def material_row_to_dict(row):
    item = dict(row)
    field_map = {
        "safety_stock": "safetyStock",
        "material_code": "materialCode",
        "material_name": "materialName",
        "english_name": "englishName",
        "chinese_spec": "chineseSpec",
        "english_spec": "englishSpec",
        "product_line": "productLine",
        "sub_product_line": "subProductLine",
        "stock_category": "stockCategory",
        "stock_subcategory": "stockSubcategory",
        "stock_custom_category": "stockCustomCategory",
        "drawing_no": "drawingNo",
        "engineering_change_no": "engineeringChangeNo",
        "source_type": "sourceType",
        "is_planned": "isPlanned",
        "is_inventory_controlled": "isInventoryControlled",
        "is_virtual_part": "isVirtualPart",
        "order_policy": "orderPolicy",
        "lot_rule": "lotRule",
        "lead_time_days": "leadTimeDays",
        "manufacturing_lead_days": "manufacturingLeadDays",
        "safety_time_days": "safetyTimeDays",
        "max_order_qty": "maxOrderQty",
        "fixed_order_qty": "fixedOrderQty",
        "economic_order_qty": "economicOrderQty",
        "order_cycle_days": "orderCycleDays",
        "multiple_qty": "multipleQty",
        "reserved_qty": "reservedQty",
        "warehouse_planner": "warehousePlanner",
        "production_planner": "productionPlanner",
        "subcontract_planner": "subcontractPlanner",
        "substitute_code": "substituteCode",
        "process_code": "processCode",
        "startup_department": "startupDepartment",
        "created_at": "createdAt",
        "updated_at": "updatedAt",
        "current_stock": "currentStock",
    }

    for db_key, api_key in field_map.items():
        if db_key in item:
            item[api_key] = item.pop(db_key)

    return item

def parse_non_negative_number(data, field_name):
    try:
        value = float(data.get(field_name, 0) or 0)
    except Exception:
        raise ValueError(f"{field_name} must be a number.")

    if value < 0:
        raise ValueError(f"{field_name} cannot be negative.")

    return value

def require_material_payload(data, is_update=False):
    if not data:
        raise ValueError("Request body must be valid JSON.")

    required_fields = ["materialCode", "materialName", "unit"]

    if not is_update:
        for field in required_fields:
            if not str(data.get(field, "")).strip():
                raise ValueError(f"{field} is required.")

    safety_stock = parse_non_negative_number(data, "safetyStock")

    status = data.get("status", "active")
    if status not in ("active", "inactive"):
        raise ValueError("status must be active or inactive.")

    return {
        "material_code": str(data.get("materialCode", "")).strip(),
        "material_name": str(data.get("materialName", "")).strip(),
        "english_name": str(data.get("englishName", "")).strip(),
        "specification": str(data.get("specification", "")).strip(),
        "chinese_spec": str(data.get("chineseSpec", "")).strip(),
        "english_spec": str(data.get("englishSpec", "")).strip(),
        "unit": str(data.get("unit", "")).strip(),
        "category": str(data.get("category", "")).strip(),
        "product_line": str(data.get("productLine", "")).strip(),
        "sub_product_line": str(data.get("subProductLine", "")).strip(),
        "stock_category": str(data.get("stockCategory", "")).strip(),
        "stock_subcategory": str(data.get("stockSubcategory", "")).strip(),
        "stock_custom_category": str(data.get("stockCustomCategory", "")).strip(),
        "drawing_no": str(data.get("drawingNo", "")).strip(),
        "engineering_change_no": str(data.get("engineeringChangeNo", "")).strip(),
        "maintainer": str(data.get("maintainer", "")).strip(),
        "source_type": str(data.get("sourceType", "")).strip(),
        "is_planned": str(data.get("isPlanned", "yes")).strip(),
        "is_inventory_controlled": str(data.get("isInventoryControlled", "yes")).strip(),
        "is_virtual_part": str(data.get("isVirtualPart", "no")).strip(),
        "order_policy": str(data.get("orderPolicy", "")).strip(),
        "lot_rule": str(data.get("lotRule", "")).strip(),
        "lead_time_days": parse_non_negative_number(data, "leadTimeDays"),
        "manufacturing_lead_days": parse_non_negative_number(data, "manufacturingLeadDays"),
        "safety_time_days": parse_non_negative_number(data, "safetyTimeDays"),
        "max_order_qty": parse_non_negative_number(data, "maxOrderQty"),
        "fixed_order_qty": parse_non_negative_number(data, "fixedOrderQty"),
        "economic_order_qty": parse_non_negative_number(data, "economicOrderQty"),
        "order_cycle_days": parse_non_negative_number(data, "orderCycleDays"),
        "multiple_qty": parse_non_negative_number(data, "multipleQty"),
        "reserved_qty": parse_non_negative_number(data, "reservedQty"),
        "warehouse_planner": str(data.get("warehousePlanner", "")).strip(),
        "buyer": str(data.get("buyer", "")).strip(),
        "production_planner": str(data.get("productionPlanner", "")).strip(),
        "subcontract_planner": str(data.get("subcontractPlanner", "")).strip(),
        "substitute_code": str(data.get("substituteCode", "")).strip(),
        "process_code": str(data.get("processCode", "")).strip(),
        "startup_department": str(data.get("startupDepartment", "")).strip(),
        "safety_stock": safety_stock,
        "status": status
    }

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not data:
        return error_response(
            400,
            "INVALID_PAYLOAD",
            "Request body must be valid JSON."
        )

    username = data.get("username", "")
    password = data.get("password", "")

    if username != API_USERNAME or password != API_PASSWORD:
        return error_response(
            401,
            "INVALID_CREDENTIALS",
            "Wrong username or password."
        )

    token, payload = create_access_token(username)

    return jsonify({
        "status": "success",
        "token": token,
        "expiresAt": payload["exp"],
        "user": {
            "username": username,
            "role": payload["role"]
        }
    })

@app.route("/api/auth/me", methods=["GET"])
def me():
    user, auth_error = require_auth()
    if auth_error:
        return auth_error

    return jsonify({
        "status": "success",
        "user": {
            "username": user["sub"],
            "role": user["role"]
        },
        "expiresAt": user["exp"]
    })

@app.route("/api/materials", methods=["GET"])
def list_materials():
    user, auth_error = require_auth()
    if auth_error:
        return auth_error

    keyword = request.args.get("keyword", "").strip()
    status = request.args.get("status", "").strip()
    category = request.args.get("category", "").strip()

    sql = """
        SELECT
            m.id,
            m.material_code,
            m.material_name,
            m.english_name,
            m.specification,
            m.chinese_spec,
            m.english_spec,
            m.unit,
            m.category,
            m.product_line,
            m.sub_product_line,
            m.stock_category,
            m.stock_subcategory,
            m.stock_custom_category,
            m.drawing_no,
            m.engineering_change_no,
            m.maintainer,
            m.source_type,
            m.is_planned,
            m.is_inventory_controlled,
            m.is_virtual_part,
            m.order_policy,
            m.lot_rule,
            m.lead_time_days,
            m.manufacturing_lead_days,
            m.safety_time_days,
            m.max_order_qty,
            m.fixed_order_qty,
            m.economic_order_qty,
            m.order_cycle_days,
            m.multiple_qty,
            m.reserved_qty,
            m.warehouse_planner,
            m.buyer,
            m.production_planner,
            m.subcontract_planner,
            m.substitute_code,
            m.process_code,
            m.startup_department,
            m.safety_stock,
            m.status,
            m.created_at,
            m.updated_at,
            COALESCE(SUM(s.quantity), 0) AS current_stock
        FROM material_master m
        LEFT JOIN material_stock s ON s.material_id = m.id
        WHERE 1 = 1
    """
    params = []

    if keyword:
        sql += """ AND (
            m.material_code LIKE ?
            OR m.material_name LIKE ?
            OR m.english_name LIKE ?
            OR m.specification LIKE ?
            OR m.chinese_spec LIKE ?
            OR m.english_spec LIKE ?
            OR m.drawing_no LIKE ?
        )"""
        like_keyword = f"%{keyword}%"
        params.extend([
            like_keyword,
            like_keyword,
            like_keyword,
            like_keyword,
            like_keyword,
            like_keyword,
            like_keyword,
        ])

    if status:
        sql += " AND m.status = ?"
        params.append(status)

    if category:
        sql += " AND m.category = ?"
        params.append(category)

    sql += """
        GROUP BY m.id
        ORDER BY m.material_code ASC
    """

    conn = get_conn()
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    return jsonify({
        "success": True,
        "data": [material_row_to_dict(row) for row in rows]
    })

@app.route("/api/materials", methods=["POST"])
def create_material():
    user, auth_error = require_auth()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True)

    try:
        material = require_material_payload(data)
    except ValueError as e:
        return error_response(400, "INVALID_PAYLOAD", str(e))

    timestamp = now_text()
    conn = get_conn()

    try:
        cursor = conn.execute("""
            INSERT INTO material_master (
                material_code,
                material_name,
                english_name,
                specification,
                chinese_spec,
                english_spec,
                unit,
                category,
                product_line,
                sub_product_line,
                stock_category,
                stock_subcategory,
                stock_custom_category,
                drawing_no,
                engineering_change_no,
                maintainer,
                source_type,
                is_planned,
                is_inventory_controlled,
                is_virtual_part,
                order_policy,
                lot_rule,
                lead_time_days,
                manufacturing_lead_days,
                safety_time_days,
                max_order_qty,
                fixed_order_qty,
                economic_order_qty,
                order_cycle_days,
                multiple_qty,
                reserved_qty,
                warehouse_planner,
                buyer,
                production_planner,
                subcontract_planner,
                substitute_code,
                process_code,
                startup_department,
                safety_stock,
                status,
                created_by,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            material["material_code"],
            material["material_name"],
            material["english_name"],
            material["specification"],
            material["chinese_spec"],
            material["english_spec"],
            material["unit"],
            material["category"],
            material["product_line"],
            material["sub_product_line"],
            material["stock_category"],
            material["stock_subcategory"],
            material["stock_custom_category"],
            material["drawing_no"],
            material["engineering_change_no"],
            material["maintainer"] or user["sub"],
            material["source_type"],
            material["is_planned"],
            material["is_inventory_controlled"],
            material["is_virtual_part"],
            material["order_policy"],
            material["lot_rule"],
            material["lead_time_days"],
            material["manufacturing_lead_days"],
            material["safety_time_days"],
            material["max_order_qty"],
            material["fixed_order_qty"],
            material["economic_order_qty"],
            material["order_cycle_days"],
            material["multiple_qty"],
            material["reserved_qty"],
            material["warehouse_planner"],
            material["buyer"],
            material["production_planner"],
            material["subcontract_planner"],
            material["substitute_code"],
            material["process_code"],
            material["startup_department"],
            material["safety_stock"],
            material["status"],
            user["sub"],
            timestamp,
            timestamp
        ))
        material_id = cursor.lastrowid
        conn.execute("""
            INSERT INTO material_stock (material_id, warehouse, quantity, updated_at)
            VALUES (?, ?, ?, ?)
        """, (material_id, "MAIN", 0, timestamp))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        conn.close()
        return error_response(409, "DUPLICATE_MATERIAL", "materialCode already exists.")
    except Exception as e:
        conn.rollback()
        conn.close()
        return error_response(500, "INTERNAL_ERROR", str(e))

    row = conn.execute("""
        SELECT
            m.id,
            m.material_code,
            m.material_name,
            m.english_name,
            m.specification,
            m.chinese_spec,
            m.english_spec,
            m.unit,
            m.category,
            m.product_line,
            m.sub_product_line,
            m.stock_category,
            m.stock_subcategory,
            m.stock_custom_category,
            m.drawing_no,
            m.engineering_change_no,
            m.maintainer,
            m.source_type,
            m.is_planned,
            m.is_inventory_controlled,
            m.is_virtual_part,
            m.order_policy,
            m.lot_rule,
            m.lead_time_days,
            m.manufacturing_lead_days,
            m.safety_time_days,
            m.max_order_qty,
            m.fixed_order_qty,
            m.economic_order_qty,
            m.order_cycle_days,
            m.multiple_qty,
            m.reserved_qty,
            m.warehouse_planner,
            m.buyer,
            m.production_planner,
            m.subcontract_planner,
            m.substitute_code,
            m.process_code,
            m.startup_department,
            m.safety_stock,
            m.status,
            m.created_at,
            m.updated_at,
            COALESCE(SUM(s.quantity), 0) AS current_stock
        FROM material_master m
        LEFT JOIN material_stock s ON s.material_id = m.id
        WHERE m.id = ?
        GROUP BY m.id
    """, (material_id,)).fetchone()
    conn.close()

    return jsonify({
        "status": "success",
        "data": material_row_to_dict(row)
    }), 201

@app.route("/api/materials/<int:material_id>", methods=["PUT"])
def update_material(material_id):
    user, auth_error = require_auth()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True)

    try:
        material = require_material_payload(data)
    except ValueError as e:
        return error_response(400, "INVALID_PAYLOAD", str(e))

    timestamp = now_text()
    conn = get_conn()

    existing = conn.execute("""
        SELECT id FROM material_master WHERE id = ?
    """, (material_id,)).fetchone()

    if existing is None:
        conn.close()
        return error_response(404, "MATERIAL_NOT_FOUND", "Material not found.")

    try:
        conn.execute("""
            UPDATE material_master
            SET
                material_code = ?,
                material_name = ?,
                english_name = ?,
                specification = ?,
                chinese_spec = ?,
                english_spec = ?,
                unit = ?,
                category = ?,
                product_line = ?,
                sub_product_line = ?,
                stock_category = ?,
                stock_subcategory = ?,
                stock_custom_category = ?,
                drawing_no = ?,
                engineering_change_no = ?,
                maintainer = ?,
                source_type = ?,
                is_planned = ?,
                is_inventory_controlled = ?,
                is_virtual_part = ?,
                order_policy = ?,
                lot_rule = ?,
                lead_time_days = ?,
                manufacturing_lead_days = ?,
                safety_time_days = ?,
                max_order_qty = ?,
                fixed_order_qty = ?,
                economic_order_qty = ?,
                order_cycle_days = ?,
                multiple_qty = ?,
                reserved_qty = ?,
                warehouse_planner = ?,
                buyer = ?,
                production_planner = ?,
                subcontract_planner = ?,
                substitute_code = ?,
                process_code = ?,
                startup_department = ?,
                safety_stock = ?,
                status = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            material["material_code"],
            material["material_name"],
            material["english_name"],
            material["specification"],
            material["chinese_spec"],
            material["english_spec"],
            material["unit"],
            material["category"],
            material["product_line"],
            material["sub_product_line"],
            material["stock_category"],
            material["stock_subcategory"],
            material["stock_custom_category"],
            material["drawing_no"],
            material["engineering_change_no"],
            material["maintainer"] or user["sub"],
            material["source_type"],
            material["is_planned"],
            material["is_inventory_controlled"],
            material["is_virtual_part"],
            material["order_policy"],
            material["lot_rule"],
            material["lead_time_days"],
            material["manufacturing_lead_days"],
            material["safety_time_days"],
            material["max_order_qty"],
            material["fixed_order_qty"],
            material["economic_order_qty"],
            material["order_cycle_days"],
            material["multiple_qty"],
            material["reserved_qty"],
            material["warehouse_planner"],
            material["buyer"],
            material["production_planner"],
            material["subcontract_planner"],
            material["substitute_code"],
            material["process_code"],
            material["startup_department"],
            material["safety_stock"],
            material["status"],
            timestamp,
            material_id
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        conn.close()
        return error_response(409, "DUPLICATE_MATERIAL", "materialCode already exists.")
    except Exception as e:
        conn.rollback()
        conn.close()
        return error_response(500, "INTERNAL_ERROR", str(e))

    conn.close()

    return jsonify({
        "status": "success",
        "message": "Material updated successfully."
    })

@app.route("/api/materials/<int:material_id>/status", methods=["PATCH"])
def update_material_status(material_id):
    user, auth_error = require_auth()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}
    status = data.get("status", "")

    if status not in ("active", "inactive"):
        return error_response(400, "INVALID_PAYLOAD", "status must be active or inactive.")

    conn = get_conn()
    cursor = conn.execute("""
        UPDATE material_master
        SET status = ?, updated_at = ?
        WHERE id = ?
    """, (status, now_text(), material_id))
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return error_response(404, "MATERIAL_NOT_FOUND", "Material not found.")

    return jsonify({
        "status": "success",
        "message": "Material status updated successfully."
    })

@app.route("/api/material-transactions", methods=["GET"])
def list_material_transactions():
    user, auth_error = require_auth()
    if auth_error:
        return auth_error

    material_id = request.args.get("materialId", "")

    sql = """
        SELECT
            t.id,
            t.material_id AS materialId,
            m.material_code AS materialCode,
            m.material_name AS materialName,
            t.transaction_type AS transactionType,
            t.quantity,
            t.warehouse,
            t.reference_no AS referenceNo,
            t.remark,
            t.created_by AS createdBy,
            t.created_at AS createdAt
        FROM material_transaction t
        JOIN material_master m ON m.id = t.material_id
        WHERE 1 = 1
    """
    params = []

    if material_id:
        sql += " AND t.material_id = ?"
        params.append(material_id)

    sql += " ORDER BY t.created_at DESC, t.id DESC LIMIT 100"

    conn = get_conn()
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    return jsonify({
        "success": True,
        "data": [dict(row) for row in rows]
    })

@app.route("/api/material-transactions", methods=["POST"])
def create_material_transaction():
    user, auth_error = require_auth()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True)

    if not data:
        return error_response(400, "INVALID_PAYLOAD", "Request body must be valid JSON.")

    material_id = data.get("materialId")
    transaction_type = data.get("transactionType", "")
    warehouse = str(data.get("warehouse", "MAIN") or "MAIN").strip()
    reference_no = str(data.get("referenceNo", "")).strip()
    remark = str(data.get("remark", "")).strip()

    if transaction_type not in ("in", "out", "adjust"):
        return error_response(400, "INVALID_PAYLOAD", "transactionType must be in, out, or adjust.")

    try:
        quantity = float(data.get("quantity", 0))
    except Exception:
        return error_response(400, "INVALID_PAYLOAD", "quantity must be a number.")

    if transaction_type in ("in", "out") and quantity <= 0:
        return error_response(400, "INVALID_PAYLOAD", "quantity must be greater than 0.")

    timestamp = now_text()
    conn = get_conn()

    material = conn.execute("""
        SELECT id, status FROM material_master WHERE id = ?
    """, (material_id,)).fetchone()

    if material is None:
        conn.close()
        return error_response(404, "MATERIAL_NOT_FOUND", "Material not found.")

    if material["status"] != "active":
        conn.close()
        return error_response(400, "MATERIAL_INACTIVE", "Inactive material cannot receive transactions.")

    stock = conn.execute("""
        SELECT quantity FROM material_stock
        WHERE material_id = ? AND warehouse = ?
    """, (material_id, warehouse)).fetchone()
    current_quantity = stock["quantity"] if stock else 0

    if transaction_type == "in":
        new_quantity = current_quantity + quantity
        transaction_quantity = quantity
    elif transaction_type == "out":
        if current_quantity < quantity:
            conn.close()
            return error_response(400, "INSUFFICIENT_STOCK", "Stock quantity is not enough.")
        new_quantity = current_quantity - quantity
        transaction_quantity = -quantity
    else:
        if quantity < 0:
            conn.close()
            return error_response(400, "INVALID_PAYLOAD", "adjust quantity cannot be negative.")
        new_quantity = quantity
        transaction_quantity = quantity - current_quantity

    try:
        conn.execute("""
            INSERT INTO material_stock (material_id, warehouse, quantity, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(material_id, warehouse)
            DO UPDATE SET quantity = excluded.quantity, updated_at = excluded.updated_at
        """, (material_id, warehouse, new_quantity, timestamp))
        conn.execute("""
            INSERT INTO material_transaction (
                material_id,
                transaction_type,
                quantity,
                warehouse,
                reference_no,
                remark,
                created_by,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            material_id,
            transaction_type,
            transaction_quantity,
            warehouse,
            reference_no,
            remark,
            user["sub"],
            timestamp
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        return error_response(500, "INTERNAL_ERROR", str(e))

    conn.close()

    return jsonify({
        "status": "success",
        "quantity": new_quantity,
        "message": "Material transaction created successfully."
    }), 201

if __name__ == "__main__":
    app.run(debug=True, port=5000)

"""
精品採購管理系統 — 步驟導引版
==================================
必須按順序：填完第一步才能進第二步，一路到最後統一輸出
執行：streamlit run app.py
"""

import streamlit as st
import pandas as pd
import random

random.seed(42)

st.set_page_config(page_title="精品採購管理系統", page_icon="💎", layout="wide")

# ============================================================
# 基礎資料
# ============================================================

STORES = ["信義A8", "忠孝SOGO", "南西店", "板橋店", "台中新光"]
STORE_WEIGHTS = {"信義A8": 1.5, "忠孝SOGO": 1.3, "南西店": 1.0, "板橋店": 0.7, "台中新光": 0.8}

CATEGORIES = {
    "包款": ["Mini Flap Bag", "Leather Tote", "Chain Shoulder Bag", "Bucket Bag"],
    "鞋履": ["Square Toe Sandal", "Ankle Boot", "Loafer", "Sneaker"],
    "配件": ["Silk Scarf", "Logo Belt", "Sunglasses", "Card Holder"],
    "珠寶": ["Chain Necklace", "Hoop Earrings", "Bangle"],
}

PRICES = {
    "Mini Flap Bag": 125000, "Leather Tote": 98000,
    "Chain Shoulder Bag": 115000, "Bucket Bag": 78000,
    "Square Toe Sandal": 32000, "Ankle Boot": 45000,
    "Loafer": 38000, "Sneaker": 28000,
    "Silk Scarf": 18000, "Logo Belt": 22000,
    "Sunglasses": 15000, "Card Holder": 12000,
    "Chain Necklace": 55000, "Hoop Earrings": 38000, "Bangle": 42000,
}

COST_EUR = {
    "Mini Flap Bag": 650, "Leather Tote": 500,
    "Chain Shoulder Bag": 580, "Bucket Bag": 400,
    "Square Toe Sandal": 180, "Ankle Boot": 250,
    "Loafer": 200, "Sneaker": 150,
    "Silk Scarf": 95, "Logo Belt": 120,
    "Sunglasses": 80, "Card Holder": 60,
    "Chain Necklace": 300, "Hoop Earrings": 200, "Bangle": 220,
}

EUR_TO_TWD = 34.5

STEP_NAMES = [
    "① 輸入銷售數據",
    "② 消費者偏好分析",
    "③ 生成叫貨清單",
    "④ 配貨給門市",
    "⑤ 輸入門市銷售",
    "⑥ 庫存調整",
    "⑦ 需求預測補貨",
    "⑧ 滯銷品處理",
    "📊 最終報告",
]


def generate_fake_history():
    records = []
    for month in range(1, 13):
        for store in STORES:
            for cat, styles in CATEGORIES.items():
                for style in styles:
                    base = 10
                    qty = max(1, int(base * STORE_WEIGHTS[store] + random.randint(-3, 5)))
                    records.append({
                        "month": month, "store": store,
                        "category": cat, "style": style, "quantity": qty,
                    })
    return records


# ============================================================
# 步驟控制
# ============================================================

if "current_step" not in st.session_state:
    st.session_state["current_step"] = 0


def go_next():
    st.session_state["current_step"] += 1


def go_prev():
    st.session_state["current_step"] -= 1


step = st.session_state["current_step"]

# --- Sidebar 進度 ---
st.sidebar.title("💎 精品採購系統")
st.sidebar.divider()

for i, name in enumerate(STEP_NAMES):
    if i < step:
        st.sidebar.write(f"✅ {name}")
    elif i == step:
        st.sidebar.write(f"👉 **{name}**")
    else:
        st.sidebar.write(f"⬜ {name}")

st.sidebar.divider()
if step > 0:
    st.sidebar.button("⬅️ 回上一步", on_click=go_prev)

# 進度條
progress = step / (len(STEP_NAMES) - 1)
st.progress(progress, text=f"步驟 {step + 1} / {len(STEP_NAMES)}：{STEP_NAMES[step]}")
st.write("")


# ============================================================
# Step 0：輸入銷售數據
# ============================================================

if step == 0:
    st.title("📥 Step 1：輸入過去銷售數據")

    input_method = st.radio("選擇資料來源", ["使用範例資料", "上傳 CSV"])

    if input_method == "上傳 CSV":
        uploaded = st.file_uploader("上傳 CSV（欄位：month, store, category, style, quantity）", type=["csv"])
        if uploaded:
            df_sales = pd.read_csv(uploaded)
            st.success(f"已上傳 {len(df_sales)} 筆")
        else:
            st.info("等待上傳...")
            st.stop()
    else:
        df_sales = pd.DataFrame(generate_fake_history())
        st.success(f"已載入範例資料 {len(df_sales)} 筆")

    st.subheader("資料預覽")
    st.dataframe(df_sales.head(20), use_container_width=True, hide_index=True)

    st.write("")
    if st.button("下一步 →", type="primary"):
        st.session_state["sales_data"] = df_sales
        go_next()
        st.rerun()


# ============================================================
# Step 1：消費者偏好分析
# ============================================================

elif step == 1:
    st.title("📊 Step 2：台灣消費者偏好分析")

    df_sales = st.session_state["sales_data"]

    col1, col2, col3 = st.columns(3)
    col1.metric("年度總銷量", f"{df_sales['quantity'].sum():,} 件")
    col2.metric("品類數", f"{df_sales['category'].nunique()} 類")
    col3.metric("款式數", f"{df_sales['style'].nunique()} 款")

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("品類銷售佔比")
        cat_data = df_sales.groupby("category")["quantity"].sum().reset_index()
        cat_data.columns = ["品類", "銷量"]
        st.bar_chart(cat_data, x="品類", y="銷量")

    with col_r:
        st.subheader("門市銷售排名")
        store_data = df_sales.groupby("store")["quantity"].sum().sort_values(ascending=False).reset_index()
        store_data.columns = ["門市", "銷量"]
        st.bar_chart(store_data, x="門市", y="銷量")

    st.subheader("月銷量趨勢")
    monthly = df_sales.groupby("month")["quantity"].sum().reset_index()
    monthly.columns = ["月份", "銷量"]
    st.line_chart(monthly, x="月份", y="銷量")

    st.subheader("熱門款式 TOP 10")
    top = df_sales.groupby(["category", "style"])["quantity"].sum().sort_values(ascending=False).head(10).reset_index()
    top.columns = ["品類", "款式", "年銷量"]
    st.dataframe(top, use_container_width=True, hide_index=True)

    style_demand = df_sales.groupby(["category", "style"])["quantity"].sum().reset_index()
    style_demand.columns = ["category", "style", "annual_qty"]

    st.write("")
    if st.button("下一步 →", type="primary"):
        st.session_state["style_demand"] = style_demand
        go_next()
        st.rerun()


# ============================================================
# Step 2：生成叫貨清單
# ============================================================

elif step == 2:
    st.title("📋 Step 3：生成 Assortment 叫貨清單")
    st.caption("系統根據銷售偏好算出建議量，你可以手動調整")

    style_demand = st.session_state["style_demand"]

    order_rows = []
    for _, row in style_demand.iterrows():
        suggested = max(1, round(row["annual_qty"] / 12 * 6 * 1.08))
        order_rows.append({
            "品類": row["category"],
            "款式": row["style"],
            "去年銷量": int(row["annual_qty"]),
            "叫貨數量": suggested,
        })

    df_order = pd.DataFrame(order_rows)

    edited = st.data_editor(
        df_order, use_container_width=True, hide_index=True,
        column_config={
            "叫貨數量": st.column_config.NumberColumn(min_value=0, max_value=9999, step=1),
            "去年銷量": st.column_config.NumberColumn(disabled=True),
            "品類": st.column_config.TextColumn(disabled=True),
            "款式": st.column_config.TextColumn(disabled=True),
        },
    )

    edited["單價EUR"] = edited["款式"].map(COST_EUR).fillna(300)
    edited["總價TWD"] = (edited["叫貨數量"] * edited["單價EUR"] * EUR_TO_TWD).astype(int)

    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("總叫貨數量", f"{edited['叫貨數量'].sum():,} 件")
    col2.metric("總成本 TWD", f"NT${edited['總價TWD'].sum():,}")

    st.write("")
    if st.button("下一步 →", type="primary"):
        st.session_state["order_list"] = edited
        go_next()
        st.rerun()


# ============================================================
# Step 3：配貨給門市
# ============================================================

elif step == 3:
    st.title("🏬 Step 4：配貨給各門市")

    order_list = st.session_state["order_list"]

    st.subheader("門市權重（可調整）")
    weight_cols = st.columns(len(STORES))
    weights = {}
    for i, store in enumerate(STORES):
        with weight_cols[i]:
            weights[store] = st.number_input(
                store, min_value=0.1, max_value=3.0,
                value=STORE_WEIGHTS[store], step=0.1, key=f"w_{store}",
            )

    total_w = sum(weights.values())

    alloc = []
    inv = []
    for _, row in order_list.iterrows():
        for store in STORES:
            qty = max(0, round(row["叫貨數量"] * weights[store] / total_w))
            alloc.append({"門市": store, "品類": row["品類"], "款式": row["款式"], "配貨": qty})
            inv.append({
                "store": store, "category": row["品類"], "style": row["款式"],
                "quantity": qty, "sold": 0, "unit_price": PRICES.get(row["款式"], 50000),
            })

    df_alloc = pd.DataFrame(alloc)

    st.subheader("各門市配貨量")
    st.bar_chart(df_alloc.groupby("門市")["配貨"].sum().reset_index(), x="門市", y="配貨")

    sel = st.selectbox("查看明細", STORES)
    st.dataframe(df_alloc[df_alloc["門市"] == sel], use_container_width=True, hide_index=True)

    st.write("")
    if st.button("下一步 →", type="primary"):
        st.session_state["allocation"] = df_alloc
        st.session_state["inventory"] = pd.DataFrame(inv)
        go_next()
        st.rerun()


# ============================================================
# Step 4：輸入門市銷售
# ============================================================

elif step == 4:
    st.title("🛍️ Step 5：輸入各門市實際銷售")

    inventory = st.session_state["inventory"].copy()

    sim = st.radio("銷售資料", ["自動模擬（隨機）", "手動輸入"])

    if sim == "自動模擬（隨機）":
        for idx in inventory.index:
            max_sell = inventory.loc[idx, "quantity"]
            rate = random.uniform(0.15, 0.95)
            inventory.loc[idx, "sold"] = min(int(max_sell * rate), max_sell)
        st.success("已模擬銷售！")

        summary = inventory.groupby("store").agg(配貨=("quantity", "sum"), 已售=("sold", "sum")).reset_index()
        summary["剩餘"] = summary["配貨"] - summary["已售"]
        summary.columns = ["門市", "配貨", "已售", "剩餘"]
        st.dataframe(summary, use_container_width=True, hide_index=True)
    else:
        sel_store = st.selectbox("選擇門市", STORES)
        store_mask = inventory["store"] == sel_store
        store_inv = inventory[store_mask][["store", "category", "style", "quantity", "sold"]].copy()
        store_inv.columns = ["門市", "品類", "款式", "配貨數", "已售"]

        edited = st.data_editor(store_inv, use_container_width=True, hide_index=True,
            column_config={"已售": st.column_config.NumberColumn(min_value=0, step=1)})

        for i, idx in enumerate(inventory[store_mask].index):
            inventory.loc[idx, "sold"] = edited.iloc[i]["已售"]

        st.info("切換門市輸入各店銷售，全部填完再按下一步")

    st.write("")
    if st.button("下一步 →", type="primary"):
        st.session_state["inventory"] = inventory
        go_next()
        st.rerun()


# ============================================================
# Step 5：庫存調整
# ============================================================

elif step == 5:
    st.title("📦 Step 6：庫存調整與調撥")

    inventory = st.session_state["inventory"].copy()
    inventory["remaining"] = inventory["quantity"] - inventory["sold"]
    inventory["sell_through"] = (inventory["sold"] / inventory["quantity"].replace(0, 1) * 100).round(1)

    # 警報
    st.subheader("🚨 庫存警報")
    low = inventory[inventory["remaining"] <= 2]
    out = low[low["remaining"] == 0]
    if len(out) > 0:
        st.error(f"🔴 斷貨 {len(out)} 項")
    low_only = low[low["remaining"] > 0]
    if len(low_only) > 0:
        st.warning(f"🟡 低庫存 {len(low_only)} 項")
    if len(low) == 0:
        st.success("✅ 全部正常")

    # 調撥
    st.divider()
    st.subheader("🔄 調撥建議")
    transfers = []
    for style in inventory["style"].unique():
        by_store = inventory[inventory["style"] == style].groupby("store")["remaining"].sum()
        if len(by_store) >= 2:
            mx, mn = by_store.idxmax(), by_store.idxmin()
            if by_store[mx] > 8 and by_store[mn] < 3:
                t = min(3, int(by_store[mx] - 5))
                if t > 0:
                    transfers.append({"款式": style, "從": mx, "調出": t, "到": mn})

    if transfers:
        st.dataframe(pd.DataFrame(transfers), use_container_width=True, hide_index=True)
    else:
        st.write("目前無需調撥")

    st.write("")
    if st.button("下一步 →", type="primary"):
        st.session_state["inventory"] = inventory
        go_next()
        st.rerun()


# ============================================================
# Step 6：需求預測
# ============================================================

elif step == 6:
    st.title("🔮 Step 7：需求預測與補貨建議")

    inventory = st.session_state["inventory"].copy()
    inventory["remaining"] = inventory["quantity"] - inventory["sold"]
    inventory["sell_through"] = (inventory["sold"] / inventory["quantity"].replace(0, 1) * 100).round(1)

    st.subheader("需要補貨的品項")
    reorder = inventory[(inventory["sell_through"] > 60) & (inventory["remaining"] < 5)].copy()
    reorder["建議補貨"] = ((reorder["sold"] * 0.5) - reorder["remaining"]).clip(lower=0).astype(int)
    reorder = reorder[reorder["建議補貨"] > 0]

    if len(reorder) > 0:
        display = reorder[["store", "category", "style", "quantity", "sold", "remaining", "sell_through", "建議補貨"]].copy()
        display.columns = ["門市", "品類", "款式", "配貨", "已售", "剩餘", "銷售率%", "建議補貨"]
        st.dataframe(display, use_container_width=True, hide_index=True)
        st.metric("總建議補貨量", f"{display['建議補貨'].sum()} 件")
    else:
        st.success("目前無需補貨")

    st.subheader("各門市銷售率")
    sr = inventory.groupby("store").agg(配=("quantity", "sum"), 售=("sold", "sum")).reset_index()
    sr["銷售率"] = (sr["售"] / sr["配"].replace(0, 1) * 100).round(1)
    sr.columns = ["門市", "配貨", "已售", "銷售率"]
    st.bar_chart(sr, x="門市", y="銷售率")

    st.write("")
    if st.button("下一步 →", type="primary"):
        go_next()
        st.rerun()


# ============================================================
# Step 7：滯銷品處理
# ============================================================

elif step == 7:
    st.title("🏷️ Step 8：滯銷品處理")

    inventory = st.session_state["inventory"].copy()
    inventory["remaining"] = inventory["quantity"] - inventory["sold"]
    inventory["sell_through"] = (inventory["sold"] / inventory["quantity"].replace(0, 1) * 100).round(1)

    col1, col2 = st.columns(2)
    with col1:
        outlet_th = st.slider("送 Outlet 門檻（銷售率 <）", 0, 50, 15)
    with col2:
        disc_th = st.slider("打折門檻（銷售率 <）", 0, 50, 30)

    slow = inventory[inventory["sell_through"] < disc_th].copy()
    slow["處置"] = slow["sell_through"].apply(lambda x: "送 Outlet（5折）" if x < outlet_th else "打 7 折")

    if len(slow) > 0:
        col1, col2 = st.columns(2)
        col1.metric("滯銷品項", f"{len(slow)} 項")
        col2.metric("滯銷庫存", f"{slow['remaining'].sum()} 件")

        display = slow[["store", "category", "style", "quantity", "sold", "remaining", "sell_through", "處置"]].copy()
        display.columns = ["門市", "品類", "款式", "配貨", "已售", "剩餘", "銷售率%", "處置"]
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.success("🎉 沒有滯銷品！")

    st.write("")
    if st.button("完成 → 查看最終報告 📊", type="primary"):
        st.session_state["slow_movers"] = slow if len(slow) > 0 else pd.DataFrame()
        go_next()
        st.rerun()


# ============================================================
# 最終報告：統一輸出全部東西
# ============================================================

elif step == 8:
    st.title("📊 最終報告 — 全部結果彙整")
    st.balloons()

    inventory = st.session_state.get("inventory", pd.DataFrame()).copy()
    inventory["remaining"] = inventory["quantity"] - inventory["sold"]
    inventory["sell_through"] = (inventory["sold"] / inventory["quantity"].replace(0, 1) * 100).round(1)

    # === 1. 叫貨清單 ===
    st.header("一、台灣總部叫貨清單")
    order = st.session_state.get("order_list", pd.DataFrame())
    if len(order) > 0:
        st.dataframe(order[["品類", "款式", "叫貨數量", "總價TWD"]], use_container_width=True, hide_index=True)
        col1, col2 = st.columns(2)
        col1.metric("總叫貨", f"{order['叫貨數量'].sum():,} 件")
        col2.metric("總成本", f"NT${order['總價TWD'].sum():,}")
    st.divider()

    # === 2. 配貨結果 ===
    st.header("二、各門市配貨")
    alloc = st.session_state.get("allocation", pd.DataFrame())
    if len(alloc) > 0:
        st.bar_chart(alloc.groupby("門市")["配貨"].sum().reset_index(), x="門市", y="配貨")
    st.divider()

    # === 3. 銷售成果 ===
    st.header("三、各門市銷售成果")
    if len(inventory) > 0:
        summary = inventory.groupby("store").agg(
            配貨=("quantity", "sum"), 已售=("sold", "sum"), 剩餘=("remaining", "sum"),
        ).reset_index()
        summary["銷售率%"] = (summary["已售"] / summary["配貨"].replace(0, 1) * 100).round(1)
        summary.columns = ["門市", "配貨", "已售", "剩餘", "銷售率%"]
        st.dataframe(summary, use_container_width=True, hide_index=True)
    st.divider()

    # === 4. 庫存現況 ===
    st.header("四、庫存現況")
    low = inventory[inventory["remaining"] <= 2]
    if len(low) > 0:
        st.error(f"需注意：{len(low)} 項低庫存 / 斷貨")
    else:
        st.success("庫存充足")
    st.divider()

    # === 5. 滯銷品 ===
    st.header("五、滯銷品處置")
    slow = st.session_state.get("slow_movers", pd.DataFrame())
    if len(slow) > 0:
        display = slow[["store", "category", "style", "remaining", "sell_through", "處置"]].copy()
        display.columns = ["門市", "品類", "款式", "剩餘", "銷售率%", "處置"]
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.success("無滯銷品")
    st.divider()

    # === 匯出 ===
    st.header("📥 匯出報告")
    col1, col2, col3 = st.columns(3)

    with col1:
        if len(order) > 0:
            csv1 = order.to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 叫貨清單", csv1, "叫貨清單.csv", "text/csv")

    with col2:
        if len(inventory) > 0:
            inv_export = inventory[["store", "category", "style", "quantity", "sold", "remaining", "sell_through"]].copy()
            inv_export.columns = ["門市", "品類", "款式", "配貨", "已售", "剩餘", "銷售率%"]
            csv2 = inv_export.to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 庫存報告", csv2, "庫存報告.csv", "text/csv")

    with col3:
        if len(slow) > 0:
            csv3 = slow.to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 滯銷品清單", csv3, "滯銷品清單.csv", "text/csv")

    st.divider()
    if st.button("🔄 重新開始"):
        st.session_state.clear()
        st.rerun()
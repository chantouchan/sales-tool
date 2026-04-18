import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

DATA_PATH = "data/sales.csv"
MEMBERS = ["山中", "田中", "佐藤", "鈴木"]
STATUS_OPTIONS = ["リード獲得","初回連絡","アポ取得","商談中","見積提出","成約","失注"]
STATUS_COLORS = {"リード獲得":"⚪","初回連絡":"🟡","アポ取得":"🔵","商談中":"🟣","見積提出":"🟠","成約":"🟢","失注":"🔴"}

SAMPLE_DATA = [
    {"会社名":"ABC不動産","ステータス":"リード獲得","見積金額":"","次回アクション日":"","メモ":"","担当者":"山中","登録日":"2026-04-01"},
    {"会社名":"ブルースカイ開発","ステータス":"見積提出","見積金額":"500000","次回アクション日":"","メモ":"","担当者":"佐藤","登録日":"2026-04-02"},
    {"会社名":"パシフィックホテルズ","ステータス":"見積提出","見積金額":"1200000","次回アクション日":"","メモ":"","担当者":"山中","登録日":"2026-04-03"},
    {"会社名":"グリーンヒルズ管理","ステータス":"初回連絡","見積金額":"","次回アクション日":"2026-04-20","メモ":"担当者不在で折り返し待ち","担当者":"田中","登録日":"2026-04-03"},
    {"会社名":"サンライズ建設","ステータス":"商談中","見積金額":"800000","次回アクション日":"2026-04-18","メモ":"現地調査の日程調整中","担当者":"鈴木","登録日":"2026-04-04"},
    {"会社名":"マリンリゾート","ステータス":"見積提出","見積金額":"2000000","次回アクション日":"","メモ":"","担当者":"田中","登録日":"2026-04-04"},
    {"会社名":"東京ステイ","ステータス":"アポ取得","見積金額":"","次回アクション日":"2026-04-22","メモ":"来週訪問予定","担当者":"山中","登録日":"2026-04-05"},
    {"会社名":"大阪ホスピタリティ","ステータス":"リード獲得","見積金額":"","次回アクション日":"","メモ":"","担当者":"佐藤","登録日":"2026-04-05"},
    {"会社名":"北海道リゾート開発","ステータス":"商談中","見積金額":"3000000","次回アクション日":"2026-04-15","メモ":"大型案件","担当者":"鈴木","登録日":"2026-04-05"},
    {"会社名":"九州温泉グループ","ステータス":"初回連絡","見積金額":"","次回アクション日":"2026-04-25","メモ":"資料送付済み","担当者":"田中","登録日":"2026-04-05"},
]

def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH, dtype=str).fillna("")
    df = pd.DataFrame(SAMPLE_DATA)
    os.makedirs("data", exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    return df

def save_data(df):
    df.to_csv(DATA_PATH, index=False)

st.set_page_config(page_title="山中産業 営業管理", page_icon="💼", layout="wide")
st.title("💼 山中産業 営業管理ツール")

df = load_data()

login_user = st.sidebar.selectbox("ユーザーを選択", ["マネージャー"] + MEMBERS)
st.sidebar.info(f"ログイン中：**{login_user}**")

# === アラート ===
alert_no_action = df[(df["ステータス"] == "見積提出") & (df["次回アクション日"] == "")]
alert_overdue = df[(df["次回アクション日"] != "") & (df["次回アクション日"] < str(date.today())) & (~df["ステータス"].isin(["成約","失注"]))]
if len(alert_no_action) or len(alert_overdue):
    st.header("🚨 アラート")
    if len(alert_no_action):
        st.error(f"⚠️ 見積提出済みで次回アクションが未定：**{len(alert_no_action)}件**")
        for _, r in alert_no_action.iterrows():
            st.warning(f"　**{r['会社名']}**（担当：{r['担当者']}）→ 次回アクション日を設定してください")
    if len(alert_overdue):
        st.error(f"⚠️ 次回アクション日を過ぎている案件：**{len(alert_overdue)}件**")
        for _, r in alert_overdue.iterrows():
            st.warning(f"　**{r['会社名']}**（担当：{r['担当者']}）→ アクション期限：{r['次回アクション日']}")

# === パイプライン ===
st.header("📈 パイプライン進捗")
if len(df):
    total = len(df)
    counts = df["ステータス"].value_counts()
    cols = st.columns(len(STATUS_OPTIONS))
    for i, status in enumerate(STATUS_OPTIONS):
        cols[i].metric(f"{STATUS_COLORS.get(status,'')} {status}", int(counts.get(status, 0)))
    won = int(counts.get("成約", 0))
    st.progress(won / total if total else 0)
    st.caption(f"成約進捗：**{won}/{total}（{won/total*100:.1f}%）**")

# === 案件一覧 ===
st.header("📋 案件一覧")
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    f_member_option = st.selectbox("担当者", ["全て"] + MEMBERS)
with col_f2:
    f_status_option = st.selectbox("ステータス", ["全て"] + STATUS_OPTIONS)
with col_f3:
    f_company = st.text_input("会社名で検索")

filtered = df.copy()
if f_member_option != "全て":
    filtered = filtered[filtered["担当者"] == f_member_option]
if f_status_option != "全て":
    filtered = filtered[filtered["ステータス"] == f_status_option]
if f_company:
    filtered = filtered[filtered["会社名"].str.contains(f_company, na=False)]

display = filtered.copy()
display["ステータス"] = display["ステータス"].map(lambda s: f"{STATUS_COLORS.get(s,'')} {s}")
if len(display):
    display["見積金額"] = display["見積金額"].apply(lambda x: f"¥{int(x):,}" if x and x.isdigit() else x)

col_config = {
    "会社名": st.column_config.TextColumn("会社名", width=150),
    "ステータス": st.column_config.TextColumn("ステータス", width=120),
    "見積金額": st.column_config.TextColumn("見積金額", width=100),
    "次回アクション日": st.column_config.TextColumn("次回アクション日", width=90),
    "メモ": st.column_config.TextColumn("メモ", width=300),
    "担当者": st.column_config.TextColumn("担当者", width=70),
    "登録日": st.column_config.TextColumn("登録日", width=90),
}
st.dataframe(display, hide_index=True, height=400, column_config=col_config)

# === ステータス更新 ===
st.header("✏️ ステータス更新")
if login_user == "マネージャー":
    update_targets = df["会社名"].tolist()
else:
    update_targets = df[df["担当者"] == login_user]["会社名"].tolist()

with st.form("update_form"):
    target = st.multiselect("更新する案件（複数選択可）", options=update_targets)
    new_status = st.selectbox("新しいステータス", STATUS_OPTIONS)
    action_date = st.date_input("次回アクション日", value=date.today())
    amount = st.text_input("見積金額（変更する場合）")
    memo = st.text_input("メモ")
    submitted = st.form_submit_button("更新する")
    if submitted and target:
        for comp in target:
            idx = df.index[df["会社名"] == comp].tolist()
            if idx:
                i = idx[0]
                df.at[i, "ステータス"] = new_status
                df.at[i, "次回アクション日"] = str(action_date)
                if amount:
                    df.at[i, "見積金額"] = amount
                if memo:
                    cur = df.at[i, "メモ"]
                    df.at[i, "メモ"] = f"{cur} / {memo}" if cur else memo
        save_data(df)
        st.success(f"{len(target)}件を「{new_status}」に更新しました")
        st.rerun()

# === 新規案件追加 ===
st.header("➕ 新規案件追加")
with st.form("new_deal"):
    new_company = st.text_input("会社名")
    new_status = st.selectbox("ステータス", STATUS_OPTIONS, key="new_st")
    new_amount = st.text_input("見積金額（数字のみ）")
    new_date = st.date_input("次回アクション日", value=date.today(), key="new_date")
    new_memo = st.text_area("メモ")
    if login_user == "マネージャー":
        new_person = st.selectbox("担当者", MEMBERS, key="new_person")
    else:
        new_person = login_user
        st.text(f"担当者：{login_user}")
    new_submitted = st.form_submit_button("登録する")
    if new_submitted:
        if not new_company:
            st.error("会社名を入力してください。")
        else:
            row = pd.DataFrame([{
                "会社名": new_company, "ステータス": new_status,
                "見積金額": new_amount, "次回アクション日": str(new_date),
                "メモ": new_memo, "担当者": new_person,
                "登録日": str(date.today())
            }])
            df = pd.concat([df, row], ignore_index=True)
            save_data(df)
            st.success(f"「{new_company}」を登録しました！")
            st.rerun()

# === その他 ===
st.header("⚡ その他")
col1, col2 = st.columns(2)
with col1:
    st.download_button("📥 CSVダウンロード", df.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"営業管理_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")
with col2:
    if st.button("データリセット（注意）"):
        os.remove(DATA_PATH)
        st.success("リセットしました。")
        st.rerun()

st.divider()
st.caption("© 2026 山中産業 営業管理システム")

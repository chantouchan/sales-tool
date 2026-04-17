import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# ==================================================
# 設定
# ==================================================
DATA_PATH = "data/sales.csv"

MEMBERS = ["山中", "田中", "佐藤", "鈴木"]

STATUS_OPTIONS = [
    "リード獲得",
    "初回連絡",
    "アポ取得",
    "商談中",
    "見積提出",
    "成約",
    "失注",
]

STATUS_COLORS = {
    "リード獲得": "⚪",
    "初回連絡": "🟡",
    "アポ取得": "🔵",
    "商談中": "🟣",
    "見積提出": "🟠",
    "成約": "🟢",
    "失注": "🔴",
}

# ==================================================
# 初期データ（サンプル）
# ==================================================
SAMPLE_DATA = [
    {"会社名": "ABC不動産", "ステータス": "リード獲得", "見積金額": "", "次回アクション日": "", "メモ": "", "担当者": "山中", "登録日": "2026-04-01"},
    {"会社名": "東京建設株式会社", "ステータス": "リード獲得", "見積金額": "", "次回アクション日": "", "メモ": "", "担当者": "山中", "登録日": "2026-04-01"},
    {"会社名": "サンライズホーム", "ステータス": "リード獲得", "見積金額": "", "次回アクション日": "", "メモ": "", "担当者": "田中", "登録日": "2026-04-02"},
    {"会社名": "グリーンマンション", "ステータス": "リード獲得", "見積金額": "", "次回アクション日": "", "メモ": "", "担当者": "田中", "登録日": "2026-04-02"},
    {"会社名": "ブルースカイ開発", "ステータス": "見積提出", "見積金額": "500000", "次回アクション日": "", "メモ": "", "担当者": "佐藤", "登録日": "2026-04-03"},
    {"会社名": "マリンリゾート", "ステータス": "見積提出", "見積金額": "800000", "次回アクション日": "2026-04-10", "メモ": "", "担当者": "佐藤", "登録日": "2026-04-03"},
    {"会社名": "大阪ハウジング", "ステータス": "リード獲得", "見積金額": "", "次回アクション日": "", "メモ": "", "担当者": "鈴木", "登録日": "2026-04-04"},
    {"会社名": "フジ住宅販売", "ステータス": "リード獲得", "見積金額": "", "次回アクション日": "", "メモ": "", "担当者": "鈴木", "登録日": "2026-04-04"},
    {"会社名": "パシフィックホテルズ", "ステータス": "見積提出", "見積金額": "1200000", "次回アクション日": "", "メモ": "", "担当者": "山中", "登録日": "2026-04-05"},
    {"会社名": "ノースランド建設", "ステータス": "リード獲得", "見積金額": "", "次回アクション日": "", "メモ": "", "担当者": "田中", "登録日": "2026-04-05"},
]

# ==================================================
# データ読み込み・初期化
# ==================================================
def load_data() -> pd.DataFrame:
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH, dtype=str).fillna("")
        return df
    else:
        df = pd.DataFrame(SAMPLE_DATA)
        os.makedirs("data", exist_ok=True)
        df.to_csv(DATA_PATH, index=False)
        return df


def save_data(df: pd.DataFrame):
    df.to_csv(DATA_PATH, index=False)


# ==================================================
# ページ設定
# ==================================================
st.set_page_config(page_title="山中産業 営業管理", layout="wide")
st.title("💼 山中産業 営業管理ツール")

df = load_data()

# ==================================================
# サイドバー：ログイン
# ==================================================
st.sidebar.header("ログイン")
login_user = st.sidebar.selectbox("ユーザーを選択", ["マネージャー"] + MEMBERS)
st.sidebar.info(f"ログイン中：**{login_user}**")

# ==================================================
# アラート
# ==================================================
# 見積提出済みで次回アクション日が空
alert_no_action = df[
    (df["ステータス"] == "見積提出") & (df["次回アクション日"] == "")
]

# 次回アクション日が過ぎている（成約・失注以外）
today_str = str(date.today())
alert_overdue = df[
    (df["次回アクション日"] != "") &
    (df["次回アクション日"] < today_str) &
    (~df["ステータス"].isin(["成約", "失注"]))
]

if len(alert_no_action) > 0 or len(alert_overdue) > 0:
    st.header("🚨 アラート")

    if len(alert_no_action) > 0:
        st.error(f"⚠️ 見積提出済みで次回アクションが未定：**{len(alert_no_action)}件**")
        for _, row in alert_no_action.iterrows():
            st.warning(f"　**{row['会社名']}**（担当：{row['担当者']}）→ 次回アクション日を設定してください")

    if len(alert_overdue) > 0:
        st.error(f"⚠️ 次回アクション日を過ぎている案件：**{len(alert_overdue)}件**")
        for _, row in alert_overdue.iterrows():
            st.warning(f"　**{row['会社名']}**（担当：{row['担当者']}）→ アクション期限：{row['次回アクション日']}")

# ==================================================
# パイプライン進捗
# ==================================================
st.header("📈 パイプライン進捗")

total = len(df)
counts = df["ステータス"].value_counts()

pipeline_cols = st.columns(len(STATUS_OPTIONS))
for i, status in enumerate(STATUS_OPTIONS):
    count = int(counts.get(status, 0))
    pipeline_cols[i].metric(
        f"{STATUS_COLORS.get(status, '')} {status}",
        count
    )

won = int(counts.get("成約", 0))
st.progress(won / total if total > 0 else 0)
st.caption(f"成約進捗：**{won}/{total}（{won/total*100:.1f}%）**")

# ==================================================
# 案件一覧
# ==================================================
st.header("📋 案件一覧")

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    filter_member = st.multiselect(
        "担当者で絞り込み",
        options=MEMBERS,
        default=[login_user] if login_user in MEMBERS else MEMBERS,
    )
with col_f2:
    filter_status = st.multiselect(
        "ステータスで絞り込み",
        options=STATUS_OPTIONS,
        default=STATUS_OPTIONS,
    )
with col_f3:
    filter_company = st.text_input("会社名で検索", "")

view_df = df.copy()
if filter_member:
    view_df = view_df[view_df["担当者"].isin(filter_member)]
if filter_status:
    view_df = view_df[view_df["ステータス"].isin(filter_status)]
if filter_company:
    view_df = view_df[view_df["会社名"].str.contains(filter_company, na=False)]

display_df = view_df.copy()
display_df["ステータス"] = display_df["ステータス"].map(
    lambda s: f"{STATUS_COLORS.get(s, '')} {s}"
)
display_df["見積金額"] = view_df["見積金額"].apply(
    lambda x: f"¥{int(float(x)):,}" if x != "" else ""
)

st.dataframe(
    display_df,
    hide_index=True,
    width="stretch",
    height=400,
    column_config={
        "会社名": st.column_config.TextColumn("会社名", width=150),
        "ステータス": st.column_config.TextColumn("ステータス", width=120),
        "見積金額": st.column_config.TextColumn("見積金額", width=100),
        "次回アクション日": st.column_config.TextColumn("次回アクション日", width=90),
        "メモ": st.column_config.TextColumn("メモ", width=300),
        "担当者": st.column_config.TextColumn("担当者", width=70),
        "登録日": st.column_config.TextColumn("登録日", width=90),
    },
)

# ==================================================
# ステータス更新
# ==================================================
st.header("✏️ ステータス更新")

with st.form("update_deal"):
    if login_user in MEMBERS:
        my_companies = df[df["担当者"] == login_user]["会社名"].tolist()
    else:
        my_companies = df["会社名"].tolist()

    target_companies = st.multiselect(
        "更新する案件（複数選択可）",
        options=my_companies,
    )
    new_status = st.selectbox("新しいステータス", STATUS_OPTIONS)

    col_a, col_b = st.columns(2)
    with col_a:
        action_date = st.date_input("次回アクション日", value=date.today())
    with col_b:
        amount = st.text_input("見積金額（変更する場合）")

    memo = st.text_input("メモ")

    submitted = st.form_submit_button("更新する")

    if submitted and target_companies:
        date_str = str(action_date)
        for company in target_companies:
            if login_user in MEMBERS:
                idx = df.index[
                    (df["会社名"] == company) & (df["担当者"] == login_user)
                ].tolist()
            else:
                idx = df.index[df["会社名"] == company].tolist()
            if idx:
                i = idx[0]
                df.at[i, "ステータス"] = new_status
                df.at[i, "次回アクション日"] = date_str
                if amount:
                    df.at[i, "見積金額"] = amount
                if memo:
                    existing = df.at[i, "メモ"]
                    df.at[i, "メモ"] = f"{existing} / {memo}" if existing else memo

        save_data(df)
        st.success(f"{len(target_companies)}件を「{new_status}」に更新しました")
        st.rerun()

# ==================================================
# 新規案件追加
# ==================================================
if login_user in MEMBERS:
    st.header("➕ 新規案件追加")

    with st.form("new_deal"):
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            new_company = st.text_input("会社名")
        with col_n2:
            new_status = st.selectbox("ステータス", STATUS_OPTIONS, key="new_status")

        col_n3, col_n4 = st.columns(2)
        with col_n3:
            new_amount = st.text_input("見積金額（数字のみ）", placeholder="例: 500000")
        with col_n4:
            new_action_date = st.date_input("次回アクション日", value=date.today(), key="new_date")

        new_memo = st.text_area("メモ")

        new_submitted = st.form_submit_button("登録する")

        if new_submitted:
            if not new_company:
                st.error("会社名を入力してください。")
            else:
                new_row = pd.DataFrame([{
                    "会社名": new_company,
                    "ステータス": new_status,
                    "見積金額": new_amount,
                    "次回アクション日": str(new_action_date),
                    "メモ": new_memo,
                    "担当者": login_user,
                    "登録日": str(date.today()),
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.success(f"「{new_company}」を登録しました！")
                st.rerun()

# ==================================================
# その他
# ==================================================
st.header("⚡ その他")

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    st.download_button(
        label="📥 CSV ダウンロード",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"営業管理_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
with col_btn2:
    if st.button("データリセット（注意）"):
        os.remove(DATA_PATH)
        st.success("リセットしました。")
        st.rerun()

st.divider()
st.caption("© 2026 山中産業 営業管理システム")

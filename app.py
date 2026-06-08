import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np


BASE_DIR = os.path.dirname(__file__)

# ── 页面配置 ────
st.set_page_config(
    page_title="多 Agent 量化交易系统",
    page_icon="📈",
    layout="wide",
)

st.title("📈 多 Agent 量化交易系统 · 回测看板")
st.caption("AAPL · 2020-01-01 ~ 2024-12-31 | 技术 Agent + 情感 Agent + 风险控制 Agent")

# ── 加载数据 ─────────────────────────────────────────────
@st.cache_data
def load_backtest():
    df = pd.read_csv(
        os.path.join(BASE_DIR, "results", "backtest_results.csv"),
        parse_dates=["Date"]
    )
    df.set_index("Date", inplace=True)
    return df

@st.cache_data
def load_metrics():
    df = pd.read_csv(os.path.join(BASE_DIR, "results", "metrics.csv"), index_col=0)
    df.index = df.index.astype(str).str.strip()
    df.rename(index={"Full Multi-Agent": "Long-Biased Multi-Agent"}, inplace=True)
    return df

@st.cache_data
def load_sentiment():
    df = pd.read_csv(os.path.join(BASE_DIR, "data", "monthly_sentiment.csv"))
    df["month"] = pd.to_datetime(df["month"])
    return df

df = load_backtest()
metrics_df = load_metrics()
sentiment_df = load_sentiment()

# ── 侧边栏：时间筛选 ─────────────────────────────────────
st.sidebar.header("🔧 参数设置")
date_min = df.index.min().date()
date_max = df.index.max().date()
start_date, end_date = st.sidebar.date_input(
    "回测区间",
    value=(date_min, date_max),
    min_value=date_min,
    max_value=date_max,
)
df_view = df.loc[str(start_date):str(end_date)].copy()

show_strategies = st.sidebar.multiselect(
    "显示策略",
    options=["买入并持有", "纯技术策略", "技术+情感", "长期持有偏向多Agent"],
    default=["买入并持有", "纯技术策略", "技术+情感", "长期持有偏向多Agent"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Agent 说明**")
st.sidebar.markdown(
    "- **技术 Agent**：MA20/60 + RSI + MACD 三信号投票\n"
    "- **情感 Agent**：DeepSeek LLM 月度情感评分\n"
    "- **风险 Agent**：risk_score≥0.75 一票否决 + 最大回撤25%极端保护\n"
    "- **决策 Agent**：长期持有为主，技术转空且情绪负面时退出"
)

# ── 指标卡片 ─────────────────────────────────────────────
st.subheader("📊 策略绩效总览")

col_map = {
    "买入并持有": "Buy and Hold",
    "纯技术策略": "Technical Only",
    "技术+情感":  "Technical + Sentiment",
    "长期持有偏向多Agent": "Long-Biased Multi-Agent",
}
color_map = {
    "买入并持有":  "#636EFA",
    "纯技术策略":  "#EF553B",
    "技术+情感":   "#00CC96",
    "长期持有偏向多Agent": "#FF6692",
}
curve_col = {
    "买入并持有":  "buy_hold_curve",
    "纯技术策略":  "technical_curve",
    "技术+情感":   "tech_sent_curve",
    "长期持有偏向多Agent": "multi_agent_curve",
}

cols = st.columns(4)
metric_labels = {
    "Cumulative Return": "累计收益率",
    "Annual Return":     "年化收益率",
    "Sharpe Ratio":      "夏普比率",
    "Max Drawdown":      "最大回撤",
}
highlight_row = "Long-Biased Multi-Agent"
for i, (cn, en) in enumerate(col_map.items()):
    with cols[i]:
        if en not in metrics_df.index:
            st.error(f"Missing metrics row: {en}")
            st.caption(", ".join(metrics_df.index.astype(str)))
            continue
        row = metrics_df.loc[en]
        cr  = f"{row['Cumulative Return']*100:.2f}%"
        sr  = f"{row['Sharpe Ratio']:.3f}"
        mdd = f"{row['Max Drawdown']*100:.2f}%"
        ar  = f"{row['Annual Return']*100:.2f}%"
        delta_sr = f"Sharpe {sr}"
        st.metric(label=cn, value=cr, delta=f"夏普 {sr}  |  MDD {mdd}")

st.markdown("---")

# ── 净值曲线 ─────────────────────────────────────────────
st.subheader("📈 净值曲线对比")
fig_equity = go.Figure()
for name in show_strategies:
    col = curve_col[name]
    if col in df_view.columns:
        fig_equity.add_trace(go.Scatter(
            x=df_view.index,
            y=df_view[col],
            name=name,
            line=dict(color=color_map[name], width=2),
        ))
fig_equity.update_layout(
    height=400,
    xaxis_title="日期",
    yaxis_title="净值",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=40, r=20, t=20, b=40),
)
st.plotly_chart(fig_equity, use_container_width=True)

# ── 回撤曲线 ─────────────────────────────────────────────
st.subheader("📉 回撤曲线")
fig_dd = go.Figure()
for name in show_strategies:
    col = curve_col[name]
    if col in df_view.columns:
        curve = df_view[col]
        peak = curve.cummax()
        dd = (curve - peak) / peak
        fig_dd.add_trace(go.Scatter(
            x=df_view.index,
            y=dd * 100,
            name=name,
            fill="tozeroy",
            line=dict(color=color_map[name], width=1.5),
            opacity=0.7,
        ))
fig_dd.update_layout(
    height=300,
    xaxis_title="日期",
    yaxis_title="回撤 (%)",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=40, r=20, t=20, b=40),
)
st.plotly_chart(fig_dd, use_container_width=True)

st.markdown("---")

# ── 技术信号 + 持仓 ───────────────────────────────────────
st.subheader("🔍 技术信号与持仓详情")

tab1, tab2 = st.tabs(["技术指标走势", "多Agent持仓分布"])

with tab1:
    fig_tech = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.5, 0.25, 0.25],
        vertical_spacing=0.04,
    )
    # 收盘价 + 均线
    fig_tech.add_trace(go.Scatter(x=df_view.index, y=df_view["Close"],
                                  name="收盘价", line=dict(color="#888", width=1)), row=1, col=1)
    fig_tech.add_trace(go.Scatter(x=df_view.index, y=df_view["MA20"],
                                  name="MA20", line=dict(color="#FFA500", width=1.5)), row=1, col=1)
    fig_tech.add_trace(go.Scatter(x=df_view.index, y=df_view["MA60"],
                                  name="MA60", line=dict(color="#00BFFF", width=1.5)), row=1, col=1)
    # RSI
    fig_tech.add_trace(go.Scatter(x=df_view.index, y=df_view["RSI"],
                                  name="RSI", line=dict(color="#9B59B6", width=1.5)), row=2, col=1)
    fig_tech.add_hline(y=70, line_dash="dash", line_color="red",   row=2, col=1)
    fig_tech.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    # MACD
    fig_tech.add_trace(go.Scatter(x=df_view.index, y=df_view["MACD"],
                                  name="MACD", line=dict(color="#E74C3C", width=1.5)), row=3, col=1)
    fig_tech.add_trace(go.Scatter(x=df_view.index, y=df_view["MACD_signal"],
                                  name="MACD Signal", line=dict(color="#2ECC71", width=1.5)), row=3, col=1)
    fig_tech.update_layout(height=500, hovermode="x unified",
                           margin=dict(l=40, r=20, t=10, b=40),
                           legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1))
    fig_tech.update_yaxes(title_text="价格 ($)", row=1, col=1)
    fig_tech.update_yaxes(title_text="RSI",      row=2, col=1)
    fig_tech.update_yaxes(title_text="MACD",     row=3, col=1)
    st.plotly_chart(fig_tech, use_container_width=True)

with tab2:
    pos_counts = {
        "纯技术策略":  df_view["technical_position"].value_counts().to_dict(),
        "技术+情感":   df_view["tech_sent_position"].value_counts().to_dict(),
        "长期持有偏向多Agent": df_view["multi_agent_position"].value_counts().to_dict(),
    }
    bar_data = []
    for strat, counts in pos_counts.items():
        hold  = counts.get(1, 0)
        cash  = counts.get(0, 0)
        total = hold + cash
        bar_data.append({"策略": strat, "状态": "持仓", "天数": hold,
                          "占比": f"{hold/total*100:.1f}%"})
        bar_data.append({"策略": strat, "状态": "空仓", "天数": cash,
                          "占比": f"{cash/total*100:.1f}%"})
    bar_df = pd.DataFrame(bar_data)
    fig_bar = px.bar(bar_df, x="策略", y="天数", color="状态",
                     barmode="stack", text="占比",
                     color_discrete_map={"持仓": "#2ECC71", "空仓": "#E74C3C"})
    fig_bar.update_layout(height=350, margin=dict(l=40, r=20, t=20, b=40))
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ── 情感数据 ─────────────────────────────────────────────
st.subheader("🧠 DeepSeek 情感 Agent · 月度评分")

fig_sent = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    row_heights=[0.5, 0.5],
    vertical_spacing=0.08,
    subplot_titles=("情感评分 (sentiment_score)", "风险评分 (risk_score)"),
)
colors_sent = ["#E74C3C" if v < 0 else "#2ECC71" for v in sentiment_df["sentiment_score"]]
fig_sent.add_trace(
    go.Bar(x=sentiment_df["month"], y=sentiment_df["sentiment_score"],
           marker_color=colors_sent, name="情感评分"),
    row=1, col=1,
)
fig_sent.add_trace(
    go.Scatter(x=sentiment_df["month"], y=sentiment_df["risk_score"],
               fill="tozeroy", line=dict(color="#E67E22", width=2),
               name="风险评分"),
    row=2, col=1,
)
fig_sent.add_hline(y=0.75, line_dash="dash", line_color="red",
                   annotation_text="一票否决阈值 0.75", row=2, col=1)
fig_sent.update_layout(height=420, hovermode="x unified",
                        margin=dict(l=40, r=20, t=40, b=40),
                        showlegend=False)
st.plotly_chart(fig_sent, use_container_width=True)

# ── 情感表格 ─────────────────────────────────────────────
with st.expander("📋 查看月度情感详情"):
    display_df = sentiment_df.copy()
    display_df["month"] = display_df["month"].dt.strftime("%Y-%m")
    display_df.columns = ["月份", "事件摘要", "情感评分", "风险评分"]
    st.dataframe(display_df, use_container_width=True, height=300)

st.markdown("---")

# ── 指标汇总表 ────────────────────────────────────────────
st.subheader("📋 绩效指标汇总")
fmt_df = metrics_df.copy()
for col in ["Cumulative Return", "Annual Return", "Annual Volatility", "Max Drawdown"]:
    fmt_df[col] = fmt_df[col].apply(lambda x: f"{x*100:.2f}%")
fmt_df["Sharpe Ratio"] = fmt_df["Sharpe Ratio"].apply(lambda x: f"{x:.4f}")
fmt_df.index.name = "策略"
fmt_df.columns = ["累计收益率", "年化收益率", "年化波动率", "夏普比率", "最大回撤"]
st.dataframe(fmt_df, use_container_width=True)

st.markdown("---")
st.caption("数据来源：NASDAQ · AAPL日线 | 情感数据：DeepSeek API 批量生成")

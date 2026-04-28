import streamlit as st
import numpy as np
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
import time

# ---------------------------
# PAGE SETUP
# ---------------------------
st.set_page_config(page_title="P-Value Slot Machine", layout="centered")

st.title("🎰 P-Value Slot Machine")
st.write("Each spin = one experiment where there is NO real difference between groups.")

# ---------------------------
# SESSION STATE
# ---------------------------
if "runs" not in st.session_state:
    st.session_state.runs = 0
if "significant" not in st.session_state:
    st.session_state.significant = 0
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.header("Settings")

n = st.sidebar.slider("Sample size per group", 5, 200, 30)
alpha = st.sidebar.selectbox("Significance level (alpha)", [0.05, 0.01])


if st.sidebar.button("Reset"):
    st.session_state.runs = 0
    st.session_state.significant = 0
    st.session_state.history = []
    st.rerun()

# ---------------------------
# FUNCTIONS
# ---------------------------
def simulate_once(n):
    return np.random.normal(0,1,n), np.random.normal(0,1,n)

def run_experiment():
    g1, g2 = simulate_once(n)

    if len(g1) < 3 or len(g2) < 3:
        return run_experiment()

    stat, p = ttest_ind(g1, g2, equal_var=False)
    return p, g1, g2, np.mean(g1) - np.mean(g2)

# ---------------------------
# RUN BUTTON
# ---------------------------
fruits = ["🍒", "🍋", "🍊", "🍇", "🍉", "⭐"]

if st.button("🎲 Run Study", use_container_width=True):

    p, g1, g2, effect = run_experiment()

    st.session_state.runs += 1
    st.session_state.history.append(p)

    if p < alpha:
        st.session_state.significant += 1

    # ---------------------------
    # SLOT MACHINE (SPIN)
    # ---------------------------
    st.write("### 🎰 Result")

    slot = st.empty()
    final_reel = None

    for i in range(10):
        reel = np.random.choice(fruits, 3, replace=False)
        slot.markdown(
            f"<h1 style='text-align:center'>{reel[0]} {reel[1]} {reel[2]}</h1>",
            unsafe_allow_html=True
        )
        final_reel = reel
        time.sleep(0.05 + i*0.01)  # slows slightly

    if p < alpha:
        slot.markdown(
            "<h1 style='text-align:center'>⭐ ⭐ ⭐</h1>",
            unsafe_allow_html=True
        )
    else:
        slot.markdown(
            f"<h1 style='text-align:center'>{final_reel[0]} {final_reel[1]} {final_reel[2]}</h1>",
            unsafe_allow_html=True
        )

    # ---------------------------
    # RESULTS
    # ---------------------------
    if p < alpha:
        st.success(f"🎉 SIGNIFICANT! p = {p:.4f}")
    else:
        st.info(f"Not significant. p = {p:.4f}")

    st.write(f"Effect size: {effect:.3f}")

    fig, ax = plt.subplots()
    ax.boxplot([g1, g2], labels=["Group 1", "Group 2"])
    st.pyplot(fig)

# ---------------------------
# SUMMARY
# ---------------------------
st.write("---")

runs = st.session_state.runs
sig = st.session_state.significant

if runs > 0:
    st.subheader("Results so far")
    st.write(f"Runs: {runs}")
    st.write(f"Significant results: {sig}")
    st.write(f"Proportion significant: {sig/runs:.3f}")
    st.caption("Expected under the null ≈ alpha")

# ---------------------------
# HISTORY DOTS
# ---------------------------
if st.session_state.history:
    st.subheader("Recent runs")

    last = st.session_state.history[-50:]
    cols = st.columns(len(last))

    for i, pval in enumerate(last):
        if pval < alpha:
            cols[i].markdown("🟢")
        else:
            cols[i].markdown("⚪")

# ---------------------------
# P-VALUE DISTRIBUTION (KEY FEATURE)
# ---------------------------
if len(st.session_state.history) > 5:

    st.subheader("Distribution of p-values")

    fig, ax = plt.subplots()

    ax.hist(
        st.session_state.history,
        bins=20,
        range=(0, 1)
    )

    ax.axvline(alpha, linestyle="--")
    ax.set_xlim(0, 1)
    ax.set_xlabel("p-value")
    ax.set_ylabel("Frequency")
    ax.set_title("Under the null, p-values are uniform")

    st.pyplot(fig)

    st.caption(
        "Flat = no real effect. The left tail (< alpha) is just random chance."
    )

    st.write(
        "If the bars aren't flat, something real might be happening. "
        "If they are flat, you're just mining noise."
    )

# ---------------------------
# FINAL MESSAGE
# ---------------------------
if runs >= 20:
    st.warning(
        f"You've found {sig} 'significant' results.\n\n"
        "All of them came from data with NO real effect."
    )

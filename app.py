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

multi_outcomes = st.sidebar.checkbox("Try multiple outcomes (5 variables)")
stop_early = st.sidebar.checkbox("Keep running until significant")
drop_outliers = st.sidebar.checkbox("Drop outliers (|z| > 2.5)")

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

def maybe_drop_outliers(x):
    if not drop_outliers:
        return x
    z = (x - np.mean(x)) / np.std(x)
    return x[np.abs(z) < 2.5]

def run_experiment():
    def compute():
        g1, g2 = simulate_once(n)
        g1 = maybe_drop_outliers(g1)
        g2 = maybe_drop_outliers(g2)

        if len(g1) < 3 or len(g2) < 3:
            return compute()

        stat, p = ttest_ind(g1, g2, equal_var=False)
        return p, g1, g2, np.mean(g1) - np.mean(g2)

    if multi_outcomes:
        return min([compute() for _ in range(5)], key=lambda x: x[0])
    return compute()

# ---------------------------
# RUN BUTTON
# ---------------------------
fruits = ["🍒", "🍋", "🍊", "🍇", "🍉", "⭐"]

if st.button("🎲 Run Study", use_container_width=True):

    if stop_early:
        while True:
            p, g1, g2, effect = run_experiment()
            st.session_state.runs += 1
            st.session_state.history.append(p)
            if p < alpha:
                st.session_state.significant += 1
                break
    else:
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
        reel = np.random.choice(fruits, 3)
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

if st.session_state.runs > 0:
    st.subheader("Results so far")
    st.write(f"Runs: {st.session_state.runs}")
    st.write(f"Significant: {st.session_state.significant}")
    st.write(f"Proportion: {st.session_state.significant / st.session_state.runs:.3f}")

# ---------------------------
# HISTORY DOTS
# ---------------------------
if st.session_state.history:
    st.subheader("Recent runs")
    cols = st.columns(len(st.session_state.history[-50:]))

    for i, pval in enumerate(st.session_state.history[-50:]):
        cols[i].markdown("🟢" if pval < alpha else "⚪")

# ---------------------------
# HISTOGRAM (KEY FEATURE)
# ---------------------------
if len(st.session_state.history) > 5:

    st.subheader("Distribution of p-values")

    fig, ax = plt.subplots()
    ax.hist(st.session_state.history, bins=20, range=(0,1))
    ax.axvline(alpha, linestyle="--")
    ax.set_title("Under the null, p-values are uniform")

    st.pyplot(fig)

    st.caption("Flat = no real effect. Left tail is just chance.")

# ---------------------------
# FINAL MESSAGE
# ---------------------------
if st.session_state.runs >= 20:
    st.warning(
        f"You've found {st.session_state.significant} significant results.\n\n"
        "All came from pure noise."
    )

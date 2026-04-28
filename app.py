import streamlit as st
import numpy as np
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt

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
# SIDEBAR CONTROLS
# ---------------------------
st.sidebar.header("Settings")

n = st.sidebar.slider("Sample size per group", 5, 200, 30)
alpha = st.sidebar.selectbox("Significance level (alpha)", [0.05, 0.01], index=0)

st.sidebar.write("### Flexible analysis choices")
multi_outcomes = st.sidebar.checkbox("Try multiple outcomes (5 variables)")
stop_early = st.sidebar.checkbox("Keep running until significant")
drop_outliers = st.sidebar.checkbox("Drop outliers (|z| > 2.5)")

reset = st.sidebar.button("Reset")

if reset:
    st.session_state.runs = 0
    st.session_state.significant = 0
    st.session_state.history = []
    st.rerun()

# ---------------------------
# FUNCTIONS
# ---------------------------
def simulate_once(n):
    g1 = np.random.normal(0, 1, n)
    g2 = np.random.normal(0, 1, n)
    return g1, g2

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
        effect = np.mean(g1) - np.mean(g2)
        return p, g1, g2, effect

    if multi_outcomes:
        results = [compute() for _ in range(5)]
        return min(results, key=lambda x: x[0])
    else:
        return compute()

# ---------------------------
# RUN BUTTON
# ---------------------------
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

    # RESULT DISPLAY
    if p < alpha:
        st.success(f"🎉 SIGNIFICANT! p = {p:.4f}")
    else:
        st.info(f"Not significant. p = {p:.4f}")

    st.write(f"Effect size (mean difference): {effect:.3f}")

    # DATA PLOT
    fig, ax = plt.subplots()
    ax.boxplot([g1, g2], labels=["Group 1", "Group 2"])
    ax.set_title("Simulated Data (No True Difference)")
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

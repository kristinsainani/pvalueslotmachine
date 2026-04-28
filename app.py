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

alpha = st.sidebar.selectbox("Significance level (alpha)", [0.05, 0.01], index=0)

multi_outcomes = st.sidebar.checkbox("Try multiple outcomes (p-hacking)")
stop_early = st.sidebar.checkbox("Keep spinning until significant")
drop_outliers = st.sidebar.checkbox("Drop outliers")

if st.sidebar.button("Reset"):
    st.session_state.runs = 0
    st.session_state.significant = 0
    st.session_state.history = []
    st.rerun()

# ---------------------------
# FUNCTIONS
# ---------------------------
def simulate():
    n = 30
    g1 = np.random.normal(0, 1, n)
    g2 = np.random.normal(0, 1, n)
    return g1, g2

def clean(x):
    if not drop_outliers:
        return x
    z = (x - np.mean(x)) / np.std(x)
    return x[np.abs(z) < 2.5]

def one_test():
    g1, g2 = simulate()
    g1 = clean(g1)
    g2 = clean(g2)

    if len(g1) < 3 or len(g2) < 3:
        return one_test()

    _, p = ttest_ind(g1, g2, equal_var=False)
    effect = np.mean(g1) - np.mean(g2)

    return p, effect

def run_experiment():
    if multi_outcomes:
        results = [one_test() for _ in range(5)]
        return min(results, key=lambda x: x[0])
    else:
        return one_test()

def spin(is_sig):
    box = st.empty()
    symbols = ["🍒", "🍋", "🔔", "⭐", "🍊", "💎"]

    # animation
    for i in range(12):
        s = np.random.choice(symbols, 3)
        box.markdown(f"# {' '.join(s)}")
        time.sleep(0.05 + i*0.02)

    # final result
    if is_sig:
        final = ["🍒","🍒","🍒"]
    else:
        # guarantee NOT three-of-a-kind
        s1 = np.random.choice(symbols)
        s2 = np.random.choice([x for x in symbols if x != s1])
        s3 = np.random.choice(symbols)
        final = [s1, s2, s3]

    box.markdown(f"# {' '.join(final)}")

# ---------------------------
# MAIN BUTTON
# ---------------------------
if st.button("🎰 Pull the Lever", use_container_width=True):

    if stop_early:
        while True:
            p, effect = run_experiment()
            st.session_state.runs += 1
            st.session_state.history.append(p)

            if p < alpha:
                st.session_state.significant += 1
                break
    else:
        p, effect = run_experiment()
        st.session_state.runs += 1
        st.session_state.history.append(p)

        if p < alpha:
            st.session_state.significant += 1

    sig = p < alpha

    spin(sig)

    if sig:
        st.success(f"🎉 JACKPOT! p = {p:.4f}")
        st.write("There is NO real effect. This is a false positive.")
    else:
        st.info(f"No jackpot. p = {p:.4f}")

    st.write(f"Observed difference: {effect:.3f}")

# ---------------------------
# SUMMARY
# ---------------------------
st.write("---")

runs = st.session_state.runs
hits = st.session_state.significant

if runs > 0:
    st.subheader("Results so far")
    st.write(f"Spins: {runs}")
    st.write(f"Jackpots: {hits}")
    st.write(f"Rate: {hits/runs:.3f} (expected ≈ {alpha})")

# ---------------------------
# HISTORY DOTS
# ---------------------------
if st.session_state.history:
    st.subheader("Recent spins")

    last = st.session_state.history[-30:]
    cols = st.columns(len(last))

    for i, p in enumerate(last):
        if p < alpha:
            cols[i].markdown("🍒")
        else:
            cols[i].markdown("⚪")

# ---------------------------
# P-VALUE HISTOGRAM
# ---------------------------
if len(st.session_state.history) > 5:

    st.subheader("p-value distribution")

    fig, ax = plt.subplots()
    ax.hist(st.session_state.history, bins=20, range=(0,1))
    ax.axvline(alpha, linestyle="--")
    ax.set_xlim(0,1)

    st.pyplot(fig)
    st.caption("Flat = no real effect. The 'jackpots' are just chance.")

# ---------------------------
# FINAL MESSAGE
# ---------------------------
if runs >= 20:
    st.warning(
        f"You've hit {hits} jackpots.\n\nAll from pure noise."
    )

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import t

st.set_page_config(page_title="CI + p-value Explorer", layout="wide")

st.title("Confidence Intervals and p-values: Same Story, Two Languages")

st.write("""
A confidence interval and a p-value are just two ways of answering the same question:

**Does this study detect a difference?**

- If the CI excludes 0 → p < alpha → “statistically significant”
- If the CI includes 0 → p ≥ alpha → “not significant”
""")

# ---------------- Sidebar ----------------
st.sidebar.header("Settings")

confidence_level = st.sidebar.slider("Confidence level (%)", 80, 99, 95)
sample_size = st.sidebar.slider("Sample size per group", 5, 200, 30)
true_effect = st.sidebar.slider("True difference", -2.0, 2.0, 0.0, step=0.1)

mode = st.sidebar.radio("Mode", ["One study", "Many studies"])

alpha = 1 - confidence_level / 100

# ---------------- Helper function ----------------
def run_study(n, true_diff):
    g1 = np.random.normal(0, 1, n)
    g2 = np.random.normal(true_diff, 1, n)

    diff = np.mean(g2) - np.mean(g1)

    s1 = np.var(g1, ddof=1)
    s2 = np.var(g2, ddof=1)

    se = np.sqrt(s1/n + s2/n)

    df_num = (s1/n + s2/n)**2
    df_den = ((s1/n)**2/(n-1)) + ((s2/n)**2/(n-1))
    df = df_num / df_den

    t_stat = diff / se
    p_value = 2 * (1 - t.cdf(abs(t_stat), df))

    t_crit = t.ppf(1 - alpha/2, df)

    lower = diff - t_crit * se
    upper = diff + t_crit * se

    return diff, lower, upper, p_value

# ---------------- One Study ----------------
if mode == "One study":

    if st.button("Run a study"):
        diff, lower, upper, p = run_study(sample_size, true_effect)

        col1, col2 = st.columns(2)

        # Plot CI
        with col1:
            fig, ax = plt.subplots()

            ax.plot([lower, upper], [0, 0], linewidth=3)
            ax.plot(diff, 0, marker="o")

            ax.axvline(0, linestyle="--", linewidth=2, label="0 (no difference)")

            ax.set_yticks([])
            ax.set_title("Confidence Interval")
            ax.set_xlabel("Estimated difference")

            ax.legend()
            st.pyplot(fig)

        # Numbers
        with col2:
            st.subheader("Results")

            st.write(f"Estimate: {diff:.3f}")
            st.write(f"{confidence_level}% CI: [{lower:.3f}, {upper:.3f}]")
            st.write(f"p-value: {p:.4f}")

            if lower > 0 or upper < 0:
                st.success("CI excludes 0 → p < alpha → statistically significant")
            else:
                st.info("CI includes 0 → p ≥ alpha → not significant")

# ---------------- Many Studies ----------------
else:

    n_sim = st.sidebar.slider("Number of studies", 20, 300, 100)

    if st.button("Run many studies"):

        results = []

        for i in range(n_sim):
            diff, lower, upper, p = run_study(sample_size, true_effect)

            miss = (lower > 0) or (upper < 0)

            results.append((diff, lower, upper, p, miss))

        misses = sum(r[4] for r in results)
        percent = misses / n_sim * 100

        if true_effect == 0:
            st.write(f"Expected false positives ≈ {100 - confidence_level}%")
        else:
            st.write("Now we are detecting a real effect.")

        st.write(f"Observed: {misses}/{n_sim} = {percent:.1f}% significant")

        # Plot
        fig, ax = plt.subplots(figsize=(10, 10))

        for i, r in enumerate(results):
            diff, lower, upper, p, miss = r

            if miss:
                ax.plot([lower, upper], [i, i], linewidth=2.5)
                ax.plot(diff, i, marker="o")
            else:
                ax.plot([lower, upper], [i, i], linewidth=1)
                ax.plot(diff, i, marker="o", markersize=3)

        ax.axvline(0, linestyle="--", linewidth=2)

        ax.set_xlabel("Estimated difference")
        ax.set_ylabel("Study")
        ax.set_title(f"{confidence_level}% Confidence Intervals")

        ax.grid(True, alpha=0.3)

        st.pyplot(fig)

        st.subheader("What you're seeing")

        st.write("""
Each line is a study.

When the interval misses 0, the result is “statistically significant” (p < alpha).

When the true effect is 0, these are false positives — and they happen about 1 in 20 times for a 95% CI.
""")

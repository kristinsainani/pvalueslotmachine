# ---------------------------
# RUN BUTTON
# ---------------------------
fruits = ["🍒", "🍋", "🍊", "🍇", "🍉"]

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
# SLOT MACHINE + RESULTS
# ---------------------------
if 'p' in locals():

    st.write("### 🎰 Result")

    slot_placeholder = st.empty()
    final_reel = None

    # fake spinning animation
    for _ in range(10):
        reel = np.random.choice(fruits, 3, replace=True)
        slot_placeholder.markdown(
            f"<h1 style='text-align: center;'>{reel[0]} {reel[1]} {reel[2]}</h1>",
            unsafe_allow_html=True
        )
        final_reel = reel
        time.sleep(0.08)

    # final result
    if p < alpha:
        slot_placeholder.markdown(
            "<h1 style='text-align: center;'>⭐ ⭐ ⭐</h1>",
            unsafe_allow_html=True
        )
    else:
        slot_placeholder.markdown(
            f"<h1 style='text-align: center;'>{final_reel[0]} {final_reel[1]} {final_reel[2]}</h1>",
            unsafe_allow_html=True
        )

    # RESULT TEXT
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

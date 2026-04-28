"""
therapy_components.py — Mind Mesh Interactive Therapy Widgets
Stable final version: visible breathing animation, safe Thought Release, simple exercises.
"""
import streamlit as st


def _inject_css():
    # Inject every rerun so Streamlit button reruns never remove animation CSS.
    st.markdown("""
    <style>
    .tc-card {
        background: linear-gradient(135deg,#ffffff,#eef7ff);
        padding: 28px 32px;
        border-radius: 22px;
        box-shadow: 0 10px 35px rgba(14,165,233,.15);
        margin-top: 22px;
        border: 2px solid rgba(14,165,233,.18);
        animation: tcFadeUp .7s ease;
    }
    @keyframes tcFadeUp {
        from{opacity:0;transform:translateY(22px)}
        to{opacity:1;transform:translateY(0)}
    }
    @keyframes breathAnim {
        0%{transform:scale(.82)}
        50%{transform:scale(1.25)}
        100%{transform:scale(.82)}
    }
    .step-pill {
        background: #f1f5f9;
        color: #1e293b;
        border-radius: 14px;
        padding: 13px 18px;
        margin: 8px 0;
        font-size: 16px;
        font-weight: 700;
    }
    .streak-banner {
        background: linear-gradient(135deg,#7c3aed,#0ea5e9);
        color: #fff;
        border-radius: 18px;
        padding: 18px 28px;
        text-align: center;
        font-size: 20px;
        font-weight: 800;
        box-shadow: 0 8px 25px rgba(124,58,237,.35);
        margin: 18px 0;
    }
    .exercise-card {
        background: rgba(255,255,255,.9);
        border: 1px solid rgba(14,165,233,.18);
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 8px 25px rgba(14,165,233,.08);
        margin-bottom: 14px;
        color: #1e293b;
    }
    .exercise-title {
        font-size:22px;
        font-weight:900;
        color:#0ea5e9;
        margin-bottom:8px;
    }
    .exercise-sub {
        color:#64748b;
        font-size:15px;
        line-height:1.6;
    }
    </style>
    """, unsafe_allow_html=True)


def _complete_once(key: str, on_complete_callback=None, message: str = "Therapy session completed 🎉"):
    """Prevents double-counting from Streamlit reruns. Fires celebration on first completion."""
    first_time = not st.session_state.get(key, False)
    if first_time:
        st.session_state[key] = True
        if on_complete_callback:
            on_complete_callback()
        # Celebration animations
        st.balloons()
        st.snow()
    st.success(message)


# ═══════════════════════════════════════════════════════════════════
# BREATHING EXERCISE — ALWAYS VISIBLE ANIMATION, NO START SCREEN
# ═══════════════════════════════════════════════════════════════════
import time

def breathing_exercise(on_complete_callback=None, key_prefix: str = "breath"):
    _inject_css()
    done_key = f"{key_prefix}_completed"
    start_key = f"{key_prefix}_breathing_started"
    time_key = f"{key_prefix}_breathing_start_time"

    if st.session_state.get(done_key, False):
        # Clear the "therapy running" guard when done
        st.session_state["analyze_therapy_running"] = False
        st.success("Breathing session completed 🎉")
        st.markdown("""
        <div style='text-align:center;padding:18px 0 8px;'>
            <span style='font-size:52px;'>&#x1F44F;&#x1F44F;&#x1F44F;</span><br>
            <span style='font-size:22px;font-weight:900;color:#10b981;'>Amazing work! You completed the breathing session!</span>
        </div>
        """, unsafe_allow_html=True)
        def restart_breathing():
            st.session_state[done_key] = False
            st.session_state[start_key] = True
            st.session_state[time_key] = time.time()
            st.session_state["analyze_therapy_running"] = True

        st.button("🔁 Restart Breathing", key=f"{key_prefix}_restart_btn", use_container_width=True, on_click=restart_breathing)
        return

    st.markdown("### 🌬️ Guided Breathing")
    st.markdown(
        "<p style='color:#64748b'>Follow the circle.</p>",
        unsafe_allow_html=True,
    )

    if not st.session_state.get(start_key, False):
        st.session_state[start_key] = True
        st.session_state[time_key] = time.time()
        st.session_state["analyze_therapy_running"] = True
        # Don't rerun here — fall through directly to render the first frame

    elapsed = time.time() - st.session_state[time_key]
    remaining = 30 - int(elapsed)

    if remaining > 0:
        st.markdown(f"""
        <style>
        .breath-text::after {{
            content: "Inhale";
            animation: breathWords 6s infinite;
        }}
        @keyframes breathWords {{
            0% {{ content: "Inhale"; }}
            45% {{ content: "Hold"; }}
            60% {{ content: "Exhale"; }}
            100% {{ content: "Exhale"; }}
        }}
        </style>
        <div class='tc-card' style='text-align:center;'>
            <div style="
                margin: 24px auto;
                width: 175px;
                height: 175px;
                border-radius: 50%;
                background: radial-gradient(circle, #8b5cf6, #0ea5e9, #14b8a6);
                display: flex;
                align-items: center;
                justify-content: center;
                color: #ffffff;
                font-size: 22px;
                font-weight: 900;
                box-shadow: 0 0 50px rgba(14,165,233,.55);
                animation: breathAnim 6s infinite ease-in-out;
            "><span class="breath-text"></span></div>
            <h2 style='color:#0ea5e9;margin:10px 0;'>Inhale · Hold · Exhale</h2>
            <h1 style='color:#8b5cf6;font-size:48px;'>{remaining}</h1>
            <p style='color:#64748b'>seconds remaining</p>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(1)
        st.rerun()
    else:
        st.session_state[done_key] = True
        st.session_state[start_key] = False
        st.session_state["analyze_therapy_running"] = False
        if on_complete_callback:
            on_complete_callback()
        # Fire celebration
        st.balloons()
        st.snow()
        st.rerun()


# ═══════════════════════════════════════════════════════════════════
# GROUNDING
# ═══════════════════════════════════════════════════════════════════
def anxiety_grounding(on_complete_callback=None, key_prefix: str = "grounding"):
    _inject_css()
    done_key = f"{key_prefix}_completed"

    st.markdown("### 🌱 5-4-3-2-1 Grounding")
    st.markdown(
        "<p style='color:#64748b'>Fill the boxes to bring your attention back to the present moment.</p>",
        unsafe_allow_html=True,
    )

    items = [
        ("see", "👀 5 things you can see", 5),
        ("touch", "✋ 4 things you can touch", 4),
        ("hear", "👂 3 things you can hear", 3),
        ("smell", "🌸 2 things you can smell", 2),
        ("taste", "🍬 1 thing you can taste", 1),
    ]

    values = []
    with st.form(f"{key_prefix}_form"):
        for short, label, count in items:
            st.markdown(f"<div class='step-pill'>{label}</div>", unsafe_allow_html=True)
            for i in range(count):
                values.append(
                    st.text_input(
                        f"{short}_{i}",
                        placeholder="Type here...",
                        label_visibility="collapsed",
                        key=f"{key_prefix}_{short}_{i}",
                    )
                )
        submitted = st.form_submit_button("✅ Complete Grounding", use_container_width=True)

    if submitted:
        filled = sum(1 for v in values if str(v).strip())
        if filled == len(values):
            st.balloons()
            _complete_once(done_key, on_complete_callback, "Grounding exercise completed 🌱")
        else:
            st.warning(f"Please fill all boxes to complete the exercise. Filled {filled}/{len(values)}.")


# ═══════════════════════════════════════════════════════════════════
# SMALL STEPS / DEPRESSION SUPPORT
# ═══════════════════════════════════════════════════════════════════
def depression_checklist(on_complete_callback=None, key_prefix: str = "small_steps"):
    _inject_css()
    done_key = f"{key_prefix}_completed"

    st.markdown("### 🌤️ Small Steps Challenge")
    st.markdown(
        "<p style='color:#64748b'>Choose at least one small action. Small steps count.</p>",
        unsafe_allow_html=True,
    )

    tasks = [
        "💧 Drink one glass of water",
        "🪟 Open a window for fresh air",
        "🚶 Take a 5-minute walk",
        "📩 Message one trusted person",
        "📝 Write one thing you survived today",
    ]

    done = 0
    for i, task in enumerate(tasks):
        if st.checkbox(task, key=f"{key_prefix}_task_{i}"):
            done += 1

    if done > 0:
        st.info(f"You selected {done} small step(s). That matters 💙")

    if st.button("✅ Complete Small Steps Session", key=f"{key_prefix}_complete", use_container_width=True):
        if done > 0:
            _complete_once(done_key, on_complete_callback, "Small steps session completed 🌤️")
            st.markdown("""
            <div style='text-align:center;padding:18px 0 8px;'>
                <span style='font-size:52px;'>&#x1F44F;&#x1F44F;&#x1F44F;</span><br>
                <span style='font-size:22px;font-weight:900;color:#10b981;'>Well done! Every small step matters 💪</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Please select at least one small step before completing.")


# ═══════════════════════════════════════════════════════════════════
# THOUGHT RELEASE — SAFE VERSION, NO SESSION_STATE MODIFICATION AFTER WIDGET
# ═══════════════════════════════════════════════════════════════════
def thought_release(on_complete_callback=None, key_prefix: str = "thought_release"):
    _inject_css()
    done_key = f"{key_prefix}_completed"
    text_key = f"{key_prefix}_text"
    just_released_key = f"{key_prefix}_just_released"

    if st.session_state.get(just_released_key, False):
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #ecfdf5, #f0f9ff);
            border-radius: 20px;
            padding: 28px 32px;
            border-left: 6px solid #10b981;
            box-shadow: 0 8px 25px rgba(16,185,129,0.15);
            text-align: center;
            margin-bottom: 16px;
        '>
            <div style='font-size:52px;margin-bottom:10px;'>🕊️✨</div>
            <p style='font-size:22px;font-weight:900;color:#065f46;margin:0 0 8px;'>
                That took courage. Well done! 💙
            </p>
            <p style='font-size:16px;color:#047857;margin:0;'>
                Letting your thoughts out is the first step toward peace.<br>
                You are stronger than you know.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Write Another Thought", key=f"{key_prefix}_another_btn", use_container_width=True):
            st.session_state[just_released_key] = False
            if text_key in st.session_state:
                st.session_state[text_key] = ""
            st.rerun()
    else:
        st.markdown("### ✍️ Thought Release")
        st.markdown(
            "<p style='color:#64748b'>Write what is on your mind. It is a safe space — not stored by default.</p>",
            unsafe_allow_html=True,
        )

        txt = st.text_area(
            "Write your thoughts",
            height=140,
            placeholder="Type here... pour it all out.",
            key=text_key,
        )
        if st.button("💙 Release Thoughts", use_container_width=True, key=f"{key_prefix}_btn"):
            if txt.strip():
                st.session_state[just_released_key] = True
                _complete_once(done_key, on_complete_callback, "Your thoughts were released privately 💙")
                st.rerun()
            else:
                st.warning("Write something first, even one line is enough.")


# ═══════════════════════════════════════════════════════════════════
# QUICK STRETCH
# ═══════════════════════════════════════════════════════════════════
def quick_stretch(on_complete_callback=None, key_prefix: str = "quick_stretch"):
    _inject_css()
    done_key = f"{key_prefix}_completed"

    st.markdown("### 🧘 Quick Stretch")
    st.markdown(
        "<p style='color:#64748b'>Try these gentle movements. Mark done when completed.</p>",
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div class='exercise-card'>🧍 <b>Neck roll:</b> Slowly roll your neck twice.</div>
    <div class='exercise-card'>💪 <b>Shoulder stretch:</b> Lift shoulders, hold, release.</div>
    <div class='exercise-card'>🧘 <b>Deep breathing pose:</b> Sit straight and breathe deeply.</div>
    <div class='exercise-card'>🌿 <b>Forward stretch:</b> Gently lean forward while seated.</div>
    """, unsafe_allow_html=True)

    if st.button("✅ I Completed Quick Stretch", key=f"{key_prefix}_btn", use_container_width=True):
        _complete_once(done_key, on_complete_callback, "Quick stretch completed 🌤️")
        st.markdown("""
        <div style='text-align:center;padding:18px 0 8px;'>
            <span style='font-size:52px;'>&#x1F44F;&#x1F44F;&#x1F44F;</span><br>
            <span style='font-size:22px;font-weight:900;color:#10b981;'>Great job! Your body thanks you 🧘</span>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# THOUGHT REFRAME
# ═══════════════════════════════════════════════════════════════════
def thought_reframe(on_complete_callback=None, key_prefix: str = "thought_reframe"):
    _inject_css()
    done_key = f"{key_prefix}_completed"
    
    st.markdown("### 🧠 Thought Reframe")
    st.markdown(
        "<p style='color:#64748b'>Reframing helps us see a difficult thought from a more balanced perspective.</p>",
        unsafe_allow_html=True,
    )
    
    thought = st.text_input("Write one negative thought", key=f"{key_prefix}_input", placeholder="e.g., I always fail at this")
    
    if st.button("🔄 Reframe Thought", key=f"{key_prefix}_reframe_btn", use_container_width=True):
        if thought.strip():
            st.markdown("---")
            with st.spinner("Reframing your thought..."):
                from groq_helper import generate_advice
                prompt = (
                    f"The user has this negative thought: '{thought}'. "
                    "Please reframe this thought in a positive, balanced way and provide a brief motivating message. "
                    "Write 2-3 sentences. Do not use generic headings or labels. Speak directly to the user."
                )
                try:
                    reframe = generate_advice(prompt)
                except Exception:
                    reframe = "Sometimes things don't work out as expected, but you are stronger than your negative thoughts. Keep pushing forward and be kind to yourself."
                
                st.info(f"✨ **Positive Reframe:**\n\n{reframe}")
            
            st.session_state[f"{key_prefix}_show_complete"] = True
        else:
            st.warning("Please write a thought to reframe.")
            
    if st.session_state.get(f"{key_prefix}_show_complete", False):
        if st.button("✅ Mark Reframe Completed", key=f"{key_prefix}_complete_btn", use_container_width=True):
            _complete_once(done_key, on_complete_callback, "Thought reframe completed 🧠")
            st.session_state[f"{key_prefix}_show_complete"] = False
            input_key = f"{key_prefix}_input"
            if input_key in st.session_state:
                st.session_state[input_key] = ""
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
# GAMIFICATION BANNER
# ═══════════════════════════════════════════════════════════════════
def gamification_banner(logged_in: bool, streak: int = 0, session_count: int = 0):
    _inject_css()
    if logged_in:
        day_word = "Day" if streak == 1 else "Days"
        st.markdown(
            f"<div class='streak-banner'>🔥 {streak} {day_word} Streak — You showed up today 💙</div>",
            unsafe_allow_html=True,
        )
    elif session_count > 0:
        st.markdown(
            f"<div class='streak-banner'>✨ You completed {session_count} exercise(s) this session!</div>",
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════
# DISPATCHER AFTER PREDICTION
# ═══════════════════════════════════════════════════════════════════
def show_therapy(prediction: str, on_complete_callback=None):
    """Dispatch the correct therapy widget. Header/separator are rendered by the caller."""
    _inject_css()
    # NOTE: do NOT add st.markdown('---') or st.subheader here.
    # The dashboard controls the heading to avoid double-rendering during breathing reruns.

    if prediction == "Stress":
        breathing_exercise(on_complete_callback, key_prefix="stress_breathing")
    elif prediction == "Anxiety":
        anxiety_grounding(on_complete_callback, key_prefix="anxiety_grounding")
    elif prediction == "Depression":
        depression_checklist(on_complete_callback, key_prefix="depression_steps")
    else:
        st.markdown("""
        <div class='tc-card' style='text-align:center'>
            <div style='font-size:56px'>😊</div>
            <h2 style='color:#10b981'>You seem emotionally stable!</h2>
            <p style='color:#475569'>Keep nurturing yourself with small wellness habits.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✅ Complete Wellness Check", key="normal_wellness_complete", use_container_width=True):
            _complete_once("normal_wellness_completed", on_complete_callback, "Wellness check completed 😊")


# ═══════════════════════════════════════════════════════════════════
# EXERCISES PAGE
# ═══════════════════════════════════════════════════════════════════
def show_exercises_page(on_complete_callback=None):
    _inject_css()
    st.markdown("<h1 style='color:#0ea5e9 !important;'>🌿 Exercises</h1>", unsafe_allow_html=True)
    st.markdown("Simple calming exercises you can use anytime — no analysis required.")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌬️ Breathing",
        "🌱 Grounding",
        "✍️ Release",
        "🧘 Stretch",
        "🧠 Reframe",
    ])
    with tab1:
        breathing_exercise(on_complete_callback, key_prefix="page_breathing")
    with tab2:
        anxiety_grounding(on_complete_callback, key_prefix="page_grounding")
    with tab3:
        thought_release(on_complete_callback, key_prefix="page_thought_release")
    with tab4:
        quick_stretch(on_complete_callback, key_prefix="page_quick_stretch")
    with tab5:
        thought_reframe(on_complete_callback, key_prefix="page_thought_reframe")

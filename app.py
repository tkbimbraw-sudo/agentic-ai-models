import os
import streamlit as st
from langchain_groq import ChatGroq

st.set_page_config(page_title="Blood Work Analyzer", layout="wide")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,  # slight creativity for better diet suggestions
    api_key=os.environ.get("GROQ_API_KEY"),
    max_tokens=4096  # ✅ allow much longer responses
)

st.markdown("""
<style>
.scroll-box {
    height: 280px;
    overflow-y: auto;
    padding: 14px 18px;
    border: 1px solid #555;
    border-radius: 8px;
    background-color: #1e1e1e;
    font-size: 0.95rem;
    line-height: 1.8;
}
.scroll-box p, .scroll-box li {
    color: #f5f5f5;  /* ✅ brighter text */
}
.scroll-box h3, .scroll-box strong, .scroll-box b {
    color: #ffffff;
    font-size: 1rem;
}
.scroll-box ul {
    padding-left: 18px;
}
.scroll-box li {
    margin-bottom: 6px;
    color: #f0f0f0;  /* ✅ brighter list items */
}
.section-label {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 6px;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

st.title("🩸 Blood Work Analyzer")

left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("Blood Work Report")
    blood_report = st.text_area(
        label="Paste your report below",
        height=500,
        placeholder="Paste your blood work report here...",
        label_visibility="collapsed"
    )
    analyze_clicked = st.button(
        "Analyze", type="primary", use_container_width=True)

with right_col:
    st.subheader("Health Summary")
    health_box = st.empty()
    health_box.markdown('<div class="scroll-box"></div>', unsafe_allow_html=True)

    st.subheader("Suggested Diet Plan")
    diet_box = st.empty()
    diet_box.markdown('<div class="scroll-box"></div>', unsafe_allow_html=True)

if analyze_clicked:
    if not blood_report.strip():
        with left_col:
            st.warning("Please paste a blood work report before analyzing.")
    else:
        with st.spinner("Analyzing your blood work..."):

            # Stage 1: Extract and flag abnormal values
            extraction_prompt = f"""
You are a senior medical data extraction specialist.
From the blood report below, extract EVERY test value and classify each as HIGH, LOW, or NORMAL
based on the reference ranges in the report.

For each abnormal value (HIGH or LOW), also briefly explain what that marker indicates about health.

Format your response as:
- Test Name: value | Status: HIGH/LOW/NORMAL | Reference: range | Implication: brief explanation

Be thorough — do not skip any test. If a value is borderline, mention it.

Blood Report:
{blood_report}
"""
            extraction_response = llm.invoke(extraction_prompt)
            extracted_values = extraction_response.content

            # Stage 2: Detailed health summary + Indian diet plan
            diet_prompt = f"""
You are an experienced clinical nutritionist and health advisor specializing in Indian dietary habits.
Based on the blood work analysis below, provide a DETAILED response in two clearly separated sections.

SECTION 1 - HEALTH SUMMARY:
- Write 8-10 lines explaining the patient's overall health condition in simple, non-technical language
- Highlight which areas of health need attention (e.g. liver, kidney, thyroid, iron levels, cholesterol)
- Mention which values are concerning and what symptoms the patient might be experiencing
- End with an encouraging note about what improvements are possible with diet and lifestyle

SECTION 2 - INDIAN DIET PLAN:
Provide a comprehensive Indian diet plan with the following subsections:

**Foods to Eat More Of:**
List at least 8-10 specific Indian foods with a brief reason for each
(e.g. dal, palak, methi, amla, haldi doodh, ragi, etc.)

**Foods to Strictly Avoid:**
List at least 6-8 foods to avoid with a reason for each
(e.g. maida, fried snacks, packaged foods, excess chai, etc.)

**Sample Daily Meal Plan:**
- Morning (empty stomach):
- Breakfast:
- Mid-morning snack:
- Lunch:
- Evening snack:
- Dinner:
- Before bed:

**Lifestyle Tips:**
Give 4-5 practical lifestyle tips based on the blood work findings
(e.g. sleep, exercise, hydration, stress management)

Be specific, practical, and use commonly available Indian ingredients.

Blood Work Analysis:
{extracted_values}
"""
            diet_response = llm.invoke(diet_prompt)
            full_response = diet_response.content

        # Split response into two sections
        if "SECTION 2" in full_response:
            parts = full_response.split("SECTION 2")
            health_summary = parts[0].replace(
                "SECTION 1 - HEALTH SUMMARY:", "").replace("SECTION 1", "").strip()
            diet_plan = ("SECTION 2" + parts[1]).replace(
                "SECTION 2 - INDIAN DIET PLAN:", "").replace("SECTION 2", "").strip()
        else:
            health_summary = full_response
            diet_plan = ""

        # Convert newlines to HTML for proper rendering
        health_summary_html = health_summary.replace("\n", "<br>")
        diet_plan_html = (diet_plan if diet_plan else full_response).replace("\n", "<br>")

        health_box.markdown(
            f'<div class="scroll-box">{health_summary_html}</div>',
            unsafe_allow_html=True
        )
        diet_box.markdown(
            f'<div class="scroll-box">{diet_plan_html}</div>',
            unsafe_allow_html=True
        )

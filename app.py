import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

from datetime import date, timedelta

from job_recommender import recommend_jobs


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="JobLens",
    page_icon="📊",
    layout="wide"
)

st.title("📊 JobLens")
st.subheader("AI Job Market & Skill Gap Analyzer")

st.write(
    "Explore job market trends, analyse your skills "
    "and discover relevant job opportunities."
)


# ==================================================
# 2. DATABASE CONNECTION AND TABLE SETUP
# ==================================================

conn = sqlite3.connect("joblens.db")

jobs = pd.read_sql_query("SELECT * FROM jobs", conn)

naukri_jobs = pd.read_sql_query(
    "SELECT * FROM naukri_jobs", conn
)

naukri_skills = pd.read_sql_query(
    "SELECT * FROM naukri_skills", conn
)

# Create a separate table for weekly learning tasks.
# Existing job-market tables are not modified.

conn.execute("""
    CREATE TABLE IF NOT EXISTS weekly_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        week_start TEXT NOT NULL,
        skill TEXT NOT NULL,
        task TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()
conn.close()


# ==================================================
# 3. JOB MARKET DASHBOARD
# ==================================================

st.header("📈 Job Market Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Original Job Listings", len(jobs))
col2.metric("Naukri Job Listings", len(naukri_jobs))

col3.metric(
    "Unique Extracted Skills",
    naukri_skills["skill"].nunique()
)

st.divider()


# ==================================================
# 4. JOB LISTINGS EXPLORER
# ==================================================

st.subheader("Explore Job Listings")

locations = ["All"] + sorted(
    jobs["location"].dropna().unique().tolist()
)

selected_location = st.selectbox(
    "Choose a location",
    locations
)

if selected_location == "All":
    filtered_jobs = jobs
else:
    filtered_jobs = jobs[
        jobs["location"] == selected_location
    ]

st.dataframe(filtered_jobs, width="stretch")

st.divider()


# ==================================================
# 5. TOP STATES BY JOB LISTINGS
# ==================================================

st.subheader("Top 10 States by Job Listings")

valid_states = jobs[
    (jobs["state"] != "Not Provided") &
    (jobs["state"] != "India")
]

top_states = valid_states["state"].value_counts().head(10)

fig1, ax1 = plt.subplots(figsize=(10, 5))

top_states.plot(kind="bar", ax=ax1)

ax1.set_xlabel("State")
ax1.set_ylabel("Number of Jobs")
ax1.set_title("Job Listings by State")

plt.xticks(rotation=45, ha="right")
plt.tight_layout()

st.pyplot(fig1)
plt.close(fig1)

st.divider()


# ==================================================
# 6. AVERAGE SALARY BY STATE
# ==================================================

st.subheader("Average Monthly Salary by State")

salary_data = jobs[
    (jobs["state"] != "Not Provided") &
    (jobs["state"] != "India")
]

state_salary = (
    salary_data.groupby("state")["monthly_salary"]
    .mean()
    .dropna()
    .sort_values(ascending=False)
    .head(10)
)

fig2, ax2 = plt.subplots(figsize=(10, 5))

state_salary.plot(kind="bar", ax=ax2)

ax2.set_xlabel("State")
ax2.set_ylabel("Average Monthly Salary (₹)")
ax2.set_title("Average Monthly Salary by State")

plt.xticks(rotation=45, ha="right")
plt.tight_layout()

st.pyplot(fig2)
plt.close(fig2)

st.divider()


# ==================================================
# 7. MOST COMMON JOB TITLES
# ==================================================

st.subheader("Most Common Job Titles")

top_titles = jobs["job_title"].value_counts().head(10)

fig3, ax3 = plt.subplots(figsize=(10, 5))

top_titles.plot(kind="bar", ax=ax3)

ax3.set_xlabel("Job Title")
ax3.set_ylabel("Number of Listings")
ax3.set_title("Most Common Job Roles")

plt.xticks(rotation=45, ha="right")
plt.tight_layout()

st.pyplot(fig3)
plt.close(fig3)


# ==================================================
# 8. AI SKILL GAP ANALYZER
# ==================================================

st.divider()

st.header("🤖 AI Skill Gap Analyzer")

st.write(
    "Select your target job role and enter your "
    "current skills to discover what you need to learn."
)

st.warning(
    "The Naukri dataset contains historical listings "
    "from around 2016. Results demonstrate skill matching "
    "and should not be treated as current hiring trends."
)


# ==================================================
# 9. SKILL CLASSIFICATION
# ==================================================

technical_skills = {
    "python", "sql", "excel", "power bi", "tableau",
    "r", "pandas", "numpy", "mysql", "postgresql",
    "java", "c++", "c", "javascript", "html", "css",
    "git", "github", "aws", "azure", "google cloud",
    "hadoop", "spark", "pyspark", "mongodb", "oracle",
    "sas", "spss", "tensorflow", "pytorch",
    "scikit-learn", "machine learning", "deep learning",
    "artificial intelligence", "nlp", "etl",
    "data warehousing", "database management",
    "computer vision", "linux", "powerpoint"
}

analytical_skills = {
    "statistics", "data analysis", "data visualization",
    "data mining", "time series analysis",
    "predictive modelling", "predictive modeling",
    "business analysis"
}


# ==================================================
# 10. SELECT TARGET JOB ROLE
# ==================================================

role_counts = naukri_jobs["jobtitle"].value_counts()

popular_roles = sorted(
    role_counts[role_counts >= 5].index.tolist()
)

selected_role = st.selectbox(
    "Choose your target job role",
    ["Select a role"] + popular_roles,
    key="target_role"
)


# ==================================================
# 11. ENTER CANDIDATE SKILLS
# ==================================================

candidate_input = st.text_input(
    "Enter your current skills separated by commas",
    placeholder="Python, SQL, Excel, Pandas"
)

analyse_button = st.button(
    "Analyse My Skills",
    type="primary"
)


# ==================================================
# 12. SKILL GAP ANALYSIS
# ==================================================

if analyse_button:

    if selected_role == "Select a role":

        st.warning("Please select a job role.")

    elif not candidate_input.strip():

        st.warning("Please enter your current skills.")

    else:

        candidate_skills = {
            skill.strip().lower()
            for skill in candidate_input.split(",")
            if skill.strip()
        }

        matching_jobs = naukri_jobs[
            naukri_jobs["jobtitle"] == selected_role
        ]

        matching_job_ids = matching_jobs["jobid"].unique()

        required_skills_data = naukri_skills[
            naukri_skills["jobid"].isin(matching_job_ids)
        ].copy()

        required_skills_data["skill"] = (
            required_skills_data["skill"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        allowed_skills = technical_skills | analytical_skills

        required_skills_data = required_skills_data[
            required_skills_data["skill"].isin(allowed_skills)
        ]

        skill_demand = (
            required_skills_data
            .groupby("skill")["jobid"]
            .nunique()
            .sort_values(ascending=False)
        )

        top_required_skills = skill_demand.head(10)

        required_skills = set(top_required_skills.index)

        if not required_skills:

            st.warning(
                "No recognised technical or analytical skills "
                "were found for this role in the dataset."
            )

        else:

            matched_skills = candidate_skills & required_skills

            missing_skills = required_skills - candidate_skills

            match_percentage = (
                len(matched_skills) / len(required_skills)
            ) * 100

            st.divider()

            st.subheader("Your Skill Gap Report")

            st.metric(
                "Skill Match Percentage",
                f"{match_percentage:.1f}%"
            )

            st.progress(match_percentage / 100)

            st.write(
                f"Job listings analysed: {len(matching_jobs)}"
            )

            col4, col5 = st.columns(2)

            with col4:

                st.success("Skills You Already Have")

                if matched_skills:

                    for skill in sorted(matched_skills):
                        st.write("✅", skill.title())

                else:

                    st.write("No matching skills found.")

            with col5:

                st.error("Skills You Need to Learn")

                if missing_skills:

                    for skill in sorted(missing_skills):
                        st.write("❌", skill.title())

                else:

                    st.write("You have all the listed skills!")

            st.divider()

            st.subheader("Most Demanded Skills for This Role")

            demand_display = (
                top_required_skills
                .rename_axis("Skill")
                .reset_index(name="Number of Job Listings")
            )

            demand_display["Category"] = (
                demand_display["Skill"].apply(
                    lambda skill: (
                        "Technical"
                        if skill in technical_skills
                        else "Analytical"
                    )
                )
            )

            st.dataframe(
                demand_display,
                width="stretch"
            )


            # ==================================================
            # 13. LEARNING RECOMMENDATIONS
            # ==================================================

            learning_resources = {
                "python": "https://www.w3schools.com/python/",
                "sql": "https://www.w3schools.com/sql/",
                "excel": "https://support.microsoft.com/excel",
                "power bi": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi/",
                "tableau": "https://www.tableau.com/learn/training",
                "pandas": "https://pandas.pydata.org/docs/getting_started/",
                "numpy": "https://numpy.org/learn/",
                "machine learning": "https://www.kaggle.com/learn/intro-to-machine-learning",
                "statistics": "https://www.khanacademy.org/math/statistics-probability",
                "git": "https://git-scm.com/doc",
                "mysql": "https://dev.mysql.com/doc/"
            }

            st.divider()

            st.subheader("📚 Learning Recommendations")

            if missing_skills:

                for skill in sorted(missing_skills):

                    st.write(f"**{skill.title()}**")

                    resource = learning_resources.get(
                        skill,
                        "https://www.coursera.org/"
                    )

                    st.markdown(
                        f"[Start Learning]({resource})"
                    )

            else:

                st.success(
                    "You match all the top listed skills!"
                )


            # ==================================================
            # 14. 90-DAY CAREER ROADMAP GENERATOR
            # ==================================================

            st.divider()

            st.header("🗺️ Your 90-Day Career Roadmap")

            st.write(
                "A personalised learning roadmap based "
                "on your missing skills."
            )

            if missing_skills:

                learning_order = [
                    "excel",
                    "sql",
                    "statistics",
                    "python",
                    "pandas",
                    "numpy",
                    "power bi",
                    "tableau",
                    "data visualization",
                    "machine learning"
                ]

                ordered_missing = sorted(
                    missing_skills,
                    key=lambda skill: (
                        learning_order.index(skill)
                        if skill in learning_order
                        else 999
                    )
                )

                phase_1 = ordered_missing[:2]
                phase_2 = ordered_missing[2:4]
                phase_3 = ordered_missing[4:]

                with st.expander(
                    "📘 Days 1–30: Build Your Foundation",
                    expanded=True
                ):

                    st.write(
                        "Focus on understanding the fundamentals."
                    )

                    if phase_1:

                        for skill in phase_1:
                            st.write("📌", skill.title())

                    else:

                        st.write(
                            "Your foundation skills are already covered."
                        )

                    st.write(
                        "**Practice:** Complete small exercises "
                        "and solve beginner-level problems."
                    )

                with st.expander(
                    "📊 Days 31–60: Develop Analytical Skills"
                ):

                    st.write(
                        "Apply your knowledge to real-world data."
                    )

                    if phase_2:

                        for skill in phase_2:
                            st.write("📌", skill.title())

                    else:

                        st.write(
                            "Explore intermediate analytics techniques."
                        )

                    st.write(
                        "**Practice:** Analyse datasets and "
                        "create reports and visualisations."
                    )

                with st.expander(
                    "🚀 Days 61–90: Become Job Ready"
                ):

                    st.write(
                        "Build practical projects to demonstrate "
                        "your skills."
                    )

                    if phase_3:

                        for skill in phase_3:
                            st.write("📌", skill.title())

                    st.write("**Portfolio Projects:**")

                    st.write(
                        "1. Sales Data Analysis using Python and SQL"
                    )

                    st.write(
                        "2. Interactive Power BI Dashboard"
                    )

                    st.write(
                        "3. Exploratory Data Analysis Project"
                    )

                    st.write(
                        "**Final Goal:** Upload your projects "
                        "to GitHub and prepare your resume."
                    )

                st.success(
                    "Your 90-day learning roadmap is ready!"
                )

            else:

                st.success(
                    "You have no missing skills in the current "
                    "comparison. Focus on advanced projects."
                )


            # ==================================================
            # 15. SKILL MATCH DISCLAIMER
            # ==================================================

            st.caption(
                "The match percentage measures the share of "
                "the role's top extracted skills that you have. "
                "It is not a probability of getting hired."
            )


# ==================================================
# 16. AI JOB RECOMMENDATION SYSTEM
# ==================================================

st.divider()

st.header("🤖 AI Job Recommendation System")

st.write(
    "Enter your skills and professional profile. "
    "JobLens will find job listings most similar to your profile."
)

candidate_skills_input = st.text_area(
    "Enter Your Skills",
    placeholder="Python, SQL, Excel, Power BI, Pandas"
)

candidate_profile = st.text_area(
    "Describe Your Profile",
    placeholder=(
        "I am a BCA student interested in Data Analytics. "
        "I know Python, SQL and Excel. I am looking for "
        "entry-level Data Analyst opportunities."
    )
)

if st.button("Find Recommended Jobs"):

    if not candidate_skills_input.strip() and not candidate_profile.strip():

        st.warning("Please enter your skills or profile.")

    else:

        profile_text = (
            candidate_skills_input + " " + candidate_profile
        )

        with st.spinner("Finding relevant jobs..."):

            recommendations = recommend_jobs(
                profile_text,
                top_n=10
            )

        st.subheader("Your Top 10 Job Recommendations")

        if recommendations.empty:

            st.info("No matching jobs found.")

        else:

            for _, row in recommendations.iterrows():

                with st.container(border=True):

                    st.markdown(f"### {row['jobtitle']}")

                    st.write("**Company:**", row["company"])

                    st.write(
                        "**Location:**",
                        row["joblocation_address"]
                    )

                    score = float(row["similarity_score"])

                    st.progress(
                        max(0.0, min(1.0, score))
                    )

                    st.write(
                        f"Text Similarity: {score * 100:.2f}%"
                    )

        st.caption(
            "Similarity scores measure text similarity, "
            "not hiring probability or verified skill coverage."
        )


# ==================================================
# 17. WEEKLY LEARNING TARGETS AND PROGRESS TRACKER
# ==================================================

st.divider()

st.header("🎯 Weekly Learning Targets & Progress Tracker")

st.write(
    "Create weekly learning goals, add tasks and track "
    "your progress. Your progress is saved in the database."
)


# --------------------------------------------------
# Calculate the current week's Monday
# --------------------------------------------------

today = date.today()

current_week_start = today - timedelta(days=today.weekday())

current_week_end = current_week_start + timedelta(days=6)

st.info(
    f"Current learning week: "
    f"{current_week_start.strftime('%d %b %Y')} – "
    f"{current_week_end.strftime('%d %b %Y')}"
)


# --------------------------------------------------
# Add a new learning task
# --------------------------------------------------

st.subheader("➕ Add a Weekly Learning Task")

with st.form("add_weekly_task_form", clear_on_submit=True):

    task_skill = st.selectbox(
        "Choose a skill",
        [
            "Python",
            "SQL",
            "Excel",
            "Power BI",
            "Statistics",
            "Pandas",
            "NumPy",
            "Tableau",
            "Data Analysis",
            "Data Visualization",
            "Machine Learning",
            "Git and GitHub",
            "Portfolio Project",
            "Other"
        ]
    )

    custom_skill = ""

    if task_skill == "Other":

        custom_skill = st.text_input(
            "Enter your skill name"
        )

    task_description = st.text_input(
        "Describe your learning task",
        placeholder="Example: Complete 3 SQL practice exercises"
    )

    add_task_button = st.form_submit_button(
        "Add Weekly Task",
        type="primary"
    )

    if add_task_button:

        final_skill = (
            custom_skill.strip()
            if task_skill == "Other"
            else task_skill
        )

        if not final_skill:

            st.error("Please enter a skill name.")

        elif not task_description.strip():

            st.error("Please describe your learning task.")

        else:

            task_conn = sqlite3.connect("joblens.db")

            task_conn.execute(
                """
                INSERT INTO weekly_tasks
                (week_start, skill, task, completed)
                VALUES (?, ?, ?, 0)
                """,
                (
                    current_week_start.isoformat(),
                    final_skill,
                    task_description.strip()
                )
            )

            task_conn.commit()
            task_conn.close()

            st.success("Your weekly learning task has been saved!")

            st.rerun()


# --------------------------------------------------
# Load current week's tasks
# --------------------------------------------------

task_conn = sqlite3.connect("joblens.db")

weekly_tasks = pd.read_sql_query(
    """
    SELECT *
    FROM weekly_tasks
    WHERE week_start = ?
    ORDER BY id DESC
    """,
    task_conn,
    params=(current_week_start.isoformat(),)
)

task_conn.close()


# --------------------------------------------------
# Weekly progress calculations
# --------------------------------------------------

st.divider()

st.subheader("📊 Your Weekly Progress")

total_tasks = len(weekly_tasks)

if total_tasks > 0:

    completed_tasks = int(
        weekly_tasks["completed"].sum()
    )

    pending_tasks = total_tasks - completed_tasks

    progress_percentage = (
        completed_tasks / total_tasks
    ) * 100

else:

    completed_tasks = 0
    pending_tasks = 0
    progress_percentage = 0


progress_col1, progress_col2, progress_col3 = st.columns(3)

progress_col1.metric(
    "Total Tasks",
    total_tasks
)

progress_col2.metric(
    "Completed Tasks",
    completed_tasks
)

progress_col3.metric(
    "Pending Tasks",
    pending_tasks
)

st.progress(progress_percentage / 100)

st.write(
    f"**Weekly Completion: {progress_percentage:.1f}%**"
)


# --------------------------------------------------
# Display tasks and completion controls
# --------------------------------------------------

st.subheader("📝 Your Weekly Task Checklist")

if total_tasks == 0:

    st.info(
        "You haven't added any tasks for this week yet. "
        "Add your first learning task above!"
    )

else:

    for _, task_row in weekly_tasks.iterrows():

        task_id = int(task_row["id"])

        task_is_completed = bool(task_row["completed"])

        with st.container(border=True):

            task_col1, task_col2 = st.columns([5, 1])

            with task_col1:

                st.write(f"**Skill:** {task_row['skill']}")

                if task_is_completed:

                    st.markdown(
                        f"~~{task_row['task']}~~"
                    )

                    st.success("Completed")

                else:

                    st.write(task_row["task"])

                    st.warning("Pending")

            with task_col2:

                if task_is_completed:

                    if st.button(
                        "Undo",
                        key=f"undo_{task_id}"
                    ):

                        update_conn = sqlite3.connect("joblens.db")

                        update_conn.execute(
                            """
                            UPDATE weekly_tasks
                            SET completed = 0
                            WHERE id = ?
                            """,
                            (task_id,)
                        )

                        update_conn.commit()
                        update_conn.close()

                        st.rerun()

                else:

                    if st.button(
                        "Complete",
                        key=f"complete_{task_id}",
                        type="primary"
                    ):

                        update_conn = sqlite3.connect("joblens.db")

                        update_conn.execute(
                            """
                            UPDATE weekly_tasks
                            SET completed = 1
                            WHERE id = ?
                            """,
                            (task_id,)
                        )

                        update_conn.commit()
                        update_conn.close()

                        st.rerun()

                if st.button(
                    "Delete",
                    key=f"delete_{task_id}"
                ):

                    delete_conn = sqlite3.connect("joblens.db")

                    delete_conn.execute(
                        """
                        DELETE FROM weekly_tasks
                        WHERE id = ?
                        """,
                        (task_id,)
                    )

                    delete_conn.commit()
                    delete_conn.close()

                    st.rerun()


# --------------------------------------------------
# Weekly completion message
# --------------------------------------------------

if total_tasks > 0:

    if progress_percentage == 100:

        st.balloons()

        st.success(
            "🎉 Amazing! You completed all your learning "
            "tasks for this week!"
        )

    elif progress_percentage >= 50:

        st.success(
            "Great progress! Keep going and finish your "
            "remaining learning tasks."
        )

    else:

        st.info(
            "Keep working on your weekly goals. "
            "Every completed task brings you closer to "
            "becoming job ready."
        )


# --------------------------------------------------
# Previous weeks' progress
# --------------------------------------------------

st.divider()

st.subheader("📅 Previous Learning Weeks")

history_conn = sqlite3.connect("joblens.db")

weekly_history = pd.read_sql_query(
    """
    SELECT
        week_start,
        COUNT(*) AS total_tasks,
        SUM(completed) AS completed_tasks
    FROM weekly_tasks
    GROUP BY week_start
    ORDER BY week_start DESC
    """,
    history_conn
)

history_conn.close()

if weekly_history.empty:

    st.info(
        "Your weekly learning history will appear here "
        "as you add tasks."
    )

else:

    weekly_history["completed_tasks"] = (
        weekly_history["completed_tasks"].fillna(0).astype(int)
    )

    weekly_history["completion_percentage"] = (
        weekly_history["completed_tasks"] /
        weekly_history["total_tasks"] * 100
    ).round(1)

    weekly_history = weekly_history.rename(
        columns={
            "week_start": "Week Starting",
            "total_tasks": "Total Tasks",
            "completed_tasks": "Completed Tasks",
            "completion_percentage": "Completion (%)"
        }
    )

    st.dataframe(
        weekly_history,
        width="stretch",
        hide_index=True
    )


# ==================================================
# 18. FOOTER
# ==================================================

st.divider()

st.caption(
    "JobLens | AI Job Market & Skill Gap Analyzer | "
    "Python | Pandas | SQL | SQLite | Scikit-learn | Streamlit"
)
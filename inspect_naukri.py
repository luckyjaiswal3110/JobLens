import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="JobLens",
    page_icon="📊",
    layout="wide"
)

st.title("📊 JobLens")
st.subheader("AI Job Market & Skill Gap Analyzer")

st.write(
    "Explore job market trends and analyse your skills "
    "against real job requirements."
)


# --------------------------------------------------
# 2. LOAD DATA FROM SQLITE DATABASE
# --------------------------------------------------

conn = sqlite3.connect("joblens.db")

jobs = pd.read_sql_query(
    "SELECT * FROM jobs",
    conn
)

naukri_jobs = pd.read_sql_query(
    "SELECT * FROM naukri_jobs",
    conn
)

naukri_skills = pd.read_sql_query(
    "SELECT * FROM naukri_skills",
    conn
)

conn.close()


# --------------------------------------------------
# 3. JOB MARKET DASHBOARD
# --------------------------------------------------

st.header("📈 Job Market Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Original Job Listings", len(jobs))

col2.metric("Naukri Job Listings", len(naukri_jobs))

col3.metric(
    "Unique Skills",
    naukri_skills["skill"].nunique()
)

st.divider()


# --------------------------------------------------
# 4. ORIGINAL DATASET LOCATION FILTER
# --------------------------------------------------

st.subheader("Explore Job Listings")

locations = ["All"] + sorted(
    jobs["location"].dropna().unique().tolist()
)

selected_location = st.selectbox(
    "Choose a location",
    locations,
    key="original_location"
)

if selected_location == "All":
    filtered_jobs = jobs
else:
    filtered_jobs = jobs[
        jobs["location"] == selected_location
    ]

st.dataframe(
    filtered_jobs,
    use_container_width=True
)

st.divider()


# --------------------------------------------------
# 5. TOP STATES BY JOB LISTINGS
# --------------------------------------------------

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


# --------------------------------------------------
# 6. AVERAGE SALARY BY STATE
# --------------------------------------------------

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


# --------------------------------------------------
# 7. MOST COMMON JOB TITLES
# --------------------------------------------------

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

st.divider()


# --------------------------------------------------
# 8. AI SKILL GAP ANALYZER
# --------------------------------------------------

st.header("🤖 AI Skill Gap Analyzer")

st.write(
    "Enter your current skills and select a target job role. "
    "JobLens will compare your skills with the requirements "
    "found in matching Naukri job listings."
)

st.info(
    "This dataset contains historical job listings from around "
    "2016. The results demonstrate skill matching, not current "
    "2026 hiring demand."
)


# --------------------------------------------------
# 9. SELECT JOB ROLE
# --------------------------------------------------

role_counts = naukri_jobs["jobtitle"].value_counts()

popular_roles = role_counts[
    role_counts >= 5
].index.tolist()

popular_roles = sorted(popular_roles)

selected_role = st.selectbox(
    "Choose your target job role",
    ["Select a role"] + popular_roles,
    key="target_role"
)


# --------------------------------------------------
# 10. ENTER CANDIDATE SKILLS
# --------------------------------------------------

candidate_input = st.text_input(
    "Enter your skills separated by commas",
    placeholder="Example: Python, SQL, Excel, Pandas"
)

analyse_button = st.button(
    "Analyse My Skills",
    type="primary"
)


# --------------------------------------------------
# 11. SKILL MATCHING
# --------------------------------------------------

if analyse_button:

    if selected_role == "Select a role":

        st.warning("Please select a job role.")

    elif not candidate_input.strip():

        st.warning("Please enter your existing skills.")

    else:

        # Convert candidate skills into lowercase
        candidate_skills = {
            skill.strip().lower()
            for skill in candidate_input.split(",")
            if skill.strip()
        }

        # Find jobs matching selected role
        matching_jobs = naukri_jobs[
            naukri_jobs["jobtitle"] == selected_role
        ]

        matching_job_ids = matching_jobs["jobid"].unique()

        # Get skills required for this role
        required_skills_data = naukri_skills[
            naukri_skills["jobid"].isin(matching_job_ids)
        ]

        # Count how many job listings mention each skill
        skill_demand = (
            required_skills_data
            .groupby("skill")["jobid"]
            .nunique()
            .sort_values(ascending=False)
        )

        # Select top 10 required skills
        top_required_skills = skill_demand.head(10)

        required_skills = {
            skill.lower()
            for skill in top_required_skills.index
        }

        if not required_skills:

            st.warning(
                "No extracted skills were found for this role. "
                "Try another job title."
            )

        else:

            # Matched and missing skills
            matched_skills = (
                candidate_skills & required_skills
            )

            missing_skills = (
                required_skills - candidate_skills
            )

            # Calculate skill match percentage
            match_percentage = (
                len(matched_skills) /
                len(required_skills)
            ) * 100

            st.divider()

            st.subheader("Your Skill Gap Report")

            st.metric(
                "Skill Match Percentage",
                f"{match_percentage:.1f}%"
            )

            st.progress(
                int(round(match_percentage))
            )

            st.write(
                f"**Job listings analysed:** "
                f"{len(matching_jobs)}"
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

            st.dataframe(
                demand_display,
                use_container_width=True
            )

            # Learning recommendations
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

                "mysql": "https://dev.mysql.com/doc/",

                "powerpoint": "https://support.microsoft.com/powerpoint"
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
                    "Great! You match all the top listed skills "
                    "for this role."
                )

            st.caption(
                "Skill match percentage represents the share of "
                "the selected role's top 10 extracted skills "
                "that match your entered skills. It is not a "
                "probability of getting hired."
            )


# --------------------------------------------------
# 12. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "JobLens | AI Job Market & Skill Gap Analyzer | "
    "Built using Python, Pandas, SQL, SQLite and Streamlit."
)
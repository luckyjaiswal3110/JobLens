import pandas as pd
import sqlite3
import re

# ==========================================
# 1. LOAD NAUKRI DATASET
# ==========================================

jobs = pd.read_csv("Naukri_com-job_sample.csv")

jobs.columns = (
    jobs.columns.str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

print("JobLens: Preparing Technical Skills Data")
print("----------------------------------------")

print("Original job listings:", len(jobs))


# ==========================================
# 2. CLEAN JOB DATA
# ==========================================

jobs = jobs.drop_duplicates()

if "uniq_id" in jobs.columns:
    jobs = jobs.drop_duplicates(subset=["uniq_id"])

jobs["jobtitle"] = (
    jobs["jobtitle"]
    .fillna("")
    .astype(str)
    .str.strip()
)

jobs["jobdescription"] = (
    jobs["jobdescription"]
    .fillna("")
    .astype(str)
    .str.strip()
)

jobs = jobs[jobs["jobtitle"] != ""]

jobs = jobs.reset_index(drop=True)


# ==========================================
# 3. TECHNICAL SKILLS DICTIONARY
# ==========================================

technical_skills = {
    "Python": [r"\bpython\b"],
    "SQL": [r"\bsql\b", r"\bmysql\b", r"\bpostgresql\b"],
    "Excel": [r"\bexcel\b", r"\bmicrosoft excel\b"],
    "Power BI": [r"\bpower\s?bi\b"],
    "Tableau": [r"\btableau\b"],
    "Machine Learning": [r"\bmachine learning\b"],
    "Deep Learning": [r"\bdeep learning\b"],
    "Artificial Intelligence": [r"\bartificial intelligence\b", r"\bAI\b"],
    "Pandas": [r"\bpandas\b"],
    "NumPy": [r"\bnumpy\b"],
    "R": [r"\bR programming\b", r"\blanguage R\b"],
    "Statistics": [r"\bstatistics\b", r"\bstatistical analysis\b"],
    "Data Analysis": [r"\bdata analysis\b", r"\bdata analytics\b"],
    "Data Visualization": [r"\bdata visualization\b", r"\bdata visualisation\b"],
    "Data Mining": [r"\bdata mining\b"],
    "Big Data": [r"\bbig data\b"],
    "Hadoop": [r"\bhadoop\b"],
    "Spark": [r"\bapache spark\b", r"\bpyspark\b"],
    "AWS": [r"\bAWS\b", r"\bAmazon Web Services\b"],
    "Azure": [r"\bMicrosoft Azure\b", r"\bAzure\b"],
    "Google Cloud": [r"\bGoogle Cloud\b", r"\bGCP\b"],
    "Java": [r"\bjava\b"],
    "C++": [r"\bC\+\+\b"],
    "C": [r"\bC programming\b"],
    "HTML": [r"\bHTML\b"],
    "CSS": [r"\bCSS\b"],
    "JavaScript": [r"\bJavaScript\b"],
    "React": [r"\bReactJS\b", r"\bReact\b"],
    "Node.js": [r"\bNode\.?js\b"],
    "PHP": [r"\bPHP\b"],
    "Git": [r"\bGit\b", r"\bGitHub\b"],
    "Linux": [r"\bLinux\b"],
    "PowerPoint": [r"\bPowerPoint\b"],
    "ETL": [r"\bETL\b"],
    "Data Warehousing": [r"\bdata warehousing\b"],
    "Database Management": [r"\bdatabase management\b", r"\bDBMS\b"],
    "MongoDB": [r"\bMongoDB\b"],
    "Oracle": [r"\bOracle Database\b"],
    "SAS": [r"\bSAS\b"],
    "SPSS": [r"\bSPSS\b"],
    "TensorFlow": [r"\bTensorFlow\b"],
    "PyTorch": [r"\bPyTorch\b"],
    "Scikit-learn": [r"\bscikit.learn\b", r"\bsklearn\b"],
    "NLP": [r"\bnatural language processing\b", r"\bNLP\b"],
    "Computer Vision": [r"\bcomputer vision\b"],
    "Time Series Analysis": [r"\btime series analysis\b"],
    "Data Structures": [r"\bdata structures\b"],
    "Algorithms": [r"\balgorithms\b"],
}


# ==========================================
# 4. EXTRACT TECHNICAL SKILLS
# ==========================================

skill_records = []

for _, row in jobs.iterrows():

    description = str(row["jobdescription"]).lower()

    for skill, patterns in technical_skills.items():

        for pattern in patterns:

            if re.search(pattern, description, flags=re.IGNORECASE):

                skill_records.append({
                    "jobid": row["jobid"],
                    "skill": skill
                })

                break


# ==========================================
# 5. CREATE SKILLS DATAFRAME
# ==========================================

skills_df = pd.DataFrame(
    skill_records,
    columns=["jobid", "skill"]
)

skills_df = skills_df.drop_duplicates()

print("\nTechnical skill extraction completed!")

print("Total technical skill records:", len(skills_df))

print(
    "Unique technical skills found:",
    skills_df["skill"].nunique()
)


# ==========================================
# 6. DISPLAY MOST DEMANDED SKILLS
# ==========================================

print("\nTOP 20 TECHNICAL SKILLS IN JOB DESCRIPTIONS")
print("------------------------------------------")

if not skills_df.empty:

    top_skills = (
        skills_df["skill"]
        .value_counts()
        .head(20)
    )

    print(top_skills)

else:

    print("No technical skills were detected.")


# ==========================================
# 7. SAVE CLEANED DATA
# ==========================================

jobs.to_csv("naukri_cleaned.csv", index=False)

skills_df.to_csv(
    "naukri_skills_long.csv",
    index=False
)


# ==========================================
# 8. UPDATE SQLITE DATABASE
# ==========================================

conn = sqlite3.connect("joblens.db")

jobs.to_sql(
    "naukri_jobs",
    conn,
    if_exists="replace",
    index=False
)

skills_df.to_sql(
    "naukri_skills",
    conn,
    if_exists="replace",
    index=False
)

conn.close()


# ==========================================
# 9. FINAL REPORT
# ==========================================

print("\n------------------------------------------")
print("JOBLENS DATA PREPARATION COMPLETED!")
print("------------------------------------------")

print("Total job listings:", len(jobs))
print("Total technical skill records:", len(skills_df))
print("Unique technical skills:", skills_df["skill"].nunique())

print("\nDatabase updated successfully!")
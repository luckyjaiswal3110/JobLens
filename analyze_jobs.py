import pandas as pd

jobs = pd.read_csv("jobs.csv")

print("Welcome to JobLens Data Analysis!")

print("\nTotal job listings:", len(jobs))

print("\nAll job listings:")
print(jobs)

print("\nJobs by location:")
print(jobs["location"].value_counts())
print("\nJobs requiring Python:")

python_jobs = jobs[
    jobs["skills"].str.contains("Python", case=False)
]

print(python_jobs)

print("\nNumber of jobs requiring Python:")
print(len(python_jobs))
print("\n--- Most Demanded Skills ---")

all_skills = []

for skill_list in jobs["skills"]:
    skills = skill_list.split(";")

    for skill in skills:
        all_skills.append(skill.strip())

skill_counts = pd.Series(all_skills).value_counts()

print(skill_counts)
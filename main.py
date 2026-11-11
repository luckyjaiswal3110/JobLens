jobs = [
    {
        "title": "Data Analyst Intern",
        "company": "ABC Analytics",
        "location": "Lucknow",
        "skills": ["Python", "SQL", "Excel"]
    },
    {
        "title": "Junior Data Analyst",
        "company": "DataWorks",
        "location": "Delhi NCR",
        "skills": ["Python", "SQL", "Power BI"]
    },
    {
        "title": "Python Developer Intern",
        "company": "TechStart",
        "location": "Remote",
        "skills": ["Python", "Git", "SQL"]
    }
]

print("Welcome to JobLens!")
print("Total jobs:", len(jobs))

print("\nAvailable jobs:")

for job in jobs:
    print(job["title"], "-", job["location"])
    lucknow_count = 0

for job in jobs:
    if job["location"] == "Lucknow":
        lucknow_count += 1

print("Jobs in Lucknow:", lucknow_count)
delhi_count = 0
remote_count = 0

for job in jobs:
    if job["location"] == "Delhi NCR":
        delhi_count += 1

    elif job["location"] == "Remote":
        remote_count += 1

print("\nJobs in Delhi NCR:", delhi_count)
print("Remote jobs:", remote_count)
skill_counts = {}

for job in jobs:
    for skill in job["skills"]:
        if skill in skill_counts:
            skill_counts[skill] += 1
        else:
            skill_counts[skill] = 1

print("\nMost demanded skills:")

for skill, count in skill_counts.items():
    print(skill, ":", count)
    sorted_skills = sorted(
    skill_counts.items(),
    key=lambda item: item[1],
    reverse=True
)

print("\nSkills ranked by demand:")

for skill, count in sorted_skills:
    print(skill, "-", count, "jobs")
sorted_skills = sorted(
    skill_counts.items(),
    key=lambda item: item[1],
    reverse=True
)

print("\nSkills ranked by demand:")

for skill, count in sorted_skills:
    print(skill, "-", count, "jobs")
    print("\n--- Welcome to JobLens ---")

print("\nAvailable jobs:")

for index, job in enumerate(jobs, start=1):
    print(index, ".", job["title"], "-", job["location"])

choice = int(input("\nChoose a job number: "))

selected_job = jobs[choice - 1]

user_input = input(
    "\nEnter your skills separated by commas: "
)

my_skills = [
    skill.strip().lower()
    for skill in user_input.split(",")
]

required_skills = selected_job["skills"]

matched_skills = []
missing_skills = []

for skill in required_skills:
    if skill.lower() in my_skills:
        matched_skills.append(skill)
    else:
        missing_skills.append(skill)

match_percentage = (
    len(matched_skills) / len(required_skills)
) * 100

print("\n--- Your JobLens Report ---")

print("Selected job:", selected_job["title"])
print("Matched skills:", matched_skills)
print("Missing skills:", missing_skills)
print("Skill Match:", round(match_percentage, 2), "%")
print("\n--- Learning Recommendations ---")

learning_resources = {
    "Python": "Learn Python basics and problem solving",
    "SQL": "Learn SQL queries, joins and database basics",
    "Excel": "Learn formulas, pivot tables and data analysis",
    "Power BI": "Learn dashboards and data visualisation",
    "Git": "Learn Git and GitHub basics"
}

if missing_skills:
    for skill in missing_skills:
        print(skill, ":", learning_resources.get(
            skill,
            "Search for beginner tutorials"
        ))
else:
    print("Congratulations! You have all the required skills.")
import pandas as pd
import sqlite3

jobs = pd.read_csv("job_market_india.csv")

print("Welcome to JobLens Real Data Analysis!")

print("\nTotal job listings:")
print(len(jobs))

print("\nColumn names:")
print(jobs.columns.tolist())
print("\nDataset shape:")
print(jobs.shape)

print("\nAll column names:")
print(list(jobs.columns))
print("\nFirst 5 job listings:")
print(jobs.to_string())

print("\n--- Jobs by State ---")

state_counts = jobs["State"].value_counts()

print(state_counts)
print("\n--- Data Quality Report ---")

print("\nMissing values in each column:")
print(jobs.isnull().sum())
print("\n--- Missing Data Percentage ---")

missing_percentage = (jobs.isnull().sum() / len(jobs)) * 100

print(missing_percentage)

print("\nTotal duplicate records:")
print(jobs.duplicated().sum())

print("\nTotal rows:")
print(len(jobs))
print("\n--- Duplicate Job Listings ---")

duplicates = jobs[jobs.duplicated()]

print(duplicates.to_string())
print("\n--- Removing Duplicate Records ---")

jobs = jobs.drop_duplicates()

print("Total records after removing duplicates:", len(jobs))
print("\n--- Missing Values in Salary and Locality ---")

print("Missing salaries:", jobs["Monthly Salary"].isnull().sum())

print("Missing localities:", jobs["Locality"].isnull().sum())
print("\n--- Handling Missing Values ---")

jobs["Monthly Salary"] = jobs["Monthly Salary"].fillna("Not Provided")

jobs["Locality"] = jobs["Locality"].fillna("Not Provided")

print("\nMissing values after cleaning:")
print(jobs[["Monthly Salary", "Locality"]].isnull().sum())
print("\n--- Current Column Names ---")
print(jobs.columns.tolist())
jobs.columns = (
    jobs.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

print("\n--- Cleaned Column Names ---")
print(jobs.columns.tolist())
print("\n--- Cleaning State Names ---")

jobs["state"] = jobs["state"].str.strip().str.title()

print(jobs["state"].value_counts().head(15))
print("\n--- Records with India as State ---")

india_records = jobs[jobs["state"] == "India"]

print("Number of records:", len(india_records))

print(india_records.to_string())
print("\n--- Checking Location of These 9 Records ---")

print(india_records[["job_title", "location", "locality", "state"]].to_string(index=False))
jobs.loc[jobs["state"] == "India", ["state", "location", "locality"]] = "Not Provided"
print(jobs["state"].value_counts().head(15))
print("\n--- Cleaning Job Titles ---")

jobs["job_title"] = (
    jobs["job_title"]
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
)

print("\nMost common job titles:")
print(jobs["job_title"].value_counts().head(20))
print("\n--- Inspecting Salary Data ---")

print("\nSalary column:")
print(jobs["salary"].head(15).to_string(index=False))

print("\nMonthly salary column:")
print(jobs["monthly_salary"].head(15).to_string(index=False))
print("\n--- Converting Monthly Salary to Numbers ---")

jobs["monthly_salary"] = pd.to_numeric(
    jobs["monthly_salary"],
    errors="coerce"
)

print(jobs["monthly_salary"].head(15))

print("\nSalary data type:")
print(jobs["monthly_salary"].dtype)
print("\n--- Monthly Salary Statistics ---")

print("Average monthly salary:", jobs["monthly_salary"].mean())

print("Highest monthly salary:", jobs["monthly_salary"].max())

print("Lowest monthly salary:", jobs["monthly_salary"].min())

print("Available salary records:", jobs["monthly_salary"].count())
print("\n--- Average Monthly Salary by State ---")

state_salary = jobs.groupby("state")["monthly_salary"].mean()

print(state_salary.sort_values(ascending=False).round(2))

print("\n--- Most In-Demand Job Roles ---")

job_counts = jobs["job_title"].value_counts()

print(job_counts.head(20))
print("\n--- Average Salary by Job Role ---")

job_salary = jobs.groupby("job_title")["monthly_salary"].agg(
    ["mean", "count"]
)

job_salary = job_salary.sort_values(
    by="mean",
    ascending=False
)

print(job_salary.head(15).round(2))

print("\n--- Job Listings by Location ---")

location_counts = jobs["location"].value_counts()

print(location_counts.head(20))
print("\n--- Top 10 States by Job Opportunities ---")

top_states = jobs["state"].value_counts().head(10)

print(top_states)
print("\n--- Saving Clean Dataset ---")

jobs.to_csv("joblens_cleaned.csv", index=False)

print("Clean dataset saved successfully!")
print("\n--- Creating JobLens Database ---")

conn = sqlite3.connect("joblens.db")

jobs.to_sql("jobs", conn, if_exists="replace", index=False)

conn.close()

print("JobLens database created successfully!")
import matplotlib.pyplot as plt

top_states = jobs["state"].value_counts().head(10)

top_states.plot(kind="bar", figsize=(10, 5))

plt.title("Top 10 States by Job Listings")
plt.xlabel("State")
plt.ylabel("Number of Jobs")
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()
state_salary = jobs.groupby("state")["monthly_salary"].mean()
state_salary = state_salary.sort_values(ascending=False).head(10)

state_salary.plot(kind="bar", figsize=(10, 5))

plt.title("Top 10 States by Average Monthly Salary")
plt.xlabel("State")
plt.ylabel("Average Monthly Salary (₹)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
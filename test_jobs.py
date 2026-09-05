import pandas as pd

jobs = pd.read_csv("data/jobs.csv")

print("Total Jobs:", len(jobs))
print("\nAvailable Jobs:")

for job in jobs["job_title"]:
    print("-", job)
Day 9 – Database Optimization

This document captures BEFORE and AFTER EXPLAIN ANALYZE results for key APIs.
The goal is to justify indexing decisions using measurable performance data.

⸻

Legend
	•	Scan Type: Seq Scan / Index Scan / Bitmap Index Scan
	•	Execution Time: Total execution time from EXPLAIN ANALYZE
	•	Rows Examined: Rows scanned vs rows returned
	•	Index Used: Name of index (if any)

⸻

1️⃣ Get All Jobs – Search & Filters

#	Query Purpose	        	       Before Time (ms)	           	    After Time (ms)	                    Index Used	                Notes
1   Search by description                 0.235 ms                      0.115 ms                           idx_jobs_description_trgm                                                      
2   Search by title                       3.085 ms                      0.086 ms                            idx_jobs_title_trgm 
3   Filter by location                    0.495 ms                      0.335 ms                            idx_jobs_location
4   Salary lower bound                    0.173 ms                      0.172 ms                            idx_jobs_salary_range
5   Salary upper bound                    0.214 ms                      0.191 ms                            idx_jobs_salary_range
6   Experience range                      0.259 ms                      0.352 ms                            idx_jobs_experience_range
7   Get job by ID                         0.411 ms                      0.264 ms                            Primary Key
8   Sort by views                         0.341 ms                      0.181 ms                            idx_jobs_view_count_desc

⸻

2️⃣ Apply for a Job (Write Path)

#	Query Purpose	Query	Index Impact	Notes
10	Apply for job	INSERT INTO job_applications (job_id, candidate_id)	❌ No read benefit	Indexes slightly slow inserts but enable fast reads


⸻

3️⃣ Get Single Job Application

#	Query Purpose	Query	Scan Type	Index Used	Notes
11	Get application by ID	job_applications WHERE id = 6	Index Scan	Primary Key	No change needed


⸻

4️⃣ Get Job View Count

#	Query Purpose	Query	Scan Type	Index Used	Notes
12	Get job views	jobs WHERE id = 1	Index Scan	Primary Key	Already optimal


⸻

5️⃣ Get Popular Job (Most Applications)

#	Query Purpose	Before Scan	    After Scan	            Index Used	                    Notes
13	Popular job		0.747 ms        0.345 ms                idx_job_applications_job_id	    Critical for scale


⸻

6️⃣ Get Trending Job (Most Viewed)

#	Query Purpose	Before Scan	    After Scan	            Index Used	                Notes
14	Trending job	0.296 ms		0.298 ms                idx_jobs_view_count_desc	Fast leaderboard query


⸻

How to Use This Document
	1.	Run each query with:

EXPLAIN ANALYZE <query>;


	2.	Fill Before Scan Type and Before Time columns.
	3.	Apply Alembic migrations (indexes).
	4.	Run the same queries again.
	5.	Fill After Scan Type and After Time columns.

⸻

Summary (to fill after optimization)
	•	Average query latency before indexing: ____ ms
	•	Average query latency after indexing: ____ ms
	•	Major wins observed in:
	•	Text search :
	•	Popular / trending job queries :
	•	High-frequency filters :

#Queries:

# Get all jobs - all queries

select * from jobs where job_description like '%recommendation%';

select * from jobs where lower(job_title) like '%influencer%';

select * from jobs where job_location = 'Remote';

select * from jobs where salary_lower_range >= 50000;

select * from jobs where salary_upper_range <= 95000;

select * from jobs where experience_start >= 0 and experience_end < 20;

select * from jobs where id = 2;

select * from jobs where status='active';

select * from jobs ORDER BY view_count desc;

# apply for a job

INSERT INTO job_applications (job_id, candidate_id) values (1, 2);

# get a single job
select * from job_applications where id = 6;

# get a job's view count

select id , view_count as views from jobs where id = 1;

# get popular job

select job_id, count(id) as jobs from job_applications GROUP BY job_id ORDER BY jobs desc limit 1;

# get trendy job

select id, view_count as views from jobs ORDER BY view_count desc limit 1;


Status: ⬜ Baseline captured | ⬜ Migration applied | ⬜ Post-analysis complete
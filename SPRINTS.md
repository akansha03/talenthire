# Job Board API - Sprint Plan

## Sprint 1 (Week 1: Days 1-7)
### Goal: Basic API + Auth Working

**Day 1-2: Setup & Auth**
- [ ] Project structure created
- [ ] Database connection setup
- [ ] User model (company/candidate types)
- [ ] Registration endpoint
- [ ] Login endpoint (JWT)
- [ ] Password hashing

**Day 3-4: Job Listings**
- [ ] Job model with relationships
- [ ] POST /jobs (companies only)
- [ ] GET /jobs (all users)
- [ ] GET /jobs/{id}
- [ ] Authorization middleware

**Day 5-7: Applications**
- [ ] Application model
- [ ] POST /jobs/{id}/apply (candidates only)
- [ ] GET /my-applications (candidate view)
- [ ] GET /job/{id}/applicants (company view)
- [ ] Basic tests written

**Sprint 1 Deliverable:** MVP API with auth, jobs, applications

---

## Sprint 2 (Week 2: Days 8-14)
### Goal: Search, Filters, Testing

**Day 8-9: Search & Filters**
- [ ] Search jobs by title/description
- [ ] Filter by location
- [ ] Filter by salary range
- [ ] Filter by job type
- [ ] Pagination

**Day 10-11: Performance**
- [ ] Database indexing
- [ ] Redis caching for search
- [ ] Query optimization
- [ ] Load testing

**Day 12-14: Testing & Docs**
- [ ] Test coverage 70%+
- [ ] API documentation (Swagger)
- [ ] README with setup instructions
- [ ] Deployed to Render

**Sprint 2 Deliverable:** Production-ready API with tests

---

## Sprint 3 (Week 3: Days 15-21)
### Goal: Advanced Features

**Day 15-16: Email System**
- [ ] Celery + Redis setup
- [ ] Email on new application
- [ ] Email on job posted
- [ ] Background job processing

**Day 17-18: Analytics**
- [ ] Job view tracking
- [ ] Application stats
- [ ] Company dashboard
- [ ] Candidate dashboard

**Day 19-21: Polish**
- [ ] Rate limiting
- [ ] Error handling improvement
- [ ] Logging
- [ ] Performance monitoring
- [ ] Final deployment

**Sprint 3 Deliverable:** Full-featured production app
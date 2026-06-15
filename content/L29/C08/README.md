# L29/C08 — Resume & LinkedIn

## Topics

- **T01 Impact-Driven Bullets** — Show, don't tell
- **T02 ATS Optimization** — Pass automated screens
- **T03 Recruiter Outreach** — Be findable

## Resume Format

### One Page (for < 10 years)
Recruiters glance for 6-30 seconds. One page forces tight, impactful content.

### Two Pages (10+ years OR Staff+)
Acceptable. Keep tight; no fluff.

### PDF
- Format consistent across viewers
- ATS-readable (text not image)
- Filename: `<FirstLast>_Resume.pdf`

### Structure
```
NAME (large)
contact: email | phone | LinkedIn | GitHub | Location

SUMMARY (optional, 2-3 lines)

EXPERIENCE
  Company | Title | Dates
    • Impact bullet
    • Impact bullet
    • Impact bullet

EDUCATION
  School | Degree | Dates | (GPA if > 3.5)

SKILLS
  brief list

CERTIFICATIONS (if relevant)

PROJECTS (optional; for OSS contributions)
```

## Impact-Driven Bullets

### Bad
- "Worked on Kubernetes infrastructure"
- "Maintained CI/CD pipelines"
- "Used Terraform"
- "Helped with cost optimization"

### Good
- "Led migration of 50+ services from EC2 to EKS, reducing deploy time from 2h to 8min and infra cost 40%"
- "Architected multi-region CI/CD pipeline handling 10K builds/day with 99.95% reliability"
- "Reduced AWS bill $1.2M/year via FinOps program: rightsizing + Savings Plans + Karpenter spot"
- "Built service mesh adoption (Istio) across 200 services, enabling mTLS, observability, canary deploys"

### Formula
```
ACTION + IMPACT + SCALE
"Led X" + "saving / improving Y" + "at Z scale"
```

- ACTION: led, designed, built, migrated, optimized
- IMPACT: quantified (cost, time, reliability, throughput)
- SCALE: services, requests, users, dollars, engineers

### Don't Use
- "Helped with..." (weak; what specifically?)
- "Was responsible for..." (passive)
- "Worked on..." (vague)
- "Familiar with..." (use Skills section)

### Quantify Everything
- Hours saved
- Money saved or earned
- Reliability % improvements
- Throughput numbers
- Team size led
- Project budget

If you can't quantify, ask: was there impact? If yes, find a number.

## ATS Optimization

### What ATS Is
Applicant Tracking System parses resume; matches to job description keywords.

### Practices
- Use standard fonts (Arial, Calibri, Helvetica)
- No images / graphics (ATS may fail to parse)
- No headers/footers (often missed)
- Standard section names (EXPERIENCE, not "Where I've Worked")
- Keywords from JD mentioned naturally
- File: PDF (text-based) or .docx

### Keyword Matching
- Copy JD; extract keywords (AWS, Kubernetes, Terraform, etc.)
- Use those exact words in resume (where true)
- Don't keyword stuff; integrate naturally

### Example
JD: "Experience with AWS, Kubernetes, Terraform, CI/CD, Python..."

Resume:
- "Led platform team designing AWS-based EKS infrastructure"
- "Authored Terraform modules adopted by 30+ engineers"
- "Owned CI/CD platform handling Python, Go, Node services"

Keywords there, in context.

## Skills Section

Keep tight. Group by category.

```
SKILLS
Cloud: AWS (deep), GCP, Azure
Container: Kubernetes (EKS, GKE), Docker, Containerd
IaC: Terraform, CDK, Helm, Kustomize
CI/CD: GitHub Actions, ArgoCD, Jenkins
Observability: Prometheus, Grafana, Loki, OpenTelemetry
Languages: Go, Python, Bash
```

Avoid "Word, Excel, PowerPoint" — assumed.

## Avoid

- Tables (ATS chokes)
- Columns (parsed weirdly)
- Color (looks fine; some ATS fail)
- Profile pic (don't bias hiring)
- "References available upon request"
- Personal interests unless relevant + unusual
- Languages (unless required)
- Address (city + state OK; not street)

## LinkedIn

### Profile Essentials
- **Headline**: not just job title; value prop ("Senior Platform Engineer | AWS/K8s | Building Internal Developer Platforms")
- **Photo**: professional, decent
- **About**: 2-3 paragraphs of career narrative
- **Experience**: mirror resume; more detail where wanted
- **Skills**: get endorsements from former colleagues
- **Recommendations**: ask 5-10 people

### Recruiter Outreach Optimization
- Use "Open to Work" feature (private to recruiters only)
- Configure preferences (location, role types, salary range)
- Be active on LinkedIn (comment, share)

### Job Title Discoverability
Recruiters search:
- "Senior DevOps Engineer"
- "Site Reliability Engineer"
- "Platform Engineer"
- "Staff Software Engineer"

If your title is "Specialist III, Cloud Engineering" — recruiters won't find you for "Senior DevOps Engineer". Adjust profile (truthfully).

## GitHub

For SWE/SRE/DevOps roles, GitHub matters.
- Pinned repos (your best work)
- Recent commits (show you're active)
- Public artifacts (blog posts, OSS contributions, projects)
- Profile README (highlight expertise)

### What to Build
- Real tools (something other engineers use)
- Capstone-style portfolios (see L30)
- Contributions to popular OSS (K8s, Terraform providers, Prometheus exporters)

## Blog / Talks

For Staff+ roles, public presence helps:
- Blog (Medium, Hashnode, personal site)
- Conference talks (KubeCon, SREcon, AWS re:Invent)
- Podcast appearances
- Books / book chapters (rare but powerful)

Show domain authority.

## Cover Letter

For most companies: optional.
- Custom only for "dream" roles
- 3 paragraphs: why this company, why this role, why you
- Don't repeat resume

## Recruiter Outreach Strategy

### Inbound
- Optimize LinkedIn
- Public GitHub / blog
- Mention you're "Open to Work"
- Engage with company content (likes, comments)

### Outbound
- Identify target companies
- Find recruiters on LinkedIn
- Short personalized message:
  "Hi <name>, I'm a senior platform engineer with deep AWS + K8s background, 8 years building infra at <Company>. I noticed you're hiring for <role>; would love to chat about fit. Resume attached."

### Referrals
- Most effective path
- Tap network on LinkedIn / Twitter
- Specifically: "Do you know anyone hiring senior DevOps at <Company>?"

## Resume Reviews

Get reviewed:
- Friends in target roles
- LinkedIn ResumeAssist (free Premium feature)
- Career coach ($$)
- Reddit r/cscareerquestions (free, variable quality)

Revise based on feedback. Resume is a living document.

## Final Tips

- **Tailor per company** — minor tweaks to keywords + summary
- **Test print** — does it look OK on paper too?
- **Spell check** — typos = instant reject for some
- **Save version history** — different versions for different roles
- **Update quarterly** — even when not job-hunting

## Interview Themes

- "Walk me through your resume"
- "Tell me about your biggest impact"
- "Why are you looking?"
- "What's your career growth in last 2 years?"

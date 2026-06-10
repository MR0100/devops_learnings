# L29/C08/T02 — ATS Optimization

## Learning Objectives

- Pass ATS
- Get to human

## ATS

Applicant Tracking System:
- Filters resumes
- Keyword-matching
- Pass/fail before human

## Issues

- Fancy formatting → broken
- Tables / columns → confused
- PDFs sometimes → text extraction issues
- Images → ignored

## Best Format

- PDF (well-formatted)
- Plain layout
- Standard sections

## Sections

- Name + contact
- Summary (optional)
- Experience
- Education
- Skills
- (Projects, Certifications)

## Keywords

Match job description:
- AWS, Kubernetes, Terraform
- Python, Go
- SRE, DevOps, Platform Engineering
- Certifications

## How

```python
# In skills section
Skills: Kubernetes, AWS, Terraform, Python, Go, CI/CD, Prometheus, Grafana, Linux
```

For: ATS keyword matching.

## Don't Stuff

Spam keywords: caught by ATS or human:
- Looks bad
- Backfires

## Standard Sections

- ATS recognizes
- "Experience" not "Career"

## Date Formats

```
2020-2024
2020 - Present
```

Not:
- "Last 4 years"
- Vague

## File Name

```
Alice_Smith_Resume.pdf
```

Not:
- "Resume v17 FINAL.pdf"

## Test

- Upload to ATS test tools
- See parsed output
- Iterate

Tools:
- Jobscan
- ResumeWorded

## Tailor

Per job:
- Match keywords
- Reorder bullets
- Same core

For: better match.

## Best Practices

- Standard format
- Keywords matched
- PDF clean
- Tested

## Common Mistakes

- Tables (broken)
- Images
- Fancy fonts
- Wrong file name

## Quick Refs

```
Format: PDF, clean
Sections: standard
Keywords: match JD
Test: parse tools
```

## Next Topic

→ [T03 — Recruiter Outreach](T03-Recruiter-Outreach.md)

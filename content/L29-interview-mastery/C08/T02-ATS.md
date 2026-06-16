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

## Interview Prep

**Junior**: "What is an ATS and why care?" — An Applicant Tracking System parses and filters resumes by keyword before a human sees them. If it can't read my resume — broken by tables, columns, or images — I'm rejected by a machine regardless of qualifications, so I use a clean single-column layout with standard section headings.

**Mid**: "How do you get past the keyword filter?" — Mirror the job description's terms in a dedicated skills section and throughout my bullets — Kubernetes, AWS, Terraform, CI/CD, the specific tools named in the JD. I don't keyword-stuff, which both ATS and humans catch; I make sure the real technologies I've used appear in the exact words the posting uses.

**Senior**: "What breaks ATS parsing most often?" — Multi-column layouts and tables (the parser scrambles reading order), text embedded in images (invisible to it), fancy fonts, and non-standard headings like 'Career' instead of 'Experience.' I use a plain single-column PDF, standard headings, and clear date formats, then verify with a parser tool like Jobscan to see what the machine actually extracted.

**Staff**: "How do you tailor per application without rewriting each time?" — I keep one strong master resume and make light per-role passes: reorder bullets to surface the most relevant experience first and align skill terms to that posting's language, while the core stays fixed. I run the tailored version through a parse-test to confirm keyword match, since a 10-minute tailor materially raises the callback rate at the volume senior searches require.

## Next Topic

→ [T03 — Recruiter Outreach](T03-Recruiter-Outreach.md)

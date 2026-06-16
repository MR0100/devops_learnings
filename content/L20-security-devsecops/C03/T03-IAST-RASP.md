# L20/C03/T03 — IAST & RASP

## Learning Objectives

- Understand IAST / RASP
- Use cases

## IAST

Interactive Application Security Testing:
- Hybrid SAST + DAST
- Runtime instrumentation
- During app execution
- Sees code + traffic

## How

App agent:
- Hooks into runtime
- Monitors data flow
- Detects vulns as they occur

For: more accurate.

## Tools

- Contrast Security
- Synopsys Seeker
- Acunetix

Commercial mostly.

## Workflow

```
1. Install IAST agent in app
2. Deploy to staging
3. Run tests / use app
4. IAST finds vulns in real time
5. Report
```

## Vs SAST/DAST

SAST: static; false positives.
DAST: dynamic; misses some.
IAST: instrumented; accurate, broader.

For: best of both, more cost.

## RASP

Runtime Application Self-Protection:
- Agent monitors during prod
- Blocks attacks in real time
- Not just detect

For: production defense.

## RASP Tools

- Contrast Protect
- Imperva
- Sqreen (acquired)
- F5 Distributed Cloud

## Vs WAF

WAF: external; pattern-based.
RASP: in-app; context-aware.

RASP: better at logic flaws.
WAF: easier deploy.

## How RASP Works

```
Request → App
   ↓
RASP intercepts
   ↓
Suspicious? Block.
Else: continue.
```

In-process.

## Examples

### SQL Injection
RASP sees:
- Query about to execute
- Tainted input
- Block

WAF: might miss if obfuscated.

### Insecure Deserialization
RASP:
- Deserializing untrusted
- Block

WAF can't see inside.

## Performance

- IAST: dev only; some overhead
- RASP: prod; 5-15% overhead

For: trade-off.

## When IAST

- Mature SDLC
- Complex apps
- High security
- Resources for tooling

## When RASP

- Production
- Critical app
- Limited WAF capability

## Limits

### IAST
- Agent install
- Per-language
- Cost

### RASP
- Performance
- False positives → blocks legit
- Vendor lock-in

## Compared

| | SAST | DAST | IAST | RASP |
|---|---|---|---|---|
| When | dev | test | dev/test | prod |
| Coverage | code | running | both | running |
| Speed | fast | slow | medium | runtime |
| Accuracy | medium FP | medium FN | high | high |
| Cost | low | low | high | high |

## Real Examples

Large enterprises:
- IAST for thorough dev
- RASP for high-value prod

Most:
- SAST + DAST + WAF
- IAST/RASP optional

## Cost

Significant:
- Commercial only mostly
- Per-app or per-CPU pricing

For: justify by risk.

## Future

- Open source emerging
- More mainstream
- Convergence with eBPF runtime tools

## Best Practices

- IAST in QA env
- RASP in prod
- WAF still needed
- Monitor performance

## Common Mistakes

- Skip if "WAF enough" (different)
- IAST in prod (overhead)
- No tuning (false positives block)

## Quick Refs

```
IAST: in-app, dev/test, runtime + code visibility
RASP: in-app, prod, blocks attacks

SAST = static code
DAST = dynamic external
IAST = dynamic internal
RASP = production protection
```

## Interview Prep

**Junior**: "What are IAST and RASP?" — IAST instruments a running app to detect vulnerabilities from inside during tests; RASP also instruments the app but stays in production to detect and block attacks at runtime.

**Mid**: "IAST vs DAST — what's the difference?" — Both test a running app, but IAST has inside visibility (code paths, data flow) via instrumentation, so it pinpoints the vulnerable line with low false positives, while DAST only sees external behavior.

**Senior**: "When would you deploy RASP, and what are the risks?" — Use RASP as a runtime backstop for apps you can't quickly patch or that face active attacks; the risks are performance overhead and false-positive blocking, so run it in monitor mode first and tune before enforcing.

**Staff**: "How do IAST/RASP fit into a layered AppSec stack?" — SAST/SCA shift left in the pipeline, DAST validates the running app pre-prod, IAST adds precise in-test detection, and RASP provides last-line runtime protection — defense in depth where each layer's weakness is covered by another, not a single tool to rule them all.

## Next Topic

→ [T04 — Software Composition Analysis (SCA)](T04-SCA.md)

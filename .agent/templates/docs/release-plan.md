# 🚀 Release Plan: v[X.Y.Z] — [Codename]

**Target Date**: [Date]
**Release Manager**: [Name]
**Status**: Preparing / Ready / Shipped

---

## 📦 Scope

| Type | Count | Key Items |
| :--- | :--- | :--- |
| Features | [X] | [List top items] |
| Bug Fixes | [Y] | [List top items] |
| Improvements | [Z] | [List top items] |

---

## ✅ Readiness Gates

### Gate 1: Engineering
- [ ] Code complete and merged to release branch
- [ ] Unit tests passing (>90% coverage on new code)
- [ ] Feature flags configured correctly
- [ ] Performance benchmarks met
- [ ] Tech debt items documented

### Gate 2: Quality Assurance
- [ ] Regression suite passing
- [ ] Edge cases documented and tested
- [ ] Cross-browser/device testing complete
- [ ] Accessibility audit passed (WCAG 2.1 AA)
- [ ] No open P0/P1 bugs

### Gate 3: Documentation
- [ ] Help center articles created/updated
- [ ] API documentation updated
- [ ] Internal runbook created
- [ ] Changelog drafted

### Gate 4: Support & Ops
- [ ] Support team briefed
- [ ] Escalation path defined
- [ ] Monitoring dashboards configured
- [ ] Alert thresholds set

### Gate 5: Sales & Marketing
- [ ] Release notes drafted
- [ ] Sales enablement ready
- [ ] In-app announcements configured
- [ ] Blog/email campaign queued

### Gate 6: Legal & Compliance
- [ ] Privacy review complete
- [ ] Terms updated (if needed)
- [ ] Compliance requirements met

---

## 📡 Rollout Plan

| Phase | Audience | Duration | Gate to Next |
| :--- | :--- | :--- | :--- |
| Canary | Internal team | 24h | No P0 issues |
| Internal Beta | All employees | 48h | Error rate <0.1% |
| External Beta | 5% of users | 72h | KPIs within bounds |
| GA | 25% → 50% → 100% | 1 week | Metrics stable |

---

## ↩️ Rollback Criteria

**Automatic Rollback Triggers**:
- Error rate > 2× baseline
- P95 latency > 2× baseline
- Core flow success rate drops below [X]%

**Manual Rollback Decision**:
1. Impact: How many users affected?
2. Severity: Data loss? Security? Degraded UX?
3. Fix Time: Hotfix in <2h? If no → rollback.

---

## 📊 Post-Launch Monitoring

| Window | Focus | Action If Anomaly |
| :--- | :--- | :--- |
| 0-4h | Errors, crashes, API failures | Immediate rollback consideration |
| 4-24h | User behavior, funnel metrics | Investigate + hotfix |
| 24-72h | Engagement, support tickets | Iterate or plan follow-up |
| 7d | Retention, NPS impact | Post-launch review |

---

## 📋 Post-Launch Checklist

- [ ] Monitor dashboards for 4h post-deploy
- [ ] Send release notes to stakeholders
- [ ] Update TASK_MASTER status
- [ ] Schedule post-launch review (T+7)
- [ ] Archive release branch

# Design Sync: Notification Center

> **Date**: 2024-03-15
> **Attendees**: @Admin, @Sarah (Design), @Mike (Eng)
> **Goal**: Review final mocks for the Notification Center.

## 📝 Transcript Summary

Sarah presented the Figma mocks. The team agreed on the "Red Dot" style for the badge. Mike raised a concern about the "Mark all as read" performance if a user has 1000+ notifications. We decided to cap the bulk action to the last 100 items for v1.

## ⚡ Action Items

- [ ] **@Sarah**: Update the "Empty State" illustration to be more friendly. (Due: **Tomorrow**)
- [ ] **@Mike**: Investigate pagination for the notification API. (Due: **Mar 18**)
- [ ] **@Admin**: Update the Spec to reflect the "100 item cap" decision. (Due: **Today**)

## 🧠 Decisions Log

- **Decision**: We will use a Red Dot (not a number) for the badge if count > 9.
- **Decision**: "Mark as read" will only impact the latest 100 items for performance safety in v1.

# Feature Spec: Notification Center (v1.0)

> **Status**: ✅ Approved
> **Product**: Web Dashboard
> **Owner**: @Admin

## 1. Concept

A centralized hub for all system alerts (billing, messages, system updates) to reduce email dependencies and increase user engagement.

## 2. Requirements

### Functional

1.  **Bell Icon**: Persistent in top-nav. Shows unread count badge (Red dot).
2.  **Dropdown**: Clicking bell opens a standardized dropdown list.
3.  **Actions**:
    - "Mark all as read" button.
    - Specific "View" action per notification type (e.g., Billing -> leads to Billing Page).
4.  **Real-time**: Updates without page refresh (WebSocket).

### Non-Functional

- **Performance**: Dropdown load time < 200ms.
- **Retention**: History stored for 30 days.

## 3. User Journey

1.  **Trigger**: User receives a new invoice.
2.  **Notification**: Top-nav bell shows "1" badge. System toast appears: "New Invoice #1023 available".
3.  **Action**: User clicks bell -> sees summary item.
4.  **Resolution**: User clicks item -> redirected to Invoice PDF. Badge clears.

## 4. Open Questions

- [ ] Do we group "Like" notifications (e.g., "5 people liked your post")? _Decision: No, not for v1._
- [ ] What is the max items in the dropdown before "View All"? _Decision: 10 items._

## 5. Tasks

- [ ] **Design**: Finalize "Empty State" illustration. (@Sarah)
- [ ] **Eng**: Set up WebSocket endpoint. (@Mike)
- [ ] **Eng**: Build React component for Dropdown.
- [ ] **QA**: Test "Mark as Read" latency.

# Skill: odoo-sync

## Description
Synchronize data with Odoo Community accounting system.

## Phase
Gold (Autonomous Employee)

## Trigger
- Scheduled sync (hourly/daily)
- After financial transactions
- Manual invocation

## Instructions

You are syncing with Odoo. Follow these steps:

### 1. Connect to Odoo
Use Odoo MCP with JSON-RPC API:
```
Server: odoo
Authentication: API key from environment
```

### 2. Fetch Data

#### Invoices
```
Tool: get_invoices
Params:
  state: [draft|open|paid|all]
  date_from: [ISO_DATE]
  date_to: [ISO_DATE]
```

#### Payments
```
Tool: get_payments
Params:
  date_from: [ISO_DATE]
  date_to: [ISO_DATE]
```

#### Expenses
```
Tool: get_expenses
Params:
  date_from: [ISO_DATE]
  date_to: [ISO_DATE]
```

### 3. Create Summary
Write to `/Accounting/Summary_YYYY-MM.md`:

```markdown
---
synced: [ISO_TIMESTAMP]
period: [YYYY-MM]
---

# Accounting Summary: [Month Year]

## Revenue
| Date | Client | Invoice # | Amount | Status |
|------|--------|-----------|--------|--------|
| ... | ... | ... | $... | Paid/Open |

**Total Revenue**: $[sum]
**Collected**: $[paid_sum]
**Outstanding**: $[open_sum]

## Payments Made
| Date | Vendor | Reference | Amount |
|------|--------|-----------|--------|
| ... | ... | ... | $... |

**Total Payments**: $[sum]

## Expenses
| Date | Category | Description | Amount |
|------|----------|-------------|--------|
| ... | ... | ... | $... |

**Total Expenses**: $[sum]

## Net Position
- Revenue: $[revenue]
- Expenses: $[expenses]
- Net: $[net]
```

### 4. Draft Actions (Gold - Prepare Only)
If invoice needs to be created:
1. Prepare draft in Odoo (draft state)
2. Create approval request
3. Wait for human approval before posting

### 5. Update Dashboard
Add sync status to System Status table.

### 6. Log Sync
```json
{
  "timestamp": "[ISO]",
  "action_type": "odoo_sync",
  "invoices_synced": [count],
  "payments_synced": [count],
  "result": "success"
}
```

## Permissions by Phase

| Action | Gold | Platinum Cloud | Platinum Local |
|--------|------|----------------|----------------|
| Read data | Yes | Yes | Yes |
| Create draft | Yes (approval needed) | Yes | Yes |
| Post invoice | After approval | NO | Yes (after approval) |
| Record payment | After approval | NO | Yes (after approval) |

## Success Criteria
- Data synced from Odoo
- Summary file updated
- Dashboard reflects sync status
- No unauthorized posting

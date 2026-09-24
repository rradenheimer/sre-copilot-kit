# Work item input schema (items.json)

```json
{
  "source": "postmortem PM-2026-014",
  "items": [
    {
      "title": "Add burn-rate alert for checkout availability SLO",
      "type": "User Story",
      "description": "Checkout outage was detected by customers 22 minutes before paging.",
      "acceptance_criteria": "Multiwindow burn-rate alert pages on-call within 5 minutes of a 14.4x burn.",
      "priority": 1,
      "area_path": "Commerce\\Checkout",
      "iteration_path": "Commerce\\Sprint 42",
      "tags": ["sre-postmortem"],
      "parent_id": 12345,
      "links": [{"rel": "System.LinkTypes.Related", "id": 12001}],
      "fields": {"Custom.ReliabilityCategory": "Detection"}
    }
  ]
}
```

Required: `title`, `type`. Everything else is optional unless the overlay lists it as required.
`type` must be one of the overlay's `work_item_types`. `priority` is 1-4.
Descriptions and acceptance criteria are plain text; the script converts line breaks to HTML.

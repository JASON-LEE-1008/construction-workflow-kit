# Input Schema

Construction Workflow Kit accepts a JSON object with four top-level sections.

## `project`

Required object.

Required fields:

- `name`: synthetic project name used in the report title
- `owner`: synthetic owner or agency name
- `phase`: current review or delivery phase

Recommended fields:

- `prepared_for`: report audience or coordination context

## `cost_items`

Optional list of cost review records.

Recommended fields for each item:

- `package`: cost package name
- `proposed_amount`: proposed numeric amount
- `reviewed_amount`: reviewed numeric amount

Amounts must be numbers and must not be negative.

## `meeting_notes`

Optional list of meeting note records.

Recommended fields for each note:

- `date`: meeting date in `YYYY-MM-DD` format
- `topic`: meeting topic
- `decisions`: list of decision strings
- `actions`: list of action strings

## `technical_items`

Optional list of technical material records.

Recommended fields for each item:

- `title`: technical document or issue title
- `status`: review status
- `owner`: person or role responsible for the item

Recognized status values include:

- `accepted`
- `accepted for draft reporting`
- `closed`
- `needs review`
- `open`
- `pending`
- `resolved`

## Data safety

Use synthetic data only. Do not include real client names, private company names,
internal project names, personal contact details, live contract values, or
confidential technical material.

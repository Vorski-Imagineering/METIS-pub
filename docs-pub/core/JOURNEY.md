# Journeys Manual

Journeys are the progression model used to track where a Person or Organisation (Holon) sits in a relationship with another Holon.

---

## Concepts

| Model | Purpose |
|---|---|
| `Journey` | A named progression track (e.g. "Contact Membership"). Targets a **Class** — the `MetisClass` it applies to (e.g. `person/person`, `holon/camp`, `holon/event`), stored on `applies_to_metis_class`. |
| `JourneyStep` | An ordered step within a journey (e.g. "Signed Up", "Active"). Each step has a `slug` and display config. |
| `Membership` | Links a **Person → Holon** and records their current journey/step. Requires a journey whose Class has `object_kind = person`. |
| `HolonRelationship` | Links a **Holon → Holon** and records the relationship's current journey/step. Requires a journey whose Class has `object_kind = holon`. |

> **A journey targets a Class.** Every journey applies to one **Class** (a `MetisClass`), and the class determines the journey's object kind — `person`, `holon`, or `convo`. Conversation journeys target a class with `object_kind = convo` and are managed in Coherence, not here.

---

## Existing Journeys

### Person Journeys (Class `object_kind = person`)

Used on `Membership` records.

| Slug | Name |
|---|---|
| `person_team_membership` | Team Membership |
| `person_participant_membership` | Participant Membership |
| `person_contact_membership` | Contact Membership |
| `person_contributor_membership` | Contributor Membership |

**Steps** (shared by all person journeys, in order):

| Order | Slug | Title |
|---|---|---|
| 1 | `invited` | Invited |
| 2 | `confirmed` | Confirmed |
| 3 | `signed_up` | Signed Up |
| 4 | `active` | Active |
| 5 | `retired` | Retired |

### Holon Journeys (Class `object_kind = holon`)

Used on `HolonRelationship` records.

| Slug | Name |
|---|---|
| `holon_participant_relationship` | Participant Relationship |
| `holon_sponsor_relationship` | Sponsor Relationship |
| `holon_partner_relationship` | Partner Relationship |
| `holon_affiliate_relationship` | Affiliate Relationship |
| `holon_camp_lead_relationship` | Camp Lead Relationship |

**Steps** (shared by all holon journeys, in order):

| Order | Slug | Title |
|---|---|---|
| 1 | `to_contact` | To Contact |
| 2 | `invited` | Invited |
| 3 | `confirmed` | Confirmed |
| 4 | `onboarded` | Onboarded |
| 5 | `active` | Active |
| 6 | `inactive` | Inactive |

---

## Creating a New Journey

Use the in-app **Journey editor** (`/journey/edit/` → the **＋** button) rather than the Django admin for day-to-day work.

1. On the create page, set:
   - **Class**: pick the class the journey applies to. Choices are grouped by **People** and **Holons** (e.g. `Person`, `Camp`, `Event`). The Class determines whether the journey is usable by Memberships (a People class) or HolonRelationships (a Holon class). Inactive classes are hidden unless an existing journey already uses one.
   - **Name**: human-readable label
2. Add **Journey Steps**:
   - Each step needs an **order**, **slug**, and **title**
   - The `slug` is what code references — keep it stable
   - Common step slugs: `signed_up`, `active`, `inactive`, `retired`
3. Save.

Selecting a Class sets what the journey applies to and derives its object kind (person / holon / convo) automatically. Conversation journeys are managed in Coherence, not here.

> **Constraint**: `(applies_to_metis_class, slug)` must be unique. You cannot have two journeys targeting the same MetisClass with the same slug.


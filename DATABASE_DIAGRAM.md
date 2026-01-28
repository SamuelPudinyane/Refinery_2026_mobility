# Database Schema Visualization

## Table Relationships Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MOBILITY APPLICATION                             │
│                      Dynamic Database Architecture                       │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────── USERS & AUTHENTICATION ────────────────────────┐
│                                                                          │
│  ┌──────────┐                ┌──────────┐                              │
│  │  Role    │◄───────────────│  User    │                              │
│  │  ======  │                │  ======  │                              │
│  │  id      │                │  id      │                              │
│  │  name    │                │  username│                              │
│  │  level   │                │  email   │                              │
│  │  perms   │                │  role_id │                              │
│  └──────────┘                │  parent_id (self-ref)                   │
│                               │  dept_id │                              │
│                               │  team_id │                              │
│                               │  custom_fields (JSONB)                  │
│                               └──────┬───┘                              │
│                                      │                                  │
│                                      │                                  │
│                          ┌───────────┴──────────┐                      │
│                          │                      │                      │
│                    ┌─────▼─────┐         ┌────▼─────┐                 │
│                    │UserLocation│         │ Message │                 │
│                    │============│         │=========│                 │
│                    │ latitude   │         │ sender  │                 │
│                    │ longitude  │         │recipient│                 │
│                    │ is_current │         │ body    │                 │
│                    └────────────┘         └─────────┘                 │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌────────────────────── ORGANIZATIONAL STRUCTURE ────────────────────────┐
│                                                                          │
│  ┌──────────────┐                  ┌──────────┐                        │
│  │ Department   │◄─────────────────│   Team   │                        │
│  │ ============ │                  │ ======== │                        │
│  │ id           │                  │ id       │                        │
│  │ name         │                  │ name     │                        │
│  │ parent_id    │ (self-ref)       │ dept_id  │                        │
│  │ head_user_id │──────┐           │ leader_id│────┐                   │
│  │ custom_fields│      │           └──────────┘    │                   │
│  └──────┬───────┘      │                           │                   │
│         │              │                           │                   │
│         │              └───────────────────────────┴─► User            │
│         │                                                               │
│         └──────────► OrganizationHistory                              │
│                      ==================                                │
│                      entity_type                                       │
│                      entity_id                                         │
│                      previous_state (JSONB)                            │
│                      new_state (JSONB)                                 │
│                      changed_by_id                                     │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────── SURVEY SYSTEM ────────────────────────────────┐
│                                                                          │
│  ┌──────────────┐        ┌──────────┐         ┌───────────────┐       │
│  │QuestionPool  │◄───────│ Question │         │    Survey     │       │
│  │============= │        │========= │         │============== │       │
│  │ id           │        │ id       │         │ id            │       │
│  │ name         │        │ pool_id  │         │ title         │       │
│  │ dept_id      │        │ text     │         │ dept_id       │       │
│  │ created_by   │        │ type     │         │ created_by    │       │
│  │ custom_fields│        │ options  │         │ start_date    │       │
│  └──────────────┘        │ required │         │ end_date      │       │
│                           │ custom   │         │ status        │       │
│                           └────┬─────┘         └───┬───────────┘       │
│                                │                   │                   │
│                                │      ┌────────────┴──────────┐        │
│                                └──────►   SurveyQuestion      │        │
│                                       │ ==================    │        │
│                                       │ survey_id             │        │
│                                       │ question_id           │        │
│                                       │ order_index           │        │
│                                       └──────┬────────────────┘        │
│                                              │                         │
│                                              │                         │
│  ┌────────────────────────────────────────────┼──────────────┐        │
│  │                                            │              │        │
│  │   ┌───────────────┐              ┌────────▼────────┐     │        │
│  │   │ SurveyAnswer  │◄─────────────│SurveyResponse   │     │        │
│  │   │============== │              │===============  │     │        │
│  │   │ response_id   │              │ id              │     │        │
│  │   │ question_id   │              │ survey_id       │     │        │
│  │   │ answer_text   │              │ user_id         │     │        │
│  │   │ answer_number │              │ dept_at_submit  │     │        │
│  │   │ answer_json   │              │ team_at_submit  │     │        │
│  │   └───────────────┘              │ location_id     │     │        │
│  │                                   │ hierarchy_path  │     │        │
│  │                                   │ custom_fields   │     │        │
│  │                                   └─────────────────┘     │        │
│  │                                                            │        │
│  │  Key Feature: Responses linked to organizational          │        │
│  │  structure at submission time - preserves history!        │        │
│  └────────────────────────────────────────────────────────────┘        │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────── CHECKLIST SYSTEM ──────────────────────────────┐
│                                                                          │
│  ┌──────────────────┐         ┌──────────────┐                         │
│  │ChecklistTemplate │◄────────│ChecklistItem │                         │
│  │================= │         │============= │                         │
│  │ id               │         │ template_id  │                         │
│  │ name             │         │ title        │                         │
│  │ dept_id          │         │ description  │                         │
│  │ require_location │         │ is_required  │                         │
│  │ custom_fields    │         │ requires_evidence                      │
│  └────┬─────────────┘         └──────────────┘                         │
│       │                                                                 │
│       │                                                                 │
│       └────────► ChecklistAssignment                                   │
│                  ===================                                   │
│                  template_id                                           │
│                  assigned_to_user_id                                   │
│                  assigned_to_team_id                                   │
│                  due_date                                              │
│                  status                                                │
│                          │                                             │
│                          │                                             │
│                          ▼                                             │
│                  ChecklistSubmission                                   │
│                  ===================                                   │
│                  assignment_id                                         │
│                  user_id                                               │
│                  dept_at_submission                                    │
│                  team_at_submission                                    │
│                  location_id                                           │
│                  custom_fields                                         │
│                          │                                             │
│                          │                                             │
│                          ▼                                             │
│                  ChecklistItemResponse                                 │
│                  =====================                                 │
│                  submission_id                                         │
│                  item_id                                               │
│                  is_checked                                            │
│                  evidence_data (JSONB)                                 │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌─────────────────── DYNAMIC CONFIGURATION ──────────────────────────────┐
│                                                                          │
│  ┌────────────────────┐              ┌──────────────────┐              │
│  │CustomEntityType    │◄─────────────│  CustomEntity    │              │
│  │==================  │              │ ================ │              │
│  │ id                 │              │ id               │              │
│  │ name               │              │ entity_type_id   │              │
│  │ display_name       │              │ data (JSONB)     │              │
│  │ field_definitions  │              │ created_by_id    │              │
│  │   (JSONB array)    │              └──────────────────┘              │
│  │ icon               │                                                 │
│  │ color              │   ┌─────────────────────┐                      │
│  └────────────────────┘   │SystemConfiguration  │                      │
│                            │==================== │                      │
│  Super Admin creates       │ key                 │                      │
│  entity types with         │ value (JSONB)       │                      │
│  custom field defs.        │ description         │                      │
│  No code changes!          │ category            │                      │
│                            │ data_type           │                      │
│                            │ modified_by_id      │                      │
│                            └─────────────────────┘                      │
│                                                                          │
│  Examples:                                                              │
│  - Equipment registers                                                  │
│  - Inspection forms                                                     │
│  - Incident reports                                                     │
│  - Any custom data structure                                            │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌────────────────────── AUDIT & HISTORY ─────────────────────────────────┐
│                                                                          │
│  ┌────────────────────────┐        ┌─────────────────────┐             │
│  │ OrganizationHistory    │        │    AuditLog         │             │
│  │ =====================  │        │ =================== │             │
│  │ entity_type            │        │ user_id             │             │
│  │ entity_id              │        │ action              │             │
│  │ action                 │        │ entity_type         │             │
│  │ previous_state (JSONB) │        │ entity_id           │             │
│  │ new_state (JSONB)      │        │ description         │             │
│  │ changes (JSONB)        │        │ old_values (JSONB)  │             │
│  │ changed_by_id          │        │ new_values (JSONB)  │             │
│  │ reason                 │        │ ip_address          │             │
│  │ ip_address             │        │ user_agent          │             │
│  │ created_at             │        │ success             │             │
│  └────────────────────────┘        │ created_at          │             │
│                                     └─────────────────────┘             │
│                                                                          │
│  Complete audit trail with before/after states                          │
│  Preserves all historical data - nothing ever truly deleted!            │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────── COMMUNICATION ─────────────────────────────────────┐
│                                                                          │
│  ┌─────────────────┐              ┌──────────────────┐                 │
│  │  Notification   │              │     Message      │                 │
│  │ =============== │              │ ================ │                 │
│  │ user_id         │              │ sender_id        │                 │
│  │ title           │              │ recipient_id     │                 │
│  │ message         │              │ subject          │                 │
│  │ type            │              │ body             │                 │
│  │ priority        │              │ is_read          │                 │
│  │ is_read         │              │ parent_msg_id    │                 │
│  │ action_url      │              │ thread_id        │                 │
│  │ related_entity  │              │ attachments      │                 │
│  │ sender_id       │              │ priority         │                 │
│  └─────────────────┘              └──────────────────┘                 │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────── LOCATION TRACKING ─────────────────────────────────┐
│                                                                          │
│  ┌─────────────────┐              ┌──────────────────┐                 │
│  │  UserLocation   │              │  LocationZone    │                 │
│  │ =============== │              │ ================ │                 │
│  │ user_id         │              │ name             │                 │
│  │ latitude        │              │ zone_type        │                 │
│  │ longitude       │              │ center_lat       │                 │
│  │ altitude        │              │ center_lon       │                 │
│  │ accuracy        │              │ radius_meters    │                 │
│  │ address         │              │ polygon_coords   │                 │
│  │ location_type   │              │ dept_id          │                 │
│  │ is_current      │              │ team_id          │                 │
│  │ related_entity  │              │ is_active        │                 │
│  │ custom_fields   │              └──────────────────┘                 │
│  └─────────────────┘                                                    │
│                                                                          │
│  Tracks: Check-ins, surveys, checklists, manual updates                 │
│  Supports: Geofencing with zones                                        │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                          KEY DESIGN FEATURES                             │
│                                                                          │
│  1. DYNAMIC FIELDS (JSONB)                                              │
│     All major tables have custom_fields column                          │
│     Super Admin can add fields without code changes                     │
│                                                                          │
│  2. SOFT DELETE                                                          │
│     Records marked is_deleted=True, never actually deleted              │
│     Preserves complete historical data                                  │
│                                                                          │
│  3. AUDIT TRAIL                                                          │
│     All changes tracked with before/after states                        │
│     Who, what, when, why, from where                                    │
│                                                                          │
│  4. HIERARCHICAL                                                         │
│     Users, departments support parent-child relationships               │
│     Unlimited depth, efficient queries                                  │
│                                                                          │
│  5. TEMPORAL CONTEXT                                                     │
│     Responses linked to hierarchy at submission time                    │
│     Even if org changes, history preserved correctly                    │
│                                                                          │
│  6. EXTENSIBLE                                                           │
│     Custom entity types for any new data structure                      │
│     No developer required to add new entities                           │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                         INDEXES & PERFORMANCE                            │
│                                                                          │
│  Strategic indexes on:                                                  │
│  • Foreign keys (user_id, dept_id, team_id, etc.)                       │
│  • Lookup fields (username, email, company_number)                      │
│  • Temporal queries (created_at, submission_date)                       │
│  • Status fields (is_deleted, is_active, is_current)                    │
│  • Location data (latitude, longitude)                                  │
│  • Composite indexes for common query patterns                          │
│                                                                          │
│  JSONB Support:                                                          │
│  • GIN indexes on custom_fields for fast queries                        │
│  • Supports nested JSON queries                                         │
│  • Native PostgreSQL operators (@>, ?, ?|, etc.)                        │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Example: Survey Submission

```
1. User Opens Survey
   ├─► Load survey questions from QuestionPool
   ├─► Check user's current location (UserLocation)
   └─► Display survey form

2. User Completes Survey
   ├─► Capture current location coordinates
   ├─► Record submission timestamp
   ├─► Capture organizational context:
   │   ├─► Current department
   │   ├─► Current team
   │   ├─► Current role
   │   └─► Full hierarchy path
   └─► Save all answers

3. System Saves Response
   ├─► Create SurveyResponse record
   │   ├─► Link to survey_id
   │   ├─► Link to user_id
   │   ├─► Save dept_id_at_submission
   │   ├─► Save team_id_at_submission
   │   ├─► Save role_id_at_submission
   │   ├─► Save hierarchy_path (JSONB)
   │   └─► Save location_id
   │
   ├─► Create SurveyAnswer records
   │   ├─► One per question
   │   ├─► Link to response_id
   │   ├─► Link to question_id
   │   └─► Save answer value(s)
   │
   ├─► Create UserLocation record
   │   ├─► Save coordinates
   │   ├─► Mark as current
   │   ├─► Link to response
   │   └─► Mark old locations as not current
   │
   └─► Create AuditLog entry
       ├─► Action: survey_submitted
       ├─► User ID
       ├─► Timestamp
       └─► IP address

4. Historical Integrity
   Even if user changes department later:
   ├─► Old response still shows correct dept at submission
   ├─► Hierarchy path preserved in JSONB
   ├─► Reports show accurate historical data
   └─► Audit trail complete
```

## Permission Flow Example

```
User Login
    ↓
Load User Record
    ├─► Get role_id
    │   ↓
    └─► Load Role Record
        ├─► Get permissions (JSONB)
        │   {
        │     "view_department_data": true,
        │     "create_surveys": true,
        │     "assign_checklists": true,
        │     "view_all_locations": false
        │   }
        │
        └─► Check Permission for Action
            ├─► if permissions['create_surveys'] == true
            │   └─► Allow survey creation
            │
            └─► if permissions['view_all_locations'] == false
                └─► Restrict to department locations only
```

---

**This architecture supports:**
- ✅ Unlimited organizational depth
- ✅ Dynamic field addition without migrations
- ✅ Complete historical preservation
- ✅ Flexible permissions
- ✅ Real-time location tracking
- ✅ Audit compliance
- ✅ Scalable to 10,000+ users
- ✅ Production-ready

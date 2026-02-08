# Tasks: Bronze Phase - AI Employee Foundation

**Input**: Design documents from `/specs/1-bronze-phase/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md

**Tests**: Tests are OPTIONAL for Bronze Phase - focus on manual verification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Vault root**: `D:\syeda Gulzar Bano\AI_Employee_Vault_`
- **Watchers**: `watchers/`
- **Skills**: `.claude/skills/`
- **Logs**: `Logs/`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Verify project structure and dependencies are ready

- [ ] T001 Verify Python 3.13+ is installed by running `python --version`
- [ ] T002 [P] Install dependencies from requirements.txt using `pip install -r requirements.txt`
- [ ] T003 [P] Verify watchdog is installed by running `python -c "import watchdog; print(watchdog.__version__)"`
- [ ] T004 Create .env file from .env.example with correct VAULT_PATH and DROP_FOLDER paths
- [ ] T005 Verify Obsidian can open the vault at `D:\syeda Gulzar Bano\AI_Employee_Vault_`

**Checkpoint**: Environment ready - all dependencies installed, vault accessible in Obsidian

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create watchers/__init__.py to make watchers a Python package
- [ ] T007 [P] Verify base_watcher.py exists and has BaseWatcher class in watchers/base_watcher.py
- [ ] T008 [P] Verify .gitignore includes .env, credentials, and sensitive files
- [ ] T009 [P] Verify .env.example has all required environment variables (DEV_MODE, DRY_RUN, VAULT_PATH, DROP_FOLDER)

**Checkpoint**: Foundation ready - watchers package initialized, security files in place

---

## Phase 3: User Story 1 - Initialize AI Employee Vault (Priority: P1)

**Goal**: Set up Obsidian vault with folder structure and core documents

**Independent Test**: Open Obsidian, verify all folders exist, Dashboard.md and Company_Handbook.md are readable

### Implementation for User Story 1

- [ ] T010 [US1] Verify folder /Needs_Action exists, create if missing
- [ ] T011 [P] [US1] Verify folder /Done exists, create if missing
- [ ] T012 [P] [US1] Verify folder /Logs exists, create if missing
- [ ] T013 [P] [US1] Verify folder /Inbox exists, create if missing
- [ ] T014 [P] [US1] Verify folder /Drop_Folder exists, create if missing
- [ ] T015 [US1] Verify Dashboard.md exists with all required sections (System Status, Pending Tasks, Recent Activity, Quick Stats)
- [ ] T016 [P] [US1] Verify Company_Handbook.md exists with Core Rules and Action Categories sections
- [ ] T017 [US1] Update vault-init.md skill in .claude/skills/vault-init.md to verify all folders and documents
- [ ] T018 [US1] Test vault-init skill by running Claude with "Initialize and verify my AI Employee vault"

**Checkpoint**: User Story 1 complete - vault structure verified, core documents accessible in Obsidian

---

## Phase 4: User Story 2 - FileSystem Watcher Detects Files (Priority: P1)

**Goal**: Python watcher monitors Drop_Folder and creates task files in /Needs_Action

**Independent Test**: Drop a file into Drop_Folder, verify .md task file appears in /Needs_Action within 5 seconds

### Implementation for User Story 2

- [ ] T019 [US2] Review filesystem_watcher.py in watchers/filesystem_watcher.py for completeness
- [ ] T020 [US2] Verify FileSystemWatcher class extends BaseWatcher correctly
- [ ] T021 [US2] Verify DropFolderHandler creates YAML frontmatter with type, status, timestamp fields
- [ ] T022 [US2] Verify task file naming follows pattern FILE_{original_name}.md
- [ ] T023 [US2] Add file size and file type detection to create_action_file method in watchers/filesystem_watcher.py
- [ ] T024 [US2] Verify log_action method writes to Logs/YYYY-MM-DD.json
- [ ] T025 [US2] Test watcher by running `python watchers/filesystem_watcher.py` and dropping a test file
- [ ] T026 [US2] Verify task file appears in /Needs_Action within 5 seconds of drop
- [ ] T027 [US2] Verify task file has correct YAML frontmatter (type: file_drop, status: pending)

**Checkpoint**: User Story 2 complete - FileSystem Watcher detects files and creates task files automatically

---

## Phase 5: User Story 3 - Claude Code Processes Tasks (Priority: P1)

**Goal**: Claude reads /Needs_Action files, processes them, updates Dashboard, moves to /Done

**Independent Test**: Place task file in /Needs_Action, run Claude, verify Dashboard updated and file in /Done

### Implementation for User Story 3

- [ ] T028 [US3] Review process-inbox.md skill in .claude/skills/process-inbox.md
- [ ] T029 [US3] Ensure process-inbox skill reads all .md files from /Needs_Action
- [ ] T030 [US3] Ensure process-inbox skill parses YAML frontmatter correctly
- [ ] T031 [US3] Ensure process-inbox skill generates summary for each task
- [ ] T032 [US3] Review update-dashboard.md skill in .claude/skills/update-dashboard.md
- [ ] T033 [US3] Ensure update-dashboard skill adds processed tasks to Recent Activity table
- [ ] T034 [US3] Ensure update-dashboard skill updates Pending Tasks count
- [ ] T035 [US3] Ensure update-dashboard skill updates Quick Stats section
- [ ] T036 [US3] Review log-action.md skill in .claude/skills/log-action.md
- [ ] T037 [US3] Ensure log-action skill appends to Logs/YYYY-MM-DD.json with correct schema
- [ ] T038 [US3] Create summarize-file.md skill in .claude/skills/summarize-file.md for file content summaries
- [ ] T039 [US3] Test full workflow: drop file → watcher creates task → Claude processes → Dashboard updates → file in /Done

**Checkpoint**: User Story 3 complete - Claude processes tasks end-to-end with logging

---

## Phase 6: User Story 4 - Agent Skills for AI Functionality (Priority: P2)

**Goal**: All AI functionality packaged as reusable Agent Skills

**Independent Test**: Run each skill command and verify expected behavior

### Implementation for User Story 4

- [ ] T040 [US4] Verify vault-init.md skill follows standard skill schema (Description, Phase, Trigger, Instructions, Success Criteria)
- [ ] T041 [P] [US4] Verify process-inbox.md skill follows standard skill schema
- [ ] T042 [P] [US4] Verify update-dashboard.md skill follows standard skill schema
- [ ] T043 [P] [US4] Verify log-action.md skill follows standard skill schema
- [ ] T044 [P] [US4] Verify summarize-file.md skill follows standard skill schema
- [ ] T045 [US4] Create skills index in .claude/skills/README.md listing all Bronze skills
- [ ] T046 [US4] Test vault-init skill: Claude should verify/create vault structure
- [ ] T047 [US4] Test process-inbox skill: Claude should process all /Needs_Action files
- [ ] T048 [US4] Test update-dashboard skill: Claude should refresh Dashboard.md
- [ ] T049 [US4] Document skill invocation examples in specs/1-bronze-phase/quickstart.md

**Checkpoint**: User Story 4 complete - all skills documented and tested

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and documentation

- [ ] T050 Run complete end-to-end test: watcher running → drop file → Claude processes → verify all outputs
- [ ] T051 [P] Verify all log entries follow JSON schema from data-model.md
- [ ] T052 [P] Verify Dashboard.md updates correctly with timestamps
- [ ] T053 [P] Update quickstart.md with any discovered issues or tips
- [ ] T054 Create demo script for hackathon presentation in specs/1-bronze-phase/demo-script.md
- [ ] T055 Verify system stability: run watcher for 10 minutes, process 5+ files without errors

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup
    ↓
Phase 2: Foundational
    ↓
Phase 3: US1 (Vault Init) ←──────┐
    ↓                            │
Phase 4: US2 (Watcher) ──────────┤ Can run in parallel after Phase 2
    ↓                            │
Phase 5: US3 (Processing) ───────┘
    ↓
Phase 6: US4 (Skills)
    ↓
Phase 7: Polish
```

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Phase 2 - Independent of US1
- **User Story 3 (P1)**: Requires US1 (vault structure) and US2 (watcher creates files)
- **User Story 4 (P2)**: Requires US1-3 complete (skills wrap functionality)

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T002 [P] Install dependencies
T003 [P] Verify watchdog
```

**Phase 2 (Foundational)**:
```
T007 [P] Verify base_watcher.py
T008 [P] Verify .gitignore
T009 [P] Verify .env.example
```

**Phase 3 (US1 - Vault Init)**:
```
T011 [P] Verify /Done
T012 [P] Verify /Logs
T013 [P] Verify /Inbox
T014 [P] Verify /Drop_Folder
T016 [P] Verify Company_Handbook.md
```

**Phase 6 (US4 - Skills)**:
```
T041 [P] Verify process-inbox.md
T042 [P] Verify update-dashboard.md
T043 [P] Verify log-action.md
T044 [P] Verify summarize-file.md
```

---

## Implementation Strategy

### MVP First (User Stories 1-3)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T009)
3. Complete Phase 3: User Story 1 - Vault Init (T010-T018)
4. Complete Phase 4: User Story 2 - Watcher (T019-T027)
5. Complete Phase 5: User Story 3 - Processing (T028-T039)
6. **STOP and VALIDATE**: Test complete workflow
7. Demo if ready for Bronze tier

### Full Bronze Delivery

1. Complete MVP (US1-3)
2. Complete Phase 6: User Story 4 - Skills (T040-T049)
3. Complete Phase 7: Polish (T050-T055)
4. Final demo and submission

---

## Task Summary

| Phase | Tasks | Parallel | Story |
|-------|-------|----------|-------|
| Setup | 5 | 2 | - |
| Foundational | 4 | 3 | - |
| US1: Vault Init | 9 | 5 | P1 |
| US2: Watcher | 9 | 0 | P1 |
| US3: Processing | 12 | 0 | P1 |
| US4: Skills | 10 | 4 | P2 |
| Polish | 6 | 3 | - |
| **Total** | **55** | **17** | - |

---

## Notes

- [P] tasks = different files, no dependencies
- [US#] label maps task to specific user story
- Each user story is independently testable
- Commit after each phase completion
- Run watcher in separate terminal during testing

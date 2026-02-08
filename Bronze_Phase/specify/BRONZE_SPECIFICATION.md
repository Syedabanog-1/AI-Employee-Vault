# Bronze Phase Specification

**Phase**: Bronze  
**Target**: Foundation (Minimum Viable Deliverable)  
**Estimated Time**: 8-12 hours

## Objectives
- Establish the core AI Employee architecture
- Implement basic file-based workflow system
- Create foundational components for the system

## Requirements
- Obsidian vault with Dashboard.md and Company_Handbook.md
- One working Watcher script (Gmail OR file system monitoring)
- Claude Code successfully reading from and writing to the vault
- Basic folder structure: /Inbox, /Needs_Action, /Done
- All AI functionality should be implemented as Agent Skills

## Components to Specify
1. **Vault Structure**
   - Dashboard.md - Real-time summary of activities
   - Company_Handbook.md - Rules of engagement
   - Business_Goals.md - Business objectives

2. **Folder Structure**
   - /Inbox - Incoming items to be categorized
   - /Needs_Action - Items requiring processing
   - /Done - Completed tasks
   - /Plans - Planning documents created by Claude
   - /Logs - Audit trail of all actions

3. **Watcher System**
   - BaseWatcher class with abstract methods
   - FileSystemWatcher for monitoring drop folder
   - Simple file processing workflow

4. **Orchestration**
   - Basic orchestrator to manage Claude interactions
   - File movement between folders
   - Dashboard updating mechanism

## Constraints
- Must use Claude Code as primary reasoning engine
- All data stored locally in Obsidian vault
- Human-in-the-loop for sensitive actions
- Privacy-focused architecture

## Success Criteria
- Claude can read files from Needs_Action
- Claude can write files to Plans and Done folders
- Dashboard updates automatically with activity
- Basic file monitoring works
- System follows Company_Handbook rules
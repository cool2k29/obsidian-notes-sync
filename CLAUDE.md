# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a trainee development project (研修生育成プロジェクト) designed to teach comprehensive software development skills through hands-on implementation of a complete CRUD application with JOIN operations and UI controls.

## Project Structure

```
アーキテクチャ設計資料/
├── 0-プロジェクト概要/     # Project overview and objectives
├── 1-要件定義/             # Requirements documentation
│   ├── 要件サマリー        # Requirements summary
│   ├── 要件定義書          # Detailed requirements
│   ├── 機能要件書          # Functional requirements
│   └── 非機能要件書        # Non-functional requirements
└── 2-詳細設計/             # Detailed design
    └── テーブル定義書      # Database table definitions
```

## Key System Components

### Core Entity: Entry
The system manages "Entry" records with these attributes:
- ID (auto-increment)
- Name (max 50 chars)
- Email (unique, email format)
- Category (General/VIP/Internal - dropdown)
- Status (Active/Inactive - radio)
- Tags (A/B/C/D - multi-select listbox)
- Newsletter Agreement (checkbox)
- Timestamps (created_at, updated_at)

### Database Schema
Seven main tables with relationships:
- **categories**, **statuses** - Master tables (INNER JOIN required)
- **entries** - Main data table
- **entry_tags** - Many-to-many relationship
- **tags** - Tag master
- **notes** - Optional notes (LEFT OUTER JOIN)
- **audit_logs** - Error and operation logging

### UI Pages
- **RegisterPage** - Create new entries
- **ListPage** - Search, filter, paginate (10 items/page)
- **DetailPage** - View single entry with delete option
- **UpdatePage** - Edit existing entries

## Critical Requirements

### Error Handling (NFR-002, NFR-003, NFR-004)
- ALL business logic and data access layers MUST implement try-catch blocks
- User-facing errors must be clear but not expose stack traces or sensitive data
- All unexpected exceptions MUST be logged to audit_logs table

### Data Validation
- Name: Required, max 50 characters
- Email: Required, unique, valid format
- Category: Required (FK to categories)
- Status: Required (FK to statuses)
- Tags: 0-4 selections allowed

### JOIN Operations
- **INNER JOIN** required for categories and statuses (NOT NULL FKs)
- **LEFT OUTER JOIN** for tags and notes (may not exist)

## Development Guidelines

### When implementing features:
1. Follow the numbered document structure (0-プロジェクト概要, 1-要件定義, etc.)
2. Implement complete CRUD operations with proper UI controls
3. Ensure all exceptions are caught and logged appropriately
4. Validate data according to VAL-001 through VAL-005 specifications
5. Use proper SQL JOINs as specified in the requirements

### Testing Requirements (TST-001 to TST-007)
- Test all input controls for two-way binding
- Verify validation rules
- Test search, filter, and pagination combinations
- Confirm delete operations with dialog
- Verify exception handling displays user-friendly messages
- Ensure sensitive information is never exposed to users

## API Endpoints (Reference)
- POST /api/entries - Create
- GET /api/entries - List (with query params)
- GET /api/entries/{id} - Detail
- PUT /api/entries/{id} - Update
- DELETE /api/entries/{id} - Delete

## Skill Level Assessment
The project defines skill levels 0-5 based on completion capability, from completing JUnit tests (Level 0) to unable to complete registration screen (Level 5).
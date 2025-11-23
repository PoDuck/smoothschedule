# CLAUDE.md - AI Assistant Guide for SmoothSchedule

## Repository Overview

**Project Name:** SmoothSchedule
**Repository:** PoDuck/smoothschedule
**Purpose:** Scheduling application (to be defined as development progresses)

This document serves as a comprehensive guide for AI assistants (like Claude) working on this codebase. It outlines the project structure, development workflows, coding conventions, and best practices to follow.

---

## Table of Contents

1. [Project Status](#project-status)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Development Workflows](#development-workflows)
5. [Coding Conventions](#coding-conventions)
6. [Git Workflow](#git-workflow)
7. [Testing Guidelines](#testing-guidelines)
8. [Documentation Standards](#documentation-standards)
9. [Common Tasks](#common-tasks)
10. [AI Assistant Guidelines](#ai-assistant-guidelines)

---

## Project Status

**Current State:** Two-repository architecture with Django backend
**Last Updated:** 2025-11-23

This repository contains the **Django backend** for SmoothSchedule, a multi-tenant SaaS scheduling platform. The React frontend is maintained separately in the `SmoothScheduleReact` repository and managed via Google AI Studio.

### Key Considerations for AI Assistants:
- This is the **backend only** - frontend is in a separate repository
- The `api-schema.ts` file is the **source of truth** for the API contract
- Always sync changes to the API contract between repositories
- Follow the handoff protocol when API changes are needed
- This repository is managed with Claude Code for backend development

---

## Technology Stack

### Backend (This Repository)
- **Framework:** Django 5.x with Django REST Framework (DRF)
- **Language:** Python 3.11+
- **Database:** PostgreSQL (production), SQLite (development)
- **Authentication:** JWT (djangorestframework-simplejwt)
- **API:** REST API following the contract in `api-schema.ts`
- **Multi-tenancy:** Subdomain-based tenant resolution

### Frontend (Separate Repository: `SmoothScheduleReact`)
- **Framework:** React 19.2 with TypeScript (strict mode)
- **Build Tool:** Vite
- **Styling:** Tailwind CSS (dark mode support)
- **Routing:** React Router v6
- **Icons:** Lucide React
- **Charts:** Recharts
- **AI:** Google Gemini API integration
- **Repository:** Managed via Google AI Studio

### Infrastructure
- **Deployment:** TBD (Docker, cloud platforms)
- **CI/CD:** GitHub Actions (TBD)

---

## Project Structure

### Two-Repository Architecture

This project uses a **two-repository strategy** to leverage the strengths of different AI tools:

**Repository 1: `smoothschedule` (This Repo)** - Backend (Claude Code)
```
smoothschedule/
├── backend/                 # Django project
│   ├── config/             # Django settings
│   ├── apps/               # Django apps
│   │   ├── core/          # Multi-tenancy, auth
│   │   ├── bookings/      # Appointments, availability
│   │   ├── resources/     # Resources, blockers
│   │   ├── customers/     # Customer management
│   │   └── payments/      # Payment processing
│   ├── manage.py
│   └── requirements.txt
├── docs/                    # API documentation
├── api-schema.ts           # **THE CONTRACT** (synced from frontend)
├── IMPLEMENTATION.md       # API implementation guide
├── HANDOFF.md              # Cross-repo sync protocol
├── CLAUDE.md               # This file
├── README.md
└── .gitignore
```

**Repository 2: `SmoothScheduleReact`** - Frontend (Google AI Studio)
```
SmoothScheduleReact/
├── components/             # React components
├── pages/                  # Route pages
├── layouts/                # Layout wrappers
├── api-schema.ts          # **THE CONTRACT** (source of truth)
├── types.ts               # UI-specific types
├── mockData.ts            # Development data
├── App.tsx                # Main application
├── CLAUDE.md              # Frontend guide
├── IMPLEMENTATION.md      # API requirements
└── package.json
```

### The Contract: `api-schema.ts`

This TypeScript file defines all data structures exchanged between frontend and backend. It must be kept in sync between both repositories using the handoff protocol (see `HANDOFF.md`).

---

## Development Workflows

### Two-Repository Workflow

This project uses **separate repositories** for frontend and backend development:

- **Frontend:** Edited via Google AI Studio (SmoothScheduleReact repo)
- **Backend:** Edited via Claude Code (this repo)
- **Contract:** `api-schema.ts` serves as the bridge between them

**See `HANDOFF.md` for detailed sync protocol.**

### Setting Up Backend Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/PoDuck/smoothschedule.git
   cd smoothschedule
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your database settings, secret key, etc.
   ```

5. **Run migrations:**
   ```bash
   cd backend
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server:**
   ```bash
   python manage.py runserver
   ```

### Development Branch Strategy

- **Main branches:**
  - `main` or `master` - production-ready code
  - `develop` - integration branch for features

- **Feature branches:**
  - AI assistants work on branches with pattern: `claude/claude-md-<session-id>`
  - Format: `claude/claude-md-{identifier}-{session-id}`
  - Example: `claude/claude-md-mib4vhk5goq5jrjf-01Jsg7bGSDF2Si3FytxPaew4`

### Code Review Process

1. Make changes on feature branch
2. Commit with descriptive messages
3. Push to remote: `git push -u origin <branch-name>`
4. Create pull request for review
5. Address feedback and merge when approved

---

## Coding Conventions

### General Principles

1. **Write Clean, Readable Code**
   - Use meaningful variable and function names
   - Keep functions small and focused on a single responsibility
   - Avoid deep nesting (max 3-4 levels)

2. **Follow DRY (Don't Repeat Yourself)**
   - Extract common logic into reusable functions/modules
   - Avoid code duplication

3. **YAGNI (You Aren't Gonna Need It)**
   - Don't add functionality until it's needed
   - Avoid over-engineering solutions
   - Keep solutions simple and focused

4. **Error Handling**
   - Validate input at system boundaries (user input, API calls)
   - Use appropriate error handling mechanisms
   - Provide meaningful error messages

5. **Security Best Practices**
   - Never commit secrets, API keys, or credentials
   - Validate and sanitize user input
   - Protect against common vulnerabilities (XSS, SQL injection, CSRF, etc.)
   - Use parameterized queries for database operations
   - Implement proper authentication and authorization

### Language-Specific Conventions

**Python/Django:**
- Follow PEP 8 style guide
- Use `black` for code formatting (line length: 100)
- Use `isort` for import sorting
- Use `flake8` for linting
- Type hints for function signatures (Python 3.11+)
- Docstrings for all public functions, classes, and modules
- Django models: Use `verbose_name` and `help_text`
- Django views: Use class-based views (ViewSets for DRF)
- Queries: Always filter by tenant to ensure data isolation
- Naming: `snake_case` for functions/variables, `PascalCase` for classes

### Code Formatting

- Use a consistent code formatter (e.g., Prettier, Black, gofmt)
- Configure editor to format on save
- Include formatter config in repository

### Comments and Documentation

- Write self-documenting code where possible
- Add comments for complex logic or non-obvious decisions
- Document the "why" not the "what"
- Keep comments up-to-date with code changes

---

## Git Workflow

### Branch Naming

- Feature branches: `feature/<description>` or `claude/<session-id>`
- Bug fixes: `fix/<description>`
- Documentation: `docs/<description>`

### Commit Messages

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(auth): add user authentication with JWT

Implement JWT-based authentication system with login/logout endpoints.
Include refresh token mechanism for extended sessions.

feat(scheduler): implement recurring event support

fix(api): resolve timezone handling in event creation

docs(readme): add setup instructions for local development
```

### Push Workflow

When pushing to remote:
```bash
git push -u origin <branch-name>
```

- Always use `-u` flag for first push to set upstream
- Branch must follow naming convention: `claude/*`
- Retry failed pushes up to 4 times with exponential backoff (2s, 4s, 8s, 16s)

### Pull Request Guidelines

1. **PR Title:** Clear, descriptive summary of changes
2. **Description:** Include:
   - What changed and why
   - How to test the changes
   - Any breaking changes or migrations needed
   - Screenshots for UI changes
3. **Checklist:**
   - Tests added/updated
   - Documentation updated
   - No merge conflicts
   - Follows code style guidelines

---

## Testing Guidelines

### Test Coverage Goals

- Aim for 80%+ code coverage
- All critical paths must be tested
- Test edge cases and error conditions

### Test Organization

```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Tests of multiple components
└── e2e/           # Full application flow tests
```

### Testing Best Practices

1. **Write Tests First (TDD when appropriate)**
   - Define expected behavior before implementation
   - Helps design better APIs

2. **Test Naming**
   - Descriptive test names: `test_user_can_create_event_with_valid_data`
   - Clearly state what's being tested and expected outcome

3. **Test Structure**
   - Arrange: Set up test data and conditions
   - Act: Execute the code being tested
   - Assert: Verify expected outcomes

4. **Mock External Dependencies**
   - Don't make real API calls in tests
   - Use mocks/stubs for databases, external services

5. **Keep Tests Fast**
   - Unit tests should run in milliseconds
   - Optimize or parallelize slow test suites

### Running Tests

```bash
# Update with actual commands once framework is chosen
# npm test
# pytest
# go test ./...
```

---

## Documentation Standards

### Code Documentation

1. **Functions/Methods:**
   - Document purpose, parameters, return values
   - Include examples for complex functions

2. **Classes:**
   - Describe responsibility and key methods
   - Document relationships with other classes

3. **Modules/Packages:**
   - Overview of functionality
   - Usage examples

### Project Documentation

1. **README.md:**
   - Project overview
   - Quick start guide
   - Installation instructions
   - Basic usage examples

2. **CONTRIBUTING.md:**
   - How to contribute
   - Development setup
   - Code review process

3. **API Documentation:**
   - Endpoint descriptions
   - Request/response examples
   - Authentication requirements
   - Error codes

---

## Common Tasks

### Adding a New Feature

1. Create feature branch from `develop` or `main`
2. Implement feature with tests
3. Update documentation
4. Commit with descriptive message
5. Push and create pull request
6. Address review feedback

### Fixing a Bug

1. Create fix branch
2. Add test that reproduces the bug
3. Fix the bug (test should pass)
4. Commit and push
5. Create pull request with bug description

### Refactoring Code

1. Ensure existing tests pass
2. Make incremental refactoring changes
3. Run tests after each change
4. Update documentation if needed
5. Commit with clear refactoring description

### Updating Dependencies

1. Check for security vulnerabilities
2. Update one dependency at a time (or related group)
3. Run full test suite
4. Test critical user flows manually
5. Document any breaking changes

---

## AI Assistant Guidelines

### Core Principles for AI Assistants

1. **Read Before Modifying**
   - ALWAYS read files before suggesting changes
   - Understand existing code patterns and conventions
   - Match the style of the existing codebase

2. **Avoid Over-Engineering**
   - Only make requested changes
   - Don't add unrequested features or refactoring
   - Keep solutions simple and focused
   - Don't add abstractions for one-time operations

3. **Security First**
   - Never introduce security vulnerabilities
   - Validate user input at boundaries
   - Use parameterized queries
   - Don't commit secrets or credentials

4. **Be Incremental**
   - Make small, focused changes
   - Test after each change
   - Commit frequently with clear messages

5. **Ask When Uncertain**
   - Clarify requirements if ambiguous
   - Confirm architectural decisions
   - Check before making breaking changes

### Task Management

Use the TodoWrite tool for:
- Multi-step tasks (3+ steps)
- Complex features requiring planning
- Bug fixes with multiple related changes
- When user provides multiple tasks

**Task workflow:**
1. Create todos at start of work
2. Mark task as `in_progress` before starting
3. Complete tasks one at a time
4. Mark `completed` immediately after finishing
5. Only one task `in_progress` at a time

### File Operations

**Prefer specialized tools:**
- `Read` for reading files (not `cat`)
- `Edit` for modifying files (not `sed`/`awk`)
- `Write` for creating files (not `echo >`)
- `Grep` for searching code (not `grep` command)
- `Glob` for finding files (not `find`)

### Communication Style

- Be concise and technical
- Focus on facts over validation
- Output text directly (not through bash `echo`)
- Use markdown for formatting
- Avoid emojis unless requested

### Git Operations

**Committing:**
- Only commit when requested
- Never skip hooks (no `--no-verify`)
- Use heredoc for commit messages
- Check `git status` and `git diff` before committing
- Add relevant files to staging area

**Pull Requests:**
- Analyze all commits in PR (not just latest)
- Create descriptive PR summary
- Include test plan
- Push with `-u` flag: `git push -u origin <branch>`

### Code Review Checklist

Before committing, verify:
- [ ] Code follows project conventions
- [ ] Tests added/updated and passing
- [ ] No security vulnerabilities introduced
- [ ] Documentation updated if needed
- [ ] No secrets or credentials in code
- [ ] Error handling is appropriate
- [ ] Code is readable and maintainable
- [ ] No unnecessary complexity added

### Exploration and Research

For open-ended questions about the codebase:
- Use `Task` tool with `subagent_type=Explore`
- Don't run searches directly for broad questions
- Examples: "How does authentication work?", "What's the codebase structure?"

For specific file/class/function searches:
- Use `Grep` or `Glob` directly
- Example: "Find the User class definition"

### Common Pitfalls to Avoid

1. ❌ Don't add features not explicitly requested
2. ❌ Don't refactor code unless asked
3. ❌ Don't add comments to unchanged code
4. ❌ Don't create abstractions prematurely
5. ❌ Don't add error handling for impossible scenarios
6. ❌ Don't keep backwards-compatibility hacks (renaming `_vars`, etc.)
7. ❌ Don't guess at file paths - read or search first
8. ❌ Don't use bash for file operations - use specialized tools
9. ❌ Don't create documentation files unless requested
10. ❌ Don't batch multiple todo completions - mark done immediately

### What to Do Instead

1. ✅ Read existing code before modifying
2. ✅ Make minimal, focused changes
3. ✅ Delete unused code completely
4. ✅ Ask for clarification when uncertain
5. ✅ Use specialized tools (Read, Edit, Grep, Glob)
6. ✅ Update this CLAUDE.md as patterns emerge
7. ✅ Follow existing code style and conventions
8. ✅ Test changes thoroughly
9. ✅ Commit with clear, descriptive messages
10. ✅ Track complex tasks with TodoWrite

---

## Project Evolution

This CLAUDE.md file should evolve with the project. Update it when:

- Technology stack is chosen or changed
- New coding conventions are established
- Project structure changes significantly
- New development tools are added
- Common issues or patterns emerge
- Best practices are refined

**Last Updated:** 2025-11-23
**Version:** 1.0.0 (Initial)

---

## Questions or Issues?

For questions about:
- **Project decisions:** Consult with the repository owner
- **Technical implementation:** Check existing code patterns first
- **This guide:** Suggest updates via pull request

---

*This guide is a living document. Keep it updated as the project grows.*

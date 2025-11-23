# PyCharm Setup Guide for SmoothSchedule

This guide will help you configure PyCharm Professional for optimal Django development with Docker.

## Prerequisites

- PyCharm Professional (required for Django and Docker support)
- Docker Desktop installed and running
- Python 3.11+

---

## Quick Setup

### 1. Open Project in PyCharm

```bash
# Clone repository (if not already done)
git clone https://github.com/PoDuck/smoothschedule.git
cd smoothschedule

# Open in PyCharm
pycharm .
```

Or: File → Open → Select `smoothschedule` directory

### 2. Configure Python Interpreter

#### Option A: Use Docker Compose (Recommended)

1. **File → Settings → Project → Python Interpreter**
2. Click **Add Interpreter** (gear icon) → **On Docker Compose**
3. Select **docker-compose.yml**
4. Service: **django**
5. Click **OK**

PyCharm will now use the Python environment inside your Docker container.

#### Option B: Use Local Virtual Environment

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements/local.txt
```

Then in PyCharm:
1. **File → Settings → Project → Python Interpreter**
2. Click **Add Interpreter** → **Virtualenv Environment**
3. **Existing environment**
4. Browse to `backend/venv/bin/python`
5. Click **OK**

### 3. Enable Django Support

1. **File → Settings → Languages & Frameworks → Django**
2. ✅ Enable Django Support
3. **Django project root:** `backend`
4. **Settings:** `config/settings/local.py`
5. **Manage script:** `manage.py`
6. Click **OK**

### 4. Configure Database (PostgreSQL)

1. **View → Tool Windows → Database** (or click Database tab)
2. Click **+** → **Data Source** → **PostgreSQL**
3. **Host:** localhost
4. **Port:** 5432
5. **Database:** smoothschedule
6. **User:** smoothschedule
7. **Password:** smoothschedule
8. Click **Test Connection** → Should succeed
9. Click **OK**

Now you can browse database tables, run SQL queries, etc.

### 5. Configure Docker Integration

1. **File → Settings → Build, Execution, Deployment → Docker**
2. Click **+** to add Docker
3. **Connect to Docker daemon with:** Docker for Mac/Windows
4. **Docker Compose executable:** (auto-detected)
5. Click **OK**

### 6. Mark Directories

Right-click on directories and mark them:
- **backend** → Mark Directory as → **Sources Root**
- **backend/apps** → Mark Directory as → **Sources Root**
- **backend/staticfiles** → Mark Directory as → **Excluded**
- **backend/media** → Mark Directory as → **Excluded**
- **backend/venv** → Mark Directory as → **Excluded**

---

## Run Configurations

Pre-configured run configurations are included in `.idea/runConfigurations/`. These should appear automatically in your Run menu:

### Available Configurations

1. **Docker Compose: Up** - Start all services
2. **Django Server** - Run Django development server
3. **Django Shell** - Interactive Django shell (shell_plus)
4. **Make Migrations** - Create database migrations
5. **Django Migrations** - Apply database migrations
6. **pytest: All Tests** - Run all tests with coverage
7. **Black: Format Code** - Format code with Black

### How to Use

Click the **Run Configuration** dropdown (top right) → Select configuration → Click **Run** (▶) or **Debug** (🐛)

---

## Code Quality Tools

### Black (Auto-formatting)

**Option 1: Run Configuration**
- Select **Black: Format Code** → Run

**Option 2: File Watcher (Auto-format on save)**
1. **File → Settings → Tools → File Watchers**
2. Click **+** → **Black**
3. **Program:** `$PROJECT_DIR$/backend/venv/bin/black`
4. **Arguments:** `$FilePath$`
5. **Working directory:** `$ProjectFileDir$`
6. Click **OK**

Now files auto-format when you save!

### Configure Black in PyCharm

1. **File → Settings → Tools → Black**
2. **Black executable:** `backend/venv/bin/black`
3. **Line length:** 100
4. ✅ **On save**
5. Click **OK**

### Flake8 (Linting)

1. **File → Settings → Tools → External Tools**
2. Click **+** to add tool
3. **Name:** Flake8
4. **Program:** `$PROJECT_DIR$/backend/venv/bin/flake8`
5. **Arguments:** `$FilePath$`
6. **Working directory:** `$ProjectFileDir$`
7. Click **OK**

Run: **Tools → External Tools → Flake8**

### isort (Import Sorting)

1. **File → Settings → Tools → External Tools**
2. Click **+** to add tool
3. **Name:** isort
4. **Program:** `$PROJECT_DIR$/backend/venv/bin/isort`
5. **Arguments:** `$FilePath$`
6. **Working directory:** `$ProjectFileDir$`
7. Click **OK**

Run: **Tools → External Tools → isort**

---

## Debugging

### Debug Django Server

1. Set breakpoint (click left margin of code line)
2. Select **Django Server** configuration
3. Click **Debug** (🐛) instead of Run
4. Make request to trigger breakpoint
5. Use debugger controls to step through code

### Debug Tests

1. Right-click on test file/function
2. Select **Debug 'pytest in ...'**
3. Breakpoints will work in tests

### Debug Docker Container

1. Select **Docker Compose: Up** configuration
2. Click **Debug** (🐛)
3. Set breakpoints in code
4. Attach debugger to running container

---

## Useful PyCharm Features

### Django-Specific

- **Ctrl + Click** on model field → Jump to definition
- **Ctrl + Click** on URL name → Jump to view
- **Ctrl + Space** → Autocomplete Django model fields, query methods
- **Alt + Enter** on model → Quick actions (migrations, admin, etc.)

### Database

- **Database tool window** → Browse tables, run SQL
- Right-click table → **Dump Data to File** → Export
- Right-click table → **Import Data from File**
- **Console** tab → Run SQL queries

### Git Integration

- **Git tool window** (bottom) → View commits, branches
- **Ctrl + K** → Commit changes
- **Ctrl + Shift + K** → Push
- **Alt + 9** → Show Git log

### Docker

- **Services tool window** → View running containers
- Right-click container → **Exec → /bin/bash** → Terminal inside container
- View logs, inspect environment, restart containers

---

## Testing in PyCharm

### Run All Tests

1. Select **pytest: All Tests** configuration
2. Click **Run** (▶)
3. View results in **Run tool window**

### Run Single Test

- Right-click test file → **Run 'pytest in test_file.py'**
- Right-click test function → **Run 'pytest in test_function'**

### Coverage

The **pytest: All Tests** configuration includes coverage:
```
--cov=apps --cov-report=html
```

After running tests:
1. Open `backend/htmlcov/index.html` in browser
2. See coverage report with line-by-line breakdown

---

## Keyboard Shortcuts

### Essential

- **Ctrl + Space** → Autocomplete
- **Ctrl + Click** → Go to definition
- **Alt + Enter** → Quick fix / suggestions
- **Ctrl + B** → Go to declaration
- **Ctrl + Alt + L** → Reformat code
- **Ctrl + /** → Comment/uncomment line
- **Shift + Shift** → Search everywhere

### Django-Specific

- **Ctrl + Alt + R** → Run manage.py command
- **Ctrl + Shift + R** → Run configuration (custom)

### Refactoring

- **Shift + F6** → Rename (class, function, variable)
- **Ctrl + Alt + M** → Extract method
- **Ctrl + Alt + V** → Extract variable
- **Ctrl + Alt + C** → Extract constant

---

## Troubleshooting

### "Module not found" errors

1. Check Python interpreter is set correctly
2. Mark `backend` and `backend/apps` as **Sources Root**
3. Invalidate caches: **File → Invalidate Caches → Invalidate and Restart**

### Django features not working

1. Verify Django support is enabled: **Settings → Django**
2. Check **Django project root** is set to `backend`
3. Check **Settings** points to `config/settings/local.py`

### Docker not connecting

1. Ensure Docker Desktop is running
2. **Settings → Docker** → Test connection
3. Restart PyCharm

### Tests not discovering

1. **Settings → Python Integrated Tools**
2. **Default test runner:** pytest
3. **pytest.ini or pyproject.toml** should be auto-detected

### Database connection fails

1. Ensure `docker-compose up` is running
2. Check PostgreSQL is running: `docker-compose ps postgres`
3. Verify credentials match `docker-compose.yml`

---

## Advanced Tips

### Multiple Django Settings

Create run configurations for different settings:

1. Duplicate **Django Server** configuration
2. Change **Environment variables** → `DJANGO_SETTINGS_MODULE=config.settings.production`
3. Rename to **Django Server (Production)**

### Custom Manage.py Commands

1. **Run → Edit Configurations**
2. Click **+** → **Python**
3. **Script path:** `backend/manage.py`
4. **Parameters:** `your_custom_command`
5. **Environment variables:** `DJANGO_SETTINGS_MODULE=config.settings.local`

### Django Console

1. **Tools → Run manage.py Task** (Ctrl + Alt + R)
2. Type command: `shell`, `dbshell`, `migrate`, etc.
3. Press Enter

Or use **Django Shell** run configuration for interactive shell_plus.

---

## Recommended Plugins

1. **File → Settings → Plugins**
2. Search and install:
   - **.ignore** - Gitignore support
   - **Rainbow Brackets** - Colorize brackets
   - **String Manipulation** - String case conversion
   - **Markdown** - Markdown preview (built-in)

---

## Next Steps

1. ✅ Configure Python interpreter
2. ✅ Enable Django support
3. ✅ Set up database connection
4. ✅ Mark source directories
5. ✅ Run **Docker Compose: Up**
6. ✅ Run **Django Migrations**
7. ✅ Run **Django Server**
8. ✅ Open http://localhost:8000/admin/
9. ✅ Start coding!

---

**Happy Coding!** 🚀

For issues, check:
- PyCharm logs: **Help → Show Log in Finder/Explorer**
- Docker logs: **Services tool window → Container → Logs**
- Django logs: **Run tool window**

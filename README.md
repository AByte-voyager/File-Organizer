# 🗃️ File Organizer with Logging and SQLite Tracking

This project is a **hybrid Python and Bash tool** that automatically organizes files in a given directory by **file type** and **modification year**, while keeping track of every operation through both a human-readable log file and a structured SQLite database. It also provides optional cleanup of old folders, safe conflict handling, and system-level backup control—all done transparently with minimal user input.

---

## 🎯 Purpose

Over time, folders like *Downloads*, *Documents*, or *Shared Drives* get cluttered with random files. Manually organizing them is tedious and error-prone. This project automates the task to:

- Keep files organized and easy to find.
- Maintain a history of changes (for transparency and tracking).
- Allow safe deletion of unnecessary folders after sorting.
- Prevent accidental overwrites through conflict resolution.
- Empower users with both file-level logs and database-level records.

---

## 🛠️ How It Works

### 📁 File Categorization
The Python script categorizes files into 5 main types:
- `Documents` (`.doc`, `.docx`)
- `Images` (`.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`)
- `PDFs` (`.pdf`)
- `Videos` (`.mp4`)
- `Others` (anything else)

Each file is moved into a subfolder like `Images/2023/` based on its last modified year.

### 🔀 Conflict Handling
If a file with the same name already exists in the destination, it is **renamed with a suffix** (e.g., `file(1).pdf`) to avoid overwriting.

### 🗃️ Database Logging
Every move is logged into a local SQLite database (`file_organization.db`) with the following fields:
- Filename
- File Type
- Original Path
- New Path
- Timestamp of Move

This allows future querying or reporting.

### 📜 Log File
A human-readable log (`file_organization.log`) is maintained, which appends timestamps for each folder deletion in the format:
### 🧹 Folder Deletion
You’ll be prompted whether you want to **delete original folders** after organizing. Only folders that existed before the sort are considered, protecting important system folders.

### 🔐 Safe Bash Backups
A Bash wrapper script:
- Backs up the target directory before making changes.
- Calls the Python script.
- Appends log entries with real system time.
- Optionally deletes the backup if everything succeeds.

---

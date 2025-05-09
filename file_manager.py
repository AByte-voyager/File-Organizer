import sys
import os
import shutil
import datetime
import sqlite3

def handleConflicts(dest_path):
    if os.path.exists(dest_path):
        base, ext = os.path.splitext(dest_path)
        i = 1
        new_dest = base + "(" + str(i) + ")" + ext
        while os.path.exists(new_dest):
            i += 1
            new_dest = base + "(" + str(i) + ")" + ext
        return new_dest
    return dest_path

def filetype(file):
    ext = os.path.splitext(file)[1].lower()
    if ext in ['.doc', '.docx']:
        return "Documents"
    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
        return "Images"
    elif ext in ['.pdf']:
        return "PDFs"
    elif ext in ['.mp4']:
        return "Videos"
    else:
        return "Others"
    
def log_file_move(db_connection, filename, file_type, original_path, new_path):
    cursor = db_connection.cursor()
    mod_time = datetime.datetime.now().isoformat()
    cursor.execute("INSERT INTO file_log (filename, file_type, original_path, new_path, modification_date) VALUES (?, ?, ?, ?, ?)", 
                   (filename, file_type, original_path, new_path, mod_time))
    db_connection.commit()

def log_deleted_dir(db_connection, dir_path):
    cursor = db_connection.cursor()
    deletion_time = datetime.datetime.now().isoformat()
    cursor.execute("INSERT INTO deleted_dirs (dir_path, deletion_date) VALUES (?, ?)", 
                   (dir_path, deletion_time))
    db_connection.commit()

def main():
    if len(sys.argv) < 2:
        print("Usage: python file_manager.py <folder_path>")
        return
    folder_path = sys.argv[1].strip()

    db_connection = sqlite3.connect('file_organization.db')
    cursor = db_connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS file_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        file_type TEXT,
        original_path TEXT,
        new_path TEXT,
        modification_date TIMESTAMP
    )''')
    db_connection.commit()

    toDelete = input("Do you want to delete the subdirectories after organizing? (Y/N): ").strip().lower()
    if (toDelete in ['y', 'yes', '1'] ):
        original_subdirs = set()
        destination_folders = {'Documents', 'Images', 'PDFs', 'Videos', 'Others'}
        for item in os.listdir(folder_path):
            full_path = os.path.join(folder_path, item)
            if os.path.isdir(full_path) and item not in destination_folders:
                original_subdirs.add(full_path)

    for current_dir, _, file_list in os.walk(folder_path):
        if any(current_dir.startswith(os.path.join(folder_path, x)) for x in ['Documents', 'Images', 'PDFs', 'Videos', 'Others']):
            continue
        for file in file_list:
            full_file_path = os.path.join(current_dir, file)
            if os.path.isfile(full_file_path):  
                category = filetype(file)
                mod_time = os.path.getmtime(full_file_path)
                year = datetime.datetime.fromtimestamp(mod_time).year
                target_dir = os.path.join(folder_path, category, str(year))
                os.makedirs(target_dir, exist_ok=True)
                dest_path = os.path.join(target_dir, file)
                dest_path = handleConflicts(dest_path)
                shutil.move(full_file_path, dest_path)
                log_file_move(db_connection, file, category, full_file_path, dest_path)
    print("Files organized successfully.")
    
    if (toDelete in ['y', 'yes', '1']):
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS deleted_dirs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dir_path TEXT,
            deletion_date TIMESTAMP
        )''')
        db_connection.commit()
        for dir_path in original_subdirs:
            try:
                shutil.rmtree(dir_path)
                log_deleted_dir(db_connection, dir_path)
                with open("file_organization.log", "a") as f:
                    timestamp = datetime.datetime.now().astimezone().strftime("%a %b %e %H:%M:%S %Z %Y")
                    f.write(f"{timestamp} - Deleted original directory: {dir_path}\n")
            except Exception as e:
                with open("file_organization.log", "a") as f:
                    timestamp = datetime.datetime.now().astimezone().strftime("%a %b %e %H:%M:%S %Z %Y")
                    f.write(f"{timestamp} - Failed to delete {dir_path}: {e}\n")    
    db_connection.close()

if __name__ == "__main__":
    main()


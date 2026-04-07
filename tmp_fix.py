import glob

for filepath in glob.glob("app/models/*.py"):
    with open(filepath, "r") as f:
        content = f.read()
    
    modified = False
    if "Column(DateTime)" in content:
        content = content.replace("Column(DateTime)", "Column(DateTime(timezone=True))")
        modified = True
    if "Column(DateTime," in content:
        content = content.replace("Column(DateTime,", "Column(DateTime(timezone=True),")
        modified = True
        
    if modified:
        print(f"Updated {filepath}")
        with open(filepath, "w") as f:
            f.write(content)

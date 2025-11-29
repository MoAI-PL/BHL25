# create_tests.py
from pathlib import Path
from datetime import datetime

start = 4
end = 50
ext = ".py"  # zmień na .cs, .java itp.

for i in range(start, end+1):
    filename = Path(f"test{i}{ext}")
    if filename.exists():
        print(f"{filename} już istnieje — pomijam")
    else:
        content = f"Test file #{i}\nCreated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        filename.write_text(content, encoding="utf-8")
        print(f"Utworzono {filename}")

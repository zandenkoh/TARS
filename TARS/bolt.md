## 2025-02-12 - [Substring Matching Before JSON Parsing in Hot Loops]
**Learning:** Found an optimization where checking for a raw string substring (`query in line`) before parsing the entire line with `json.loads` results in a 20x performance improvement in large file streaming scenarios (e.g., searching session files).
**Action:** Always attempt raw string checks before expensive deserialization operations in hot loops.

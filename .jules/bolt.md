## 2025-03-31 - Pre-compiling RegEx in Web Tools
**Learning:** During extensive web scraping and formatting inside `TARS/agent/tools/web.py` (e.g. `_strip_tags`, `_normalize`, `_to_markdown`), the system heavily relies on `re.sub()`. For large strings or heavy tool usage, dynamically recompiling the same regex expressions continuously wastes CPU cycles and slows down operations. This is especially true for hot-path regex strings containing flags like `re.I`.
**Action:** Always pre-compile regular expressions (`re.compile`) at the module level for repetitive text processing loops and scraping modules to reduce regex overhead and maintain speed.
## 2025-03-31 - Pre-compiling Regex in Hot Paths
**Learning:** In highly-frequented data pathways like log parsing, string formatting or URL extractions (e.g. inside `TARS/agent/tools/shell.py`, `TARS/channels/email.py`, and `TARS/channels/slack.py`), regex operations built directly within a function via `re.sub()`, `re.search()` or `re.findall()` are forced to recompile (or query an internal regex cache) repeatedly. While Python's internal cache is helpful, avoiding this lookup inside loop bodies or frequently-called class methods significantly reduces CPU overhead, improving end-to-end processing speeds of streaming text and messages.
**Action:** Always refactor constant regular expressions to use `re.compile()` at the class or module level, avoiding recompilation within function bodies. Where user inputs or configuration variables are involved (e.g., Slack's `_bot_user_id`), compile and cache the regex once at initialization time or the first time the configuration value is confirmed.
## 2026-04-01 - Avoid Heavy JSON Parsing for Content Search
**Learning:** In the `SessionManager.search_sessions` method, loading the entire chat history for every session into memory via `self._load(key)` (which invokes `json.loads` on every line) was a severe bottleneck for users with long histories performing searches. This caused large memory allocations and CPU spikes when we only needed to perform a simple substring match to find a specific keyword.
**Action:** When searching or filtering large structured text files like JSONL logs or chat histories, stream the file line-by-line using `open()` and perform a raw string substring match (`query in line`) *before* invoking the expensive `json.loads()`. Only parse the line if the raw string check succeeds to confirm field constraints.
## 2026-04-01 - [Pre-compile regex inside formatting hot paths]
**Learning:** Re-evaluating `re.fullmatch(pattern)` inside a text replacement hook (e.g. `_convert_table`) incurs redundant regex compilation on each match. While individual table conversions are fast, they block the event loop in `asyncio` if processing heavily markdown-formatted chat histories.
**Action:** Replace dynamically compiled regex with class-level pre-compiled regex objects (`cls._TABLE_SEP_RE.fullmatch`) to avoid recompilation overhead in hot loops.
## 2026-04-01 - Global Cache for Heavy Initialization Tasks
**Learning:** Calling initialization methods like `tiktoken.get_encoding("cl100k_base")` repeatedly inside highly-frequent utility functions (such as token estimators for messages) adds significant and measurable overhead to execution times, especially when generating stream chunks or processing histories.
**Action:** When a static dependency like a token encoder is needed across multiple frequent function calls, declare a module-level variable to cache the result lazily (e.g., via a helper `_get_tiktoken_encoding()`) instead of retrieving it each time.
## 2026-04-01 - O(N^2) String Slicing in chunking loops
**Learning:** `split_message` previously relied on repeatedly making copies of large strings via `content = content[pos:].lstrip()` inside a `while` loop, resulting in a performance bottleneck (O(n²) time complexity for large texts) due to heavy memory allocation.
**Action:** When iterating over a long string to yield pieces (e.g. for chunked pagination or length-splitting), do not mutate or reassign slices of the large string to the same variable. Instead, use an integer pointer index (e.g. `start`) to track progress and only slice out the necessary sub-string piece at each step (`content[start:pos]`), keeping processing complexity to O(N).

## 2025-04-01 - [Fast-Path Token Estimation Optimization]
**Learning:** Using EAFP (Easier to Ask for Forgiveness than Permission) list comprehensions combined with localized variable lookups (e.g. `append = parts.append`, `json.dumps = dumps`) can massively speed up heavy text string construction pipelines like Tiktoken message compilation, bypassing slow generic loop parsing loops when plain strings are common.
**Action:** Always look for 'fast path' scenarios in extremely frequent utility functions where standard iterations can be bypassed entirely using conditional shortcuts.

## 2026-04-01 - Avoid Regex for Simple Substring Manipulations
**Learning:** In frequently called text processing functions (like `strip_think` handling continuous streaming of large thought blocks from models like deepseek-r1), compiling and using regex to remove specific tag blocks (e.g., `<think>...</think>`) causes measurable CPU overhead compared to simple native string methods. Specifically, using the `.find()` method within a `while` loop combined with string slicing avoids the regex compilation and engine overhead entirely, while providing a fast-path skip via a simple `in` check. Benchmarks show a 3x speedup when tags aren't present and 2x when they are.
**Action:** Always favor native Python string operations (`in`, `.find()`, string slicing) over regular expressions when the search patterns are predictable sub-strings (e.g. static tag bounds) in performance-sensitive hot paths.

## 2026-04-01 - [String Concatenation Performance]
**Learning:** Native python string methods are extremely fast, but iterating and overwriting a local string variable with string slices via `+` operator scales O(n^2) and becomes a severe bottleneck in data processing loops for text blocks like `strip_think`.
**Action:** Always prefer appending slices to a `list` and `"".join()`ing them at the end rather than re-allocating a new string inside hot `while` or `for` loops.

## 2026-04-02 - O(N*M) Method Calls in Sliding Windows
**Learning:** In the `_find_match` utility inside `TARS/agent/tools/filesystem.py`, checking a sliding window for line-trimmed equality involved calling `[l.strip() for l in window]` on each iteration. For long files where the text wasn't an exact match, this caused O(N*M) redundant string `.strip()` allocations and method calls, causing severe performance issues.
**Action:** When performing sliding window checks involving text or list transformations, always pre-compute the transformations on the entire dataset outside the loop.
## 2025-04-02 - [Precompute String Operations in Sliding Window]
**Learning:** In the codebase, sliding window operations that perform repeated string manipulation inside the loop (like calling `[l.strip() for l in window]`) cause O(N*M) redundant string allocations and method calls overhead.
**Action:** Pre-compute array transformations outside the sliding window loop. For example, pre-computing `stripped_content = [l.strip() for l in content_lines]` and using list slicing for comparison instead of repeatedly stripping strings inside the loop.

## 2026-04-03 - [Fast-Path Token Estimation Type Checking]
**Learning:** In highly-frequented data pathways and loops validating dictionary values (e.g., token fast paths), using `type(content) is str` instead of `isinstance(content, str)` avoids Python's inheritance-checking overhead and is measurably faster. In combination with reversing conditional checks to fail fast, this optimizes hot loops.
**Action:** When refactoring for speed in hot loops that do not require inheritance checks, prefer exact type checks `type(obj) is T` and fail-fast early returns.

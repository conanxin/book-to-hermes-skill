# Safety Policy

## Prohibited Operations

The following operations are strictly forbidden in all scripts:

1. **No automatic package installation**
   - No `pip install` calls
   - No `apt install` calls
   - No `npm install` calls
   - No `--install-missing` or similar flags
   - Missing dependencies must produce clear errors

2. **No network requests**
   - No HTTP/HTTPS requests
   - No downloads
   - No API calls
   - No webhook triggers

3. **No arbitrary shell execution**
   - No `os.system()` with user input
   - No `subprocess` with unsanitized arguments
   - No `eval()` or `exec()` with user input

4. **No secret exposure**
   - Generated files scanned for API keys, tokens, passwords
   - No credential patterns in output
   - Source files with secrets should be rejected or sanitized

5. **No overwrite without consent**
   - Existing `books/<slug>/` directories trigger error
   - Use `--allow-overwrite yes` to explicitly allow overwrite
   - Backup suggested before force overwrite

## Input Validation

- File must exist and be readable
- Format must be in supported list
- Path must not be a directory or symlink to sensitive locations
- Maximum file size: 500MB (configurable)

## Output Safety

- All generated files are UTF-8 encoded
- No binary data in markdown files
- No executable code in generated content (unless source contains code examples)
- Secret scan runs on all generated files

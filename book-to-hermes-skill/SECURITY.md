# Security Policy

## What This Tool Does NOT Do

1. **No automatic dependency installation**
   - Scripts never run `pip install`, `apt install`, or `npm install`
   - Missing dependencies produce clear error messages
   - User must manually install into isolated venv

2. **No network requests**
   - No HTTP/HTTPS calls
   - No downloads
   - No API calls to external services

3. **No external LLM calls**
   - No OpenAI, Anthropic, Ollama, or LiteLLM usage
   - All processing is extractive (local text transformation only)

4. **No script execution**
   - HTML/EPUB extractors remove `script`, `style`, `noscript`, `svg`, `nav` elements
   - No JavaScript execution
   - No CSS processing beyond element removal

5. **No macro execution**
   - DOCX extractor is read-only
   - No macro execution
   - No embedded object processing

6. **No file upload**
   - Source files are read locally only
   - No cloud upload
   - No sharing with external services

7. **No secret exposure**
   - Generated files are scanned for API keys, tokens, passwords
   - Source files with sensitive content should be reviewed manually

8. **No configuration modification**
   - Does not modify `~/.hermes/config.yaml`
   - Does not restart Hermes gateway
   - Does not modify systemd services

9. **No full-disk scanning**
   - Only reads specified source file
   - Does not scan directories recursively

10. **No DRM handling**
    - DRM-protected EPUBs are not supported
    - No DRM removal tools

11. **No OCR**
    - Scanned PDFs are not supported
    - No image text extraction

## Privacy Considerations

**Output contains source document excerpts:**
- SKILL.md includes chapter titles and topic index
- chapters/ include extractive summaries and key points
- glossary.md includes terms found in source
- patterns.md includes techniques with source evidence

**Before converting sensitive documents:**
- Review source for PII, credentials, or confidential data
- Consider whether excerpts in output are acceptable
- Use `--allow-overwrite no` to prevent accidental overwrites

## Reporting Issues

If you find a security issue:
1. Do not open a public issue
2. Review the source code in `scripts/`
3. Verify no dangerous operations exist
4. Report to project maintainer privately

## Validation

Run `scripts/validate_book_skill.py` after conversion to check:
- No secrets in generated files
- No suspicious patterns
- File sizes within bounds
- Metadata is valid JSON

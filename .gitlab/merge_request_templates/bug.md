---
name: Bug Fix
about: Pull request template for bug fixes
title: '[FIX] '
labels: bug, fix
---

## Bug Fix Summary
Brief description of the bug that was fixed.

## Related Issue
Closes #[issue_number]

## Root Cause Analysis
Explain what caused the bug:
- [ ] Logic error
- [ ] Missing validation
- [ ] Race condition
- [ ] Integration issue
- [ ] Configuration problem
- [ ] Dependency issue
- [ ] Other: ___________

## Changes Made
Detailed description of the changes made to fix the bug:

### Files Modified
- `file1.py`: Brief description of changes
- `file2.py`: Brief description of changes

### Key Changes
- [ ] Fixed logic error in function X
- [ ] Added input validation
- [ ] Updated error handling
- [ ] Fixed race condition
- [ ] Updated configuration
- [ ] Other: ___________

## Testing
How was this fix tested?

### Test Cases
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] Regression testing performed

### Test Results
```
[Paste test results here]
```

### Edge Cases Considered
- [ ] Invalid inputs
- [ ] Network failures
- [ ] Large files
- [ ] Empty data
- [ ] Concurrent access
- [ ] Other: ___________

## Verification Steps
Steps to verify the fix:
1. Step 1
2. Step 2
3. Step 3

## Performance Impact
- [ ] No performance impact
- [ ] Minor performance improvement
- [ ] Minor performance regression (justified)
- [ ] Significant performance change (explained below)

Performance details: ___________

## Breaking Changes
- [ ] No breaking changes
- [ ] Minor breaking changes (migration notes below)
- [ ] Major breaking changes (requires version bump)

Migration notes: ___________

## Screenshots/Logs
Before and after screenshots or relevant logs:

### Before
```
[Error logs or screenshots before fix]
```

### After
```
[Success logs or screenshots after fix]
```

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented, particularly complex areas
- [ ] Tests added that prove fix is effective
- [ ] Tests pass locally
- [ ] No new linting errors introduced
- [ ] Documentation updated if needed
- [ ] Change log updated

## Additional Notes
Any additional information that reviewers should know.

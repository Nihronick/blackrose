# Session Snapshot - 2026-04-28

## Objective

Fix critical UI crash in Admin Panel when editing guides.

## Hypothesis

The crash was caused by `null` values returned from the API for fields expected to be arrays (`photo`, `video`, `document`, `tags`) or strings (`text`), leading to `.map()` or `.replace()` calls on non-object types.

## Changes Applied

### Frontend

- **AdminRichEditor.tsx**:
  - Updated `renderMd` to handle `null`, `undefined`, and non-string inputs.
  - Added safe defaults (`value || ''`) in `useEffect` and `useMemo` (word count).
- **AdminGuideEditor.tsx**:
  - Modified `form` and `tags` state initialization to use `Array.isArray` checks, ensuring they are always initialized as empty arrays if data is missing or `null`.
  - Refactored `UrlListEditor` to be ultra-defensive with `safeValue` helper.

### Backend

- Verified `models.py` (GuideIn) and `db_models.py` (Guide). Fields are correctly defined as `ARRAY(Text)` with empty list defaults, but frontend-side defense was needed for extra safety and compatibility with legacy data.

## Status

- **Bug Fixed**: UI should no longer crash when entering the Guide Editor.
- **Verification**: Code review confirms all risky property accesses are now protected.

## Next Steps

- Verify the fix with the user.
- Monitor for any other "null pointer" style crashes in other admin tabs.

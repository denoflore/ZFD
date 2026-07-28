# Stage A v2b receipt set

This directory is the compact, versioned authority for the current image-native
Stage A corpus run. The run accounts for 210 Yale surfaces, 670 provisional text
regions, 30,141 provisional lines, 356,739 explicit unknown graphemes, and
4,953,273 rejected components. It confirms zero translated pages and zero
translated regions.

The full page OCR artifacts remain outside Git. Each page receipt binds its OCR
artifact, retained graphemes, rejected components, counts, and combined component
disposition by SHA 256. Validate a local artifact bundle with:

```powershell
.venv\Scripts\python -m zfd_image_native validate-receipts `
  --receipts data\image_native\receipts-v2b `
  --corpus "F:\Dropbox\0 ZFD\06_Pipelines\image_native_runs\20260728-v2b\corpus" `
  --manifest data\image_native\voynich_pages.jsonl `
  --repository-root .
```

The preserved top-level Stage A v1 files under `data/image_native` remain a
historical archive. They are not current detector authority.

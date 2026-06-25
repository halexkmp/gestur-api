# Tasks: Register Journey with Selfie Proof

## Phase 1: Implementation

- [x] T1.1: Setup dependencies (`vercel-blob`, `Pillow`) and environment variables (`BLOB_STORE_ID`, `BLOB_READ_WRITE_TOKEN`) (Plan: 1, Req: 1)
- [x] T1.2: Add `selfie_id` to `JourneyRegistry` model and run migration (Plan: 2, Req: 1)
- [x] T1.3: Implement image optimization logic in `VercelBlobService` (Plan: 3, Req: 2)
- [x] T1.4: Implement Vercel Blob upload in `register_journey` infra using `AsyncBlobClient` (Plan: 3, Req: 1)
- [x] T1.5: Update `register_journey` UI to handle file upload (Plan: 5, Req: 1)
- [x] T1.6: Update `admin_list_journeys` response schema to include selfie ID (Plan: 5, Req: 3)
- [x] T1.7: Implement `get_selfie` slice (Plan: 6, Req: 3)
    - [x] T1.7.1: UI: `ui/route.py` to serve image (Plan: 6, Req: 3)
    - [x] T1.7.2: Application: `application/use_case.py` (Plan: 6, Req: 3)
    - [x] T1.7.3: Infra: `infra/blob_service.py` download method (Plan: 6, Req: 3)

## Phase 2: Verification

- [x] T2.1: Verify image optimization and upload (Plan: 6, Req: 2)
- [x] T2.2: Verify admin list returns selfie reference (Plan: 6, Req: 3)
- [x] T2.3: Verify selfie retrieval (Plan: 6, Req: 3)

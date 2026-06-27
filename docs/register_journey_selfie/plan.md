# Implementation Plan: Register Journey with Selfie Proof

This plan describes the steps to implement the selfie proof improvement for the journey registration feature.

## 1. Environment and Dependencies
- Install `vercel-blob` for cloud storage.
- Install `Pillow` for image optimization.
- Configure `BLOB_STORE_ID` and `BLOB_READ_WRITE_TOKEN` environment variables.

## 2. Database Layer
- Update `JourneyRegistry` model in `app/shared/db/models.py` to include `selfie_id`.
- Generate and run migrations.

## 3. Infra Layer
- Implement `VercelBlobService` in `app/shared/infra/blob_service.py`.
- Implement image optimization (resize to 800px, JPEG 70%) in `VercelBlobService`.
- Use `AsyncBlobClient` from `vercel.blob` for all operations (put, get, delete).
- Use `client.put` for uploading optimized images.
- Use `client.get` for downloading images via URL.
- Use `client.delete` for cleanup if necessary.
- Ensure `BLOB_READ_WRITE_TOKEN` is available in the environment or set in the service for the SDK to function correctly.
- Update repository to save `selfie_id`.

## 4. Application Layer
- Use `VercelBlobService` to optimize and upload the selfie.
- Coordinate the upload and saving of the selfie.

## 5. UI Layer
- Update `app/slices/journey/register_journey/ui/schemas.py` to handle the new field.
- Update `app/slices/journey/register_journey/ui/route.py` to accept `UploadFile` (multipart/form-data).
- Update `app/slices/journey/admin_list_journeys/ui/schemas.py` to include `selfie_id` in the response.

## 6. Selfie Retrieval
- Create a new slice `slices/journey/get_selfie`.
- Implement UI route to handle image serving by `selfie_id`.
- Implement Application use case to fetch image from Vercel Blob.
- Implement Infra logic to download from Vercel Blob.

## 7. Verification
- Verify in-memory processing.
- Verify image compression and resizing.
- Verify upload to Vercel Blob.

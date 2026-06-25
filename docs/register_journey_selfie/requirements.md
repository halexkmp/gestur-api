# Requirements: Register Journey with Selfie Proof

## Introduction
As an improvement to the journey registration process, employees must provide a "selfie" to prove their identity at the moment of registration. This ensures higher security and verification of field presence.

## Requirements

### 1. Vercel Blob Integration
- The system SHALL use the official Vercel Blob Python SDK (`vercel-blob`).
- It SHOULD use the asynchronous client `AsyncBlobClient` from `vercel.blob`.
- Environment variables `BLOB_STORE_ID` and `BLOB_READ_WRITE_TOKEN` MUST be configured.
- Images SHALL be uploaded using the `put` method with "public" access.
- The `selfie_id` stored in the database SHALL be the full URL returned by Vercel Blob.

### 2. Selfie Capture & Upload
- **User Story**: As an employee, I want to provide a selfie when registering my journey so that my identity is verified.
- **Acceptance Criteria**:
  - WHEN registering a journey THEN the system SHALL require a selfie image.
  - WHEN the selfie is provided THEN the system SHALL optimize the image and store it in cloud storage.
  - The registration endpoint MUST accept an image file (selfie).
  - The image MUST be uploaded to Vercel Blob using the official `vercel-blob` Python SDK.
  - The database record for the journey MUST store the reference returned by Vercel Blob.
  - The system MUST use `BLOB_STORE_ID` and `BLOB_READ_WRITE_TOKEN` environment variables for Vercel Blob authentication.

### 2. Storage & Network Optimization
- **User Story**: As a system owner, I want to minimize storage and network usage for selfie images.
- **Acceptance Criteria**:
  - Images MUST be resized to a maximum width of 800px (preserving aspect ratio) before upload.
  - Images MUST be converted to JPEG format with a quality setting of 70% to minimize file size.
  - Processing MUST happen in-memory to avoid temporary file storage issues.

### 3. Administrative Access
- **User Story**: As an admin, I want to see the selfie of a journey record so I can verify the identity.
- **Acceptance Criteria**:
  - WHEN an admin lists journeys THEN the system SHALL provide the selfie reference for each record.
  - WHEN requested by a selfie ID THEN the system SHALL return the optimized image.

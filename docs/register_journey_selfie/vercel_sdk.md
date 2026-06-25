Other frameworks

Choose a framework to optimize documentation to:

*   ![](/vc-ap-vercel-docs/_next/static/immutable/media/logo-next-light.2d2j04-25g3vf.svg)![](/vc-ap-vercel-docs/_next/static/immutable/media/logo-next-dark.0jqrwuxq05oly.svg)
    
    Next.js (/app)
*   ![](/vc-ap-vercel-docs/_next/static/immutable/media/logo-next-light.2d2j04-25g3vf.svg)![](/vc-ap-vercel-docs/_next/static/immutable/media/logo-next-dark.0jqrwuxq05oly.svg)
    
    Next.js (/pages)
*   Other frameworks

On this page

# @vercel/blob

Vercel Blob is available on [all plans](/docs/plans)

Those with the [owner, member, developer](</docs/rbac/access-roles#owner, member, developer-role>) role can access this feature

## [Getting started](#getting-started)[](#getting-started)

To start using [Vercel Blob](/storage/blob) SDK, follow the steps below:

You can also interact with Vercel Blob using the [Vercel CLI](/docs/cli/blob) for command-line operations. For example, you might want to quickly upload assets during local development without writing additional code.

Vercel Blob works with any frontend framework. begin by installing the package:

TypeScriptPython

```
pip install vercel
```

1.  ### [Create a Blob store](#create-a-blob-store)[](#create-a-blob-store)
    
    1.  Go to your project's [Storage tab](https://vercel.com/d?to=%2F%5Bteam%5D%2F%5Bproject%5D%2Fstores&title=Go+to+Storage)
    2.  Select Create Database, then choose Blob
    3.  Select Continue, then set the access to Private or Public
    4.  Choose a name for your store and select Create a new Blob store
    5.  Select the environments where you would like the read-write token to be included. You can also update the prefix of the Environment Variable in Advanced Options
    
    Once created, you are taken to the Vercel Blob store page.
    
2.  ### [Prepare your local project](#prepare-your-local-project)[](#prepare-your-local-project)
    
    When you create the Blob store, Vercel adds one environment variable to the projects you selected:
    
    *   `BLOB_READ_WRITE_TOKEN`: a long-lived static read-write token. Use it for code that runs outside Vercel or to generate client tokens for browser uploads.
    
    To use this environment variable locally, use the Vercel CLI to [pull the values into your local project](/docs/cli/env#exporting-development-environment-variables):
    
    ```
    vercel env pull
    ```
    
3.  ### [Connect to a project (highly recommended)](#connect-to-a-project-highly-recommended)[](#connect-to-a-project-highly-recommended)
    
    OpenID Connect (OIDC) is the default authentication on Vercel and is more secure than the long-lived `BLOB_READ_WRITE_TOKEN`. OIDC tokens rotate automatically, which removes the risk that a static secret leaks from your codebase or environment. Learn more about [how OIDC token federation works](/docs/oidc#how-oidc-token-federation-works).
    
    When you connect your Blob store to a project, Vercel adds three environment variables to that project:
    
    *   `BLOB_STORE_ID`: the id of your Blob store. The SDK pairs this with `VERCEL_OIDC_TOKEN` to authenticate requests.
    *   `VERCEL_OIDC_TOKEN`: a short-lived OIDC token that Vercel populates and rotates on every deployment.
    *   `BLOB_WEBHOOK_PUBLIC_KEY`: the public key the SDK uses to verify webhook callbacks signed by Vercel Blob when uploads are done via presigned URLs (or via `handleUploadPresigned`).
    
    To connect a project:
    
    1.  Go to your Blob store's Projects tab
    2.  Select Connect to Project
    3.  Choose the project and environments to connect
    
    See [Authentication](/docs/vercel-blob/using-blob-sdk#authentication) for the full credential resolution order.
    

## [Authentication](#authentication)[](#authentication)

Use OIDC when your code runs on Vercel. Use a static read-write token when your code runs outside Vercel or when you generate client tokens for browser uploads.

### [OIDC tokens (recommended)](#oidc-tokens-recommended)[](#oidc-tokens-recommended)

When your application runs on Vercel, the platform populates the `VERCEL_OIDC_TOKEN` environment variable with a short-lived OpenID Connect token. The SDK reads this variable automatically and pairs it with your store id to authenticate requests. Because the token is short-lived and rotates automatically, it removes the risk that a long-lived secret leaks from your codebase or environment.

To use OIDC, the following environment variables must be present:

*   `VERCEL_OIDC_TOKEN`: populated automatically on Vercel deployments. For local development, run `vercel env pull` to fetch a short-lived token.
*   `BLOB_STORE_ID`: the id of the store you want to read or write. Vercel creates this variable when you connect a store to your project. The SDK accepts the value in either `store_<id>` or `<id>` form.

When both are present, the SDK uses OIDC by default.

#### [Passing OIDC credentials explicitly](#passing-oidc-credentials-explicitly)[](#passing-oidc-credentials-explicitly)

Some frameworks do not populate `process.env` from `.env.local` automatically. Vite, for example, only exposes variables prefixed with `VITE_` to client code, and server code requires a plugin like `dotenv-expand` or a custom config to load `.env.local` into `process.env`. In those environments, the SDK cannot read `VERCEL_OIDC_TOKEN` from the environment, so OIDC auto-configuration silently falls back to `BLOB_READ_WRITE_TOKEN` (or throws if no read-write token is available either).

You have two options:

*   Configure your framework to load `.env.local` into `process.env` (for example, with `dotenv-expand`).
    
*   Pass the OIDC credentials directly on each call using the `oidcToken` and `storeId` options:
    
    ```
    import { put } from '@vercel/blob';
     
    await put('media/photo.png', file, {
      access: 'private',
      oidcToken: loadOidcToken(), // your own loader
      storeId: loadStoreId(),
    });
    ```
    

The `oidcToken` option mirrors `token` for read-write credentials, so OIDC credentials no longer have to come from the environment.

`handleUpload` always requires a read-write token to sign client tokens for browser uploads. OIDC is not accepted for this method. See [Read-write tokens](#read-write-tokens).

### [Read-write tokens](#read-write-tokens)[](#read-write-tokens)

A read-write token is a long-lived static credential. Use one when your code runs outside Vercel, for example in a CI job or on another host.

When you create a Blob store from the Vercel dashboard, an environment variable named `BLOB_READ_WRITE_TOKEN` is added to the projects you select. OIDC takes precedence when its environment variables are present; otherwise the SDK falls back to `BLOB_READ_WRITE_TOKEN`.

### [Resolution order](#resolution-order)[](#resolution-order)

The SDK resolves credentials in this order, stopping at the first match:

1.  An explicit `token` option (a read-write token, or a client token created with `generateClientTokenFromReadWriteToken`). This always wins, including over OIDC.
    
2.  OIDC credentials, paired with a store id:
    
    *   The OIDC token comes from the `oidcToken` option if set, otherwise from `process.env.VERCEL_OIDC_TOKEN`.
    *   The store id comes from the `storeId` option if set, otherwise from `process.env.BLOB_STORE_ID`.
    
    Both an OIDC token and a store id must be available for this tier to match. The SDK accepts the store id in either `store_<id>` or `<id>` form.
    
3.  `process.env.BLOB_READ_WRITE_TOKEN`.
    
4.  If none of the above is available, the SDK throws an error.
    

## [The `access` parameter](#the-access-parameter)[](#the-access-parameter)

While the store itself determines whether files are [private or public](/docs/vercel-blob#private-and-public-storage), most SDK methods require you to pass `access: 'private'` or `access: 'public'`. This makes it explicit in your code what kind of data access you're dealing with, so anyone reading the code immediately understands the security context.

## [Using the SDK methods](#using-the-sdk-methods)[](#using-the-sdk-methods)

In the examples below, we use [Fluid compute](/docs/fluid-compute) for optimal performance and scalability.

## [Upload a blob](#upload-a-blob)[](#upload-a-blob)

This example creates a Function that accepts a file from a `multipart/form-data` form and uploads it to the Blob store. The function returns a unique URL for the blob.

TypeScriptPython

```
import asyncio
import os
import tempfile
from dotenv import load_dotenv
from vercel.blob import UploadProgressEvent, BlobClient, AsyncBlobClient
 
load_dotenv(".env.local")
load_dotenv()
 
def on_progress(e: UploadProgressEvent) -> None:
    print(f"progress: {e.loaded}/{e.total} bytes ({e.percentage}%)")
 
async def handler(form: dict) -> dict:
    client = AsyncBlobClient()
 
    file: bytes = form["file"]  # your uploaded bytes
    uploaded = await client.put(
        f"profiles/{form['filename']}",
        file,
        access="private",  # or "public",
        add_random_suffix=True,
        on_upload_progress=on_progress,
    )
    return dict(uploaded)
```

### [`put()`](#put)[](#put)

The `put` method uploads a blob object to the Blob store.

TypeScriptPython

```
put(
    pathname: str,
    body: bytes | AsyncIterator[bytes],
    *,
    access: Literal['private', 'public'],
    content_type: str | None = None,
    add_random_suffix: bool = False,
    overwrite: bool = False,
    cache_control_max_age: int | None = None,
    token: str | None = None,
    multipart: bool | None = None,
    on_upload_progress: Callable[[UploadProgressEvent], None] | None = None
)
```

It accepts the following parameters:

*   `pathname`: (Required) A string specifying the base value of the return URL
*   `body`: (Required) A blob object as `ReadableStream`, `String`, `ArrayBuffer` or `Blob` based on these [supported body types](https://developer.mozilla.org/docs/Web/API/fetch#body)
*   `options`: (Required) A `JSON` object with the following required and optional parameters:

| Parameter            | Required | Values                                                                                                                                                                                                                                                                                                                           |
| -------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `access`             | Yes      | [`'private'` or `'public'`](/docs/vercel-blob#private-and-public-storage). Determines the access level of the blob.                                                                                                                                                                                                              |
| `addRandomSuffix`    | No       | A boolean specifying whether to add a random suffix to the `pathname`. It defaults to `false`. We recommend using this option to ensure there are no conflicts in your blob filenames.                                                                                                                                           |
| `allowOverwrite`     | No       | A boolean to allow overwriting blobs. By default an error will be thrown if you try to overwrite a blob by using the same `pathname` for multiple blobs.                                                                                                                                                                         |
| `cacheControlMaxAge` | No       | A number in seconds to configure how long Blobs are cached. Defaults to one month. Cannot be set to a value lower than 1 minute. See the [caching](/docs/storage/vercel-blob#caching) documentation for more details.                                                                                                            |
| `contentType`        | No       | A string indicating the [media type](https://developer.mozilla.org/docs/Web/HTTP/Headers/Content-Type). By default, it's extracted from the pathname's extension.                                                                                                                                                                |
| `token`              | No       | A static read-write token. Defaults to `process.env.BLOB_READ_WRITE_TOKEN`. Its default value is not used when OIDC credentials are present, but an explicitly passed token always takes priority. You can also pass a client token created with `generateClientTokenFromReadWriteToken`. See [Authentication](#authentication). |
| `oidcToken`          | No       | A Vercel OIDC token, used in place of `process.env.VERCEL_OIDC_TOKEN`. Pair with `storeId` (or `BLOB_STORE_ID`). Useful when your framework does not load `.env.local` into `process.env` automatically. See [Authentication](#authentication).                                                                                  |
| `storeId`            | No       | The Blob store id, used with OIDC. Defaults to `process.env.BLOB_STORE_ID`. The SDK accepts either `store_<id>` or `<id>` form. See [Authentication](#authentication).                                                                                                                                                           |
| `multipart`          | No       | Pass `multipart: true` when uploading large files. It will split the file into multiple parts, upload them in parallel and retry failed parts.                                                                                                                                                                                   |
| `abortSignal`        | No       | An [AbortSignal](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal) to cancel the operation                                                                                                                                                                                                                           |
| `onUploadProgress`   | No       | Callback to track upload progress: `onUploadProgress({loaded: number, total: number, percentage: number})`                                                                                                                                                                                                                       |
| `ifMatch`            | No       | An ETag value. The operation only succeeds if the blob's current ETag matches this value. Use this for [conditional writes](/docs/vercel-blob#conditional-writes) to prevent overwriting changes made by others. Throws `BlobPreconditionFailedError` if the ETag doesn't match.                                                 |

#### [Example code with folder output](#example-code-with-folder-output)[](#example-code-with-folder-output)

To upload your file to an existing [folder](#folders) inside your blob storage, pass the folder name in the `pathname` as shown below:

TypeScriptPython

```
import os
from dotenv import load_dotenv
from vercel.blob import AsyncBlobClient
 
load_dotenv('.env.local')
load_dotenv()
 
client = AsyncBlobClient()
 
image_bytes = b"..."
blob = await client.put(
    f"existingBlobFolder/image.png",
    image_bytes,
    access="private",  # or "public",
    add_random_suffix=True,
)
```

#### [Example responses](#example-responses)[](#example-responses)

`put()` returns a `JSON` object with the following data for the created blob object:

```
{
  "pathname": "string",
  "contentType": "string",
  "contentDisposition": "string",
  "url": "string",
  "downloadUrl": "string",
  "etag": "string"
}
```

An example blob (uploaded with `addRandomSuffix: true`) is:

```
{
  "pathname": "profilesv1/user-12345-NoOVGDVcqSPc7VYCUAGnTzLTG2qEM2.txt",
  "contentType": "text/plain",
  "contentDisposition": "attachment; filename=\"user-12345-NoOVGDVcqSPc7VYCUAGnTzLTG2qEM2.txt\"",
  "url": "https://ce0rcu23vrrdzqap.private.blob.vercel-storage.com/profilesv1/user-12345-NoOVGDVcqSPc7VYCUAGnTzLTG2qEM2.txt",
  "downloadUrl": "https://ce0rcu23vrrdzqap.private.blob.vercel-storage.com/profilesv1/user-12345-NoOVGDVcqSPc7VYCUAGnTzLTG2qEM2.txt?download=1",
  "etag": "\"a1b2c3d4e5f6\""
}
```

If `access` is `'public'`, the URL domain will be `.public.blob.vercel-storage.com` instead of `.private.blob.vercel-storage.com`.

An example blob uploaded without `addRandomSuffix: true` (default) is:

```
{
  "pathname": "profilesv1/user-12345.txt",
  "contentType": "text/plain",
  "contentDisposition": "attachment; filename=\"user-12345.txt\"",
  // no automatic random suffix added 👇
  "url": "https://ce0rcu23vrrdzqap.private.blob.vercel-storage.com/profilesv1/user-12345.txt",
  "downloadUrl": "https://ce0rcu23vrrdzqap.private.blob.vercel-storage.com/profilesv1/user-12345.txt?download=1",
  "etag": "\"f6e5d4c3b2a1\""
}
```

## [Get a blob](#get-a-blob)[](#get-a-blob)

Retrieve blob content as a stream. For private blobs, this is how you deliver files through your functions. For public blobs, you can use this to process blob content server-side.

### [`get()`](#get)[](#get)

TypeScriptPython

```
get(
    url_or_path: str,
    *,
    access: Literal['private', 'public'],
    token: str | None = None,
    if_none_match: str | None = None,
) -> GetBlobResult | None
```

It accepts the following parameters:

*   `urlOrPathname`: (Required) A string specifying the URL or pathname of the blob object to retrieve
*   `options`: (Required) A `JSON` object with the following required and optional parameters:

| Parameter     | Required | Values                                                                                                                                                                                                                                                                            |
| ------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `access`      | Yes      | [`'private'` or `'public'`](/docs/vercel-blob#private-and-public-storage). Determines the access level of the blob.                                                                                                                                                               |
| `token`       | No       | A static read-write token. Defaults to `process.env.BLOB_READ_WRITE_TOKEN`. Its default value is not used when OIDC credentials are present, but an explicitly passed token always takes priority. See [Authentication](#authentication).                                         |
| `oidcToken`   | No       | A Vercel OIDC token, used in place of `process.env.VERCEL_OIDC_TOKEN`. Pair with `storeId` (or `BLOB_STORE_ID`). Useful when your framework does not load `.env.local` into `process.env` automatically. See [Authentication](#authentication).                                   |
| `storeId`     | No       | The Blob store id, used with OIDC. Defaults to `process.env.BLOB_STORE_ID`. The SDK accepts either `store_<id>` or `<id>` form. See [Authentication](#authentication).                                                                                                            |
| `ifNoneMatch` | No       | An ETag value. When the blob's current ETag matches, returns `statusCode: 304` with `stream: null` instead of the full response. See [browser caching with conditional requests](/docs/vercel-blob/private-storage#browser-caching-with-conditional-requests) for a full example. |
| `headers`     | No       | Additional headers to include in the fetch request. The authorization header is set automatically.                                                                                                                                                                                |
| `abortSignal` | No       | An [AbortSignal](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal) to cancel the operation                                                                                                                                                                            |

`get()` returns `null` (`None` in Python) if the blob is not found, or an object with the following properties:

TypeScriptPython

```
# GetBlobResult:
result.status_code          # int (200 or 304)
result.stream               # AsyncIterator[bytes] | None (None on 304)
result.headers              # dict
result.blob.url             # str
result.blob.download_url    # str
result.blob.pathname        # str
result.blob.content_type    # str | None (None on 304)
result.blob.content_disposition  # str
result.blob.cache_control   # str
result.blob.etag            # str
result.blob.size            # int | None (None on 304)
result.blob.uploaded_at     # datetime
```

#### [Example](#example)[](#example)

TypeScriptPython

```
from vercel.blob import AsyncBlobClient
 
client = AsyncBlobClient()
 
result = await client.get("documents/report.pdf", access="private")
 
if result is None or result.status_code != 200:
    print("Not found")
else:
    # result.stream is an async iterator of bytes
    async for chunk in result.stream:
        # process each chunk
        pass
```

#### [Example response](#example-response)[](#example-response)

`get()` returns `null` (`None` in Python) if the blob is not found, or an object with the following properties:

TypeScriptPython

```
{
  statusCode: number; // 200 or 304
  stream: ReadableStream<Uint8Array> | null; // null on 304
  headers: Headers;
  blob: {
    url: string;
    downloadUrl: string;
    pathname: string;
    contentType: string | null; // null on 304
    contentDisposition: string;
    cacheControl: string;
    etag: string;
    size: number | null; // null on 304
    uploadedAt: Date;
  };
}
```

```
# GetBlobResult:
result.status_code          # int (200 or 304)
result.stream               # AsyncIterator[bytes] | None (None on 304)
result.headers              # dict
result.blob.url             # str
result.blob.download_url    # str
result.blob.pathname        # str
result.blob.content_type    # str | None (None on 304)
result.blob.content_disposition  # str
result.blob.cache_control   # str
result.blob.etag            # str
result.blob.size            # int | None (None on 304)
result.blob.uploaded_at     # datetime
```

## [Deleting blobs](#deleting-blobs)[](#deleting-blobs)

This example creates a function that deletes a blob object from the Blob store. You can delete multiple blob objects in a single request by passing an array of blob URLs.

### [`del()`](#del)[](#del)

The `del` method deletes one or multiple blob objects from the Blob store.

Since blobs are cached, it may take up to one minute for them to be fully removed from the Vercel CDN cache.

TypeScriptPython

```
delete(url_or_path: str | Iterable[str], *, token: str | None = None) -> None
```

It accepts the following parameters:

*   `urlOrPathname`: (Required) A string or array of strings specifying the URL(s) or pathname(s) of the blob object(s) to delete.
*   `options`: (Optional) A `JSON` object with the following optional parameter:

| Parameter     | Required | Values                                                                                                                                                                                                                                                                                                                    |
| ------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `token`       | No       | A static read-write token. Defaults to `process.env.BLOB_READ_WRITE_TOKEN`. Its default value is not used when OIDC credentials are present, but an explicitly passed token always takes priority. See [Authentication](#authentication).                                                                                 |
| `oidcToken`   | No       | A Vercel OIDC token, used in place of `process.env.VERCEL_OIDC_TOKEN`. Pair with `storeId` (or `BLOB_STORE_ID`). Useful when your framework does not load `.env.local` into `process.env` automatically. See [Authentication](#authentication).                                                                           |
| `storeId`     | No       | The Blob store id, used with OIDC. Defaults to `process.env.BLOB_STORE_ID`. The SDK accepts either `store_<id>` or `<id>` form. See [Authentication](#authentication).                                                                                                                                                    |
| `ifMatch`     | No       | An ETag value. The delete only succeeds if the blob's current ETag matches this value. Use this for [conditional writes](/docs/vercel-blob#conditional-writes) to ensure you're deleting the expected version. Throws `BlobPreconditionFailedError` if the ETag doesn't match. Only works with a single URL (not arrays). |
| `abortSignal` | No       | An [AbortSignal](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal) to cancel the operation                                                                                                                                                                                                                    |

`del()` returns a `void` response. A delete action is always successful if the blob url exists. A delete action won't throw if the blob url doesn't exist.

## [Get blob metadata](#get-blob-metadata)[](#get-blob-metadata)

This example creates a Function that returns a blob object's metadata.

### [`head()`](#head)[](#head)

The `head` method returns a blob object's metadata.

TypeScriptPython

```
head(url_or_path: str, *, token: str | None = None) -> HeadBlobResult
```

It accepts the following parameters:

*   `urlOrPathname`: (Required) A string specifying the URL or pathname of the blob object to read.
*   `options`: (Optional) A `JSON` object with the following optional parameter:

| Parameter     | Required | Values                                                                                                                                                                                                                                          |
| ------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `token`       | No       | A static read-write token. Defaults to `process.env.BLOB_READ_WRITE_TOKEN`. Its default value is not used when OIDC credentials are present, but an explicitly passed token always takes priority. See [Authentication](#authentication).       |
| `oidcToken`   | No       | A Vercel OIDC token, used in place of `process.env.VERCEL_OIDC_TOKEN`. Pair with `storeId` (or `BLOB_STORE_ID`). Useful when your framework does not load `.env.local` into `process.env` automatically. See [Authentication](#authentication). |
| `storeId`     | No       | The Blob store id, used with OIDC. Defaults to `process.env.BLOB_STORE_ID`. The SDK accepts either `store_<id>` or `<id>` form. See [Authentication](#authentication).                                                                          |
| `abortSignal` | No       | An [AbortSignal](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal) to cancel the operation                                                                                                                                          |

`head()` returns one of the following:

*   a `JSON` object with the requested blob object's metadata
*   throws a `BlobNotFoundError` if the blob object was not found

TypeScriptPython

```
result.size                 # int
result.uploaded_at          # datetime
result.pathname             # str
result.content_type         # str
result.content_disposition  # str
result.url                  # str
result.download_url         # str
result.cache_control        # str
result.etag                 # str
```

## [List blobs](#list-blobs)[](#list-blobs)

This example creates a Function that returns a list of blob objects in a Blob store.

### [`list()`](#list)[](#list)

The `list` method returns a list of blob objects in a Blob store.

TypeScriptPython

```
list_objects(
    *,
    limit: int | None = None,
    prefix: str | None = None,
    cursor: str | None = None,
    mode: str | None = None,
    token: str | None = None,
) -> ListBlobResult
```

It accepts the following parameters:

*   `options`: (Optional) A `JSON` object with the following optional parameters:

| Parameter     | Required | Values                                                                                                                                                                                                                                          |
| ------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `token`       | No       | A static read-write token. Defaults to `process.env.BLOB_READ_WRITE_TOKEN`. Its default value is not used when OIDC credentials are present, but an explicitly passed token always takes priority. See [Authentication](#authentication).       |
| `oidcToken`   | No       | A Vercel OIDC token, used in place of `process.env.VERCEL_OIDC_TOKEN`. Pair with `storeId` (or `BLOB_STORE_ID`). Useful when your framework does not load `.env.local` into `process.env` automatically. See [Authentication](#authentication). |
| `storeId`     | No       | The Blob store id, used with OIDC. Defaults to `process.env.BLOB_STORE_ID`. The SDK accepts either `store_<id>` or `<id>` form. See [Authentication](#authentication).                                                                          |
| `limit`       | No       | A number specifying the maximum number of blob objects to return. It defaults to 1000                                                                                                                                                           |
| `prefix`      | No       | A string used to filter for blob objects contained in a specific folder assuming that the folder name was used in the `pathname` when the blob object was uploaded                                                                              |
| `cursor`      | No       | A string obtained from a previous `list` response to be used for reading the next page of results                                                                                                                                               |
| `mode`        | No       | A string specifying the response format. Can either be `expanded` (default) or `folded`. In `folded` mode all blobs that are located inside a folder will be folded into a single folder string entry                                           |
| `abortSignal` | No       | An [AbortSignal](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal) to cancel the operation                                                                                                                                          |

`list()` returns a `JSON` object in the following format:

TypeScriptPython

```
# ListBlobResult:
result.blobs          # list[ListBlobItem]
result.cursor         # str | None
result.has_more       # bool
result.folders        # list[str] | None
 
# ListBlobItem:
item.size # int
item.uploaded_at # datetime
item.pathname # str
item.url # str
item.download_url # str
item.etag # str
```

### [Pagination](#pagination)[](#pagination)

For a long list of blob objects (the default list `limit` is 1000), you can use the `cursor` and `hasMore` parameters to paginate through the results as shown in the example below:

TypeScriptPython

```
from vercel.blob import list_objects
 
has_more = True
cursor = None
 
while has_more:
    page = list_objects(cursor=cursor, limit=1000)
    for b in page.blobs:
        # process each blob
        pass
    has_more = page.has_more
    cursor = page.cursor
```

### [Folders](#folders)[](#folders)

To retrieve the folders from your blob store, alter the `mode` parameter to modify the response format of the list operation. The default value of `mode` is `expanded`, which returns all blobs in a single array of objects.

Alternatively, you can set `mode` to `folded` to roll up all blobs located inside a folder into a single entry. These entries will be included in the response as `folders`. Blobs that are not located in a folder will still be returned in the blobs property.

By using the `folded` mode, you can efficiently retrieve folders and subsequently list the blobs inside them by using the returned `folders` as a `prefix` for further requests. Omitting the `prefix` parameter entirely, will return all folders in the root of your store. Be aware that the blobs pathnames and the folder names will always be fully quantified and never relative to the prefix you passed.

TypeScriptPython

```
from vercel.blob import list_objects
 
root = list_objects(mode="folded")
first_folder = root.folders[0]
sub = list_objects(mode="folded", prefix=first_folder)
```

## [Copy a blob](#copy-a-blob)[](#copy-a-blob)

This example creates a Function that copies an existing blob to a new path in the store.

### [`copy()`](#copy)[](#copy)

The `copy` method copies an existing blob object to a new path inside the blob store.

The `contentType` and `cacheControlMaxAge` will not be copied from the source blob. If the values should be carried over to the copy, they need to be defined again in the options object.

Contrary to `put()`, `addRandomSuffix` is false by default. This means no automatic random id suffix is added to your blob url, unless you pass `addRandomSuffix: true`.

TypeScriptPython

```
copy(
    src_path: str,
    dst_path: str,
    *,
    access: Literal['private', 'public'],
    content_type: str | None = None,
    add_random_suffix: bool = False,
    overwrite: bool = False,
    cache_control_max_age: int | None = None,
    token: str | None = None,
) -> PutBlobResult
```

It accepts the following parameters:

*   `fromUrlOrPathname`: (Required) A blob URL or pathname identifying an already existing blob
*   `toPathname`: (Required) A string specifying the new path inside the blob store. This will be the base value of the return URL
*   `options`: (Required) A `JSON` object with the following required and optional parameters:

| Parameter            | Required | Values                                                                                                                                                                                                                                                                                                       |
| -------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `access`             | Yes      | [`'private'` or `'public'`](/docs/vercel-blob#private-and-public-storage). Determines the access level of the blob.                                                                                                                                                                                          |
| `contentType`        | No       | A string indicating the [media type](https://developer.mozilla.org/docs/Web/HTTP/Headers/Content-Type). By default, it's extracted from the toPathname's extension.                                                                                                                                          |
| `token`              | No       | A static read-write token. Defaults to `process.env.BLOB_READ_WRITE_TOKEN`. Its default value is not used when OIDC credentials are present, but an explicitly passed token always takes priority. See [Authentication](#authentication).                                                                    |
| `oidcToken`          | No       | A Vercel OIDC token, used in place of `process.env.VERCEL_OIDC_TOKEN`. Pair with `storeId` (or `BLOB_STORE_ID`). Useful when your framework does not load `.env.local` into `process.env` automatically. See [Authentication](#authentication).                                                              |
| `storeId`            | No       | The Blob store id, used with OIDC. Defaults to `process.env.BLOB_STORE_ID`. The SDK accepts either `store_<id>` or `<id>` form. See [Authentication](#authentication).                                                                                                                                       |
| `addRandomSuffix`    | No       | A boolean specifying whether to add a random suffix to the pathname. It defaults to `false`.                                                                                                                                                                                                                 |
| `allowOverwrite`     | No       | A boolean to allow overwriting blobs. By default an error will be thrown if you try to overwrite a blob by using the same `pathname` for multiple blobs.                                                                                                                                                     |
| `cacheControlMaxAge` | No       | A number in seconds to configure the edge and browser cache. Defaults to one month. See the [caching](/docs/storage/vercel-blob#caching) documentation for more details.                                                                                                                                     |
| `ifMatch`            | No       | An ETag value. The copy only succeeds if the source blob's current ETag matches this value. Use this for [conditional writes](/docs/vercel-blob#conditional-writes) to prevent copying a blob that has been modified since you last read it. Throws `BlobPreconditionFailedError` if the ETag doesn't match. |
| `abortSignal`        | No       | An [AbortSignal](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal) to cancel the operation                                                                                                                                                                                                       |

`copy()` returns a `JSON` object with the following data for the copied blob object:

TypeScriptPython

```
result.pathname             # str
result.content_type         # str
result.content_disposition  # str
result.url                  # str
result.download_url         # str
result.etag                 # str
```

An example blob is:

```
{
  "pathname": "profilesv1/user-12345-copy.txt",
  "contentType": "text/plain",
  "contentDisposition": "attachment; filename=\"user-12345-copy.txt\"",
  "url": "https://ce0rcu23vrrdzqap.public.blob.vercel-storage.com/profilesv1/user-12345-copy.txt",
  "downloadUrl": "https://ce0rcu23vrrdzqap.public.blob.vercel-storage.com/profilesv1/user-12345-copy.txt?download=1",
  "etag": "\"a1b2c3d4e5f6\""
}
```

## [Multipart Uploads](#multipart-uploads)[](#multipart-uploads)

When uploading large files you should use multipart uploads to have a more reliable upload process. A multipart upload splits the file into multiple parts, uploads them in parallel and retries failed parts. This process consists of three phases: creating a multipart upload, uploading the parts and completing the upload. `@vercel/blob` offers three different ways to create multipart uploads:

### [Automatic](#automatic)[](#automatic)

This method has everything baked in and is easiest to use. It's part of the `put` and `upload` API's. Under the hood it will start the upload, split your file into multiple parts with the same size, upload them in parallel and complete the upload.

TypeScriptPython

```
from vercel.blob import BlobClient
 
client = BlobClient()
 
with open("large-movie.mp4", "rb") as f:
    file_data = f.read()
 
blob = client.put(
    "videos/large-movie.mp4",
    file_data,
    access="private",  # or "public",
    content_type="video/mp4",
)
```

### [Manual](#manual)[](#manual)

This method gives you full control over the multipart upload process. It consists of three phases:

Phase 1: Create a multipart upload

TypeScriptPython

```
from vercel.blob import create_multipart_upload
 
multipart_upload = create_multipart_upload(
    "videos/intro.mp4",
    access="private",  # or "public",
    content_type="video/mp4",
    add_random_suffix=True,
)
```

`createMultipartUpload` accepts the following parameters:

*   `pathname`: (Required) A string specifying the path inside the blob store. This will be the base value of the return URL and includes the filename and extension.
*   `options`: (Required) A `JSON` object with the following required and optional parameters:

| Parameter            | Required | Values                                                                                                                                                                                                                                                                                                                           |
| -------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `access`             | Yes      | [`'private'` or `'public'`](/docs/vercel-blob#private-and-public-storage). Determines the access level of the blob.                                                                                                                                                                                                              |
| `contentType`        | No       | The [media type](https://developer.mozilla.org/docs/Web/HTTP/Headers/Content-Type) for the file. If not specified, it's derived from the file extension. Falls back to `application/octet-stream` when no extension exists or can't be matched.                                                                                  |
| `token`              | No       | A static read-write token. Defaults to `process.env.BLOB_READ_WRITE_TOKEN`. Its default value is not used when OIDC credentials are present, but an explicitly passed token always takes priority. You can also pass a client token created with `generateClientTokenFromReadWriteToken`. See [Authentication](#authentication). |
| `oidcToken`          | No       | A Vercel OIDC token, used in place of `process.env.VERCEL_OIDC_TOKEN`. Pair with `storeId` (or `BLOB_STORE_ID`). Useful when your framework does not load `.env.local` into `process.env` automatically. See [Authentication](#authentication).                                                                                  |
| `storeId`            | No       | The Blob store id, used with OIDC. Defaults to `process.env.BLOB_STORE_ID`. The SDK accepts either `store_<id>` or `<id>` form. See [Authentication](#authentication).                                                                                                                                                           |
| `addRandomSuffix`    | No       | A boolean specifying whether to add a random suffix to the pathname. It defaults to `true`.                                                                                                                                                                                                                                      |
| `cacheControlMaxAge` | No       | A number in seconds to configure the edge and browser cache. Defaults to one month. See the [caching](/docs/storage/vercel-blob#caching) documentation for more details.                                                                                                                                                         |
| `abortSignal`        | No       | An [AbortSignal](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal) to cancel the operation                                                                                                                                                                                                                           |

`createMultipartUpload()` returns a `JSON` object with the following data for the created upload:

```
{
  "key": "string",
  "uploadId": "string"
}
```

Phase 2: Upload all the parts

In the multipart uploader process, it's necessary for you to manage both memory usage and concurrent upload requests. Additionally, each part must be a minimum of 5MB, except the last one which can be smaller, and all parts should be of equal size.

TypeScriptPython

```
from vercel.blob import upload_part
 
chunk1 = file_data[0:5*1024*1024] # minimum 5MB each, except last part
part = upload_part(
    "videos/intro.mp4",
    chunk1,
    access="private",  # or "public",
    upload_id=multipart_upload.upload_id,
    key=multipart_upload.key,
    part_number=1,
)
```

`uploadPart` accepts the following parameters:

*   `pathname`: (Required) Same value as the `pathname` parameter passed to `createMultipartUpload`
*   `chunkBody`: (Required) A blob object as `ReadableStream`, `String`, `ArrayBuffer` or `Blob` based on these [supported body types](https://developer.mozilla.org/docs/Web/API/fetch#body)
*   `options`: (Required) A `JSON` object with the following required and optional parameters:

| Parameter     | Required | Values                                                                                                                                                                                                                                                                                                                           |
| ------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `access`      | Yes      | [`'private'` or `'public'`](/docs/vercel-blob#private-and-public-storage). Determines the access level of the blob.                                                                                                                                                                                                              |
| `partNumber`  | Yes      | A number identifying which part is uploaded                                                                                                                                                                                                                                                                                      |
| `key`         | Yes      | A string returned from `createMultipartUpload` which identifies the blob object                                                                                                                                                                                                                                                  |
| `uploadId`    | Yes      | A string returned from `createMultipartUpload` which identifies the multipart upload                                                                                                                                                                                                                                             |
| `token`       | No       | A static read-write token. Defaults to `process.env.BLOB_READ_WRITE_TOKEN`. Its default value is not used when OIDC credentials are present, but an explicitly passed token always takes priority. You can also pass a client token created with `generateClientTokenFromReadWriteToken`. See [Authentication](#authentication). |
| `oidcToken`   | No       | A Vercel OIDC token, used in place of `process.env.VERCEL_OIDC_TOKEN`. Pair with `storeId` (or `BLOB_STORE_ID`). Useful when your framework does not load `.env.local` into `process.env` automatically. See [Authentication](#authentication).                                                                                  |
| `storeId`     | No       | The Blob store id, used with OIDC. Defaults to `process.env.BLOB_STORE_ID`. The SDK accepts either `store_<id>` or `<id>` form. See [Authentication](#authentication).                                                                                                                                                           |
| `abortSignal` | No       | An [AbortSignal](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal) to cancel the operation                                                                                                                                                                                                                           |

`uploadPart()` returns a `JSON` object with the following data for the uploaded part:

```
{
  "etag": "string",
  "partNumber": "number"
}
```

Phase 3: Complete the multipart upload

TypeScriptPython

```
from vercel.blob import complete_multipart_upload
 
blob = complete_multipart_upload(
    "videos/intro.mp4",
    [part1, part2, part3],
    access="private",  # or "public",
    upload_id=multipart_upload.upload_id,
    key=multipart_upload.key,
)
```

`completeMultipartUpload` accepts the following parameters:

*   `pathname`: (Required) Same value as the `pathname` parameter passed to `createMultipartUpload`
*   `parts`: (Required) An array containing all the uploaded parts
*   `options`: (Required) A `JSON` object with the following required and optional parameters:

| Parameter            | Required | Values                                                                                                                                                                                                                                                                                                                           |
| -------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `access`             | Yes      | [`'private'` or `'public'`](/docs/vercel-blob#private-and-public-storage). Determines the access level of the blob.                                                                                                                                                                                                              |
| `key`                | Yes      | A string returned from `createMultipartUpload` which identifies the blob object                                                                                                                                                                                                                                                  |
| `uploadId`           | Yes      | A string returned from `createMultipartUpload` which identifies the multipart upload                                                                                                                                                                                                                                             |
| `contentType`        | No       | The [media type](https://developer.mozilla.org/docs/Web/HTTP/Headers/Content-Type) for the file. If not specified, it's derived from the file extension. Falls back to `application/octet-stream` when no extension exists or can't be matched.                                                                                  |
| `token`              | No       | A static read-write token. Defaults to `process.env.BLOB_READ_WRITE_TOKEN`. Its default value is not used when OIDC credentials are present, but an explicitly passed token always takes priority. You can also pass a client token created with `generateClientTokenFromReadWriteToken`. See [Authentication](#authentication). |
| `oidcToken`          | No       | A Vercel OIDC token, used in place of `process.env.VERCEL_OIDC_TOKEN`. Pair with `storeId` (or `BLOB_STORE_ID`). Useful when your framework does not load `.env.local` into `process.env` automatically. See [Authentication](#authentication).                                                                                  |
| `storeId`            | No       | The Blob store id, used with OIDC. Defaults to `process.env.BLOB_STORE_ID`. The SDK accepts either `store_<id>` or `<id>` form. See [Authentication](#authentication).                                                                                                                                                           |
| `addRandomSuffix`    | No       | A boolean specifying whether to add a random suffix to the pathname. It defaults to `true`.                                                                                                                                                                                                                                      |
| `cacheControlMaxAge` | No       | A number in seconds to configure the edge and browser cache. Defaults to one month. See the [caching](/docs/storage/vercel-blob#caching) documentation for more details.                                                                                                                                                         |
| `abortSignal`        | No       | An [AbortSignal](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal) to cancel the operation                                                                                                                                                                                                                           |

`completeMultipartUpload()` returns a `JSON` object with the following data for the created blob object:

```
{
  "pathname": "string",
  "contentType": "string",
  "contentDisposition": "string",
  "url": "string",
  "downloadUrl": "string",
  "etag": "string"
}
```

### [Uploader](#uploader)[](#uploader)

A less verbose way than the manual process is the multipart uploader method. It's a wrapper around the manual multipart upload process and takes care of the data that is the same for all the three multipart phases. This results in a simpler API, but still requires you to handle memory usage and concurrent upload requests.

Phase 1: Create the multipart uploader

TypeScriptPython

```
from vercel.blob import AsyncBlobClient
 
client = AsyncBlobClient()
uploader = await client.create_multipart_uploader(
    "examples/large-file.bin",
    content_type="application/octet-stream",
    add_random_suffix=True,
)
```

`createMultipartUploader` accepts the following parameters:

*   `pathname`: (Required) A string specifying the path inside the blob store. This will be the base value of the return URL and includes the filename and extension.
*   `options`: (Required) A `JSON` object with the following required and optional parameters:

| Parameter            | Required | Values                                                                                                                                                                                                                                                                                                                           |
| -------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `access`             | Yes      | [`'private'` or `'public'`](/docs/vercel-blob#private-and-public-storage). Determines the access level of the blob.                                                                                                                                                                                                              |
| `contentType`        | No       | The [media type](https://developer.mozilla.org/docs/Web/HTTP/Headers/Content-Type) for the file. If not specified, it's derived from the file extension. Falls back to `application/octet-stream` when no extension exists or can't be matched.                                                                                  |
| `token`              | No       | A static read-write token. Defaults to `process.env.BLOB_READ_WRITE_TOKEN`. Its default value is not used when OIDC credentials are present, but an explicitly passed token always takes priority. You can also pass a client token created with `generateClientTokenFromReadWriteToken`. See [Authentication](#authentication). |
| `oidcToken`          | No       | A Vercel OIDC token, used in place of `process.env.VERCEL_OIDC_TOKEN`. Pair with `storeId` (or `BLOB_STORE_ID`). Useful when your framework does not load `.env.local` into `process.env` automatically. See [Authentication](#authentication).                                                                                  |
| `storeId`            | No       | The Blob store id, used with OIDC. Defaults to `process.env.BLOB_STORE_ID`. The SDK accepts either `store_<id>` or `<id>` form. See [Authentication](#authentication).                                                                                                                                                           |
| `addRandomSuffix`    | No       | A boolean specifying whether to add a random suffix to the pathname. It defaults to `true`.                                                                                                                                                                                                                                      |
| `cacheControlMaxAge` | No       | A number in seconds to configure the edge and browser cache. Defaults to one month. See the [caching](/docs/storage/vercel-blob#caching) documentation for more details.                                                                                                                                                         |
| `abortSignal`        | No       | An [AbortSignal](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal) to cancel the operation                                                                                                                                                                                                                           |

`createMultipartUploader()` returns an `Uploader` object with the following attributes and methods:

TypeScriptPython

```
uploader.upload_id                              # string
uploader.key                                    # string
uploader.upload_part(part_number, chunk_body)   # method
uploader.complete(parts)                        # method
```

Phase 2: Upload all the parts

In the multipart uploader process, it's necessary for you to manage both memory usage and concurrent upload requests. Additionally, each part must be a minimum of 5MB, except the last one which can be smaller, and all parts should be of equal size.

TypeScriptPython

```
import asyncio
tasks = [
    uploader.upload_part(1, chunk_body_1),
    uploader.upload_part(2, chunk_body_2),
    uploader.upload_part(3, chunk_body_3),
]
parts = await asyncio.gather(*tasks)
```

`uploader.uploadPart` accepts the following parameters:

*   `partNumber`: (Required) A number identifying which part is uploaded
*   `chunkBody`: (Required) A blob object as `ReadableStream`, `String`, `ArrayBuffer` or `Blob` based on these [supported body types](https://developer.mozilla.org/docs/Web/API/fetch#body)

`uploader.uploadPart()` returns an object with the following data for the uploaded part:

TypeScriptPython

```
part.etag         # string
part.part_number  # int
```

Phase 3: Complete the multipart upload

TypeScriptPython

```
blob = await uploader.complete([part_1, part_2, part_3])
```

`uploader.complete` accepts the following parameters:

*   `parts`: (Required) An array containing all the uploaded parts

`uploader.complete()` returns an object with the following data for the created blob object:

TypeScriptPython

```
result.pathname             # string
result.content_type         # string
result.content_disposition  # string
result.url                  # string
result.download_url         # string
result.etag                 # string
```

## [Client uploads](#client-uploads)[](#client-uploads)

As seen in the [client uploads quickstart docs](/docs/storage/vercel-blob/client-upload), you can upload files directly from clients (like browsers) to the Blob store.

All client uploads related methods are available under `@vercel/blob/client`.

### [`upload()`](#upload)[](#upload)

The `upload` method is dedicated to [client uploads](/docs/storage/vercel-blob/client-upload). It fetches a client token on your server using the `handleUploadUrl` before uploading the blob. Read the [client uploads](/docs/storage/vercel-blob/client-upload) documentation to learn more.

```
upload(pathname, body, options);
```

It accepts the following parameters:

*   `pathname`: (Required) A string specifying the base value of the return URL
*   `body`: (Required) A blob object as `ReadableStream`, `String`, `ArrayBuffer` or `Blob` based on these [supported body types](https://developer.mozilla.org/docs/Web/API/fetch#body)
*   `options`: (Required) A `JSON` object with the following required and optional parameters:

| Parameter          | Required | Values                                                                                                                                                            |
| ------------------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `access`           | Yes      | [`'private'` or `'public'`](/docs/vercel-blob#private-and-public-storage). Determines the access level of the blob.                                               |
| `contentType`      | No       | A string indicating the [media type](https://developer.mozilla.org/docs/Web/HTTP/Headers/Content-Type). By default, it's extracted from the pathname's extension. |
| `handleUploadUrl`  | Yes\*    | A string specifying the route to call for generating client tokens for [client uploads](/docs/storage/vercel-blob/client-upload).                                 |
| `clientPayload`    | No       | A string to be sent to your `handleUpload` server code. Example use-case: attaching the post id an image relates to. So you can use it to update your database.   |
| `multipart`        | No       | Pass `multipart: true` when uploading large files. It will split the file into multiple parts, upload them in parallel and retry failed parts.                    |
| `abortSignal`      | No       | An [AbortSignal](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal) to cancel the operation                                                            |
| `onUploadProgress` | No       | Callback to track upload progress: `onUploadProgress({loaded: number, total: number, percentage: number})`                                                        |

`upload()` returns a `JSON` object with the following data for the created blob object:

```
{
  pathname: string;
  contentType: string;
  contentDisposition: string;
  url: string;
  downloadUrl: string;
  etag: string;
}
```

An example `url` is:

`https://ce0rcu23vrrdzqap.public.blob.vercel-storage.com/profilesv1/user-12345-NoOVGDVcqSPc7VYCUAGnTzLTG2qEM2.txt`

### [`handleUpload()`](#handleupload)[](#handleupload)

A server-side route helper to manage client uploads, it has two responsibilities:

1.  Generate tokens for client uploads
2.  Listen for completed client uploads, so you can update your database with the URL of the uploaded file for example

```
handleUpload(options);
```

It accepts the following parameters:

*   `options`: (Required) A `JSON` object with the following parameters:

| Parameter                                         | Required | Values                                                                                                                                                                |
| ------------------------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `token`                                           | No       | A static read-write token used to verify and sign client uploads. Defaults to `process.env.BLOB_READ_WRITE_TOKEN`. OIDC tokens are not sufficient for `handleUpload`. |
| `request`                                         | Yes      | An `IncomingMessage` or `Request` object to be used to determine the action to take                                                                                   |
| [`onBeforeGenerateToken`](#onbeforegeneratetoken) | Yes      | A function to be called right before generating client tokens for client uploads. See below for usage                                                                 |
| [`onUploadCompleted`](#onuploadcompleted)         | Yes      | A function to be called by Vercel Blob when the client upload finishes. This is useful to update your database with the blob url that was uploaded                    |
| `body`                                            | Yes      | The request body                                                                                                                                                      |

`handleUpload()` returns:

```
Promise<
  | { type: 'blob.generate-client-token'; clientToken: string }
  | { type: 'blob.upload-completed'; response: 'ok' }
>;
```

#### [`onBeforeGenerateToken()`](#onbeforegeneratetoken)[](#onbeforegeneratetoken)

The `onBeforeGenerateToken` function runs on your server before the SDK generates a client token. You must authenticate and authorize the user inside this function. If you skip this step, your upload route allows anonymous uploads to your Blob store.

The function receives the following arguments:

*   `pathname`: The destination path for the blob
*   `clientPayload`: A string payload specified on the client when calling `upload()`
*   `multipart`: A boolean specifying whether the file is a multipart upload.

The function must return an object with the following properties:

| Parameter             | Required | Values                                                                                                                                                                                                                    |
| --------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `addRandomSuffix`     | No       | A boolean specifying whether to add a random suffix to the `pathname`. It defaults to `false`. We recommend using this option to ensure there are no conflicts in your blob filenames.                                    |
| `allowedContentTypes` | No       | An array of strings specifying the [media type](https://developer.mozilla.org/docs/Web/HTTP/Headers/Content-Type) that are allowed to be uploaded. By default, it's all content types. Wildcards are supported (`text/*`) |
| `maximumSizeInBytes`  | No       | A number specifying the maximum size in bytes that can be uploaded. The maximum is 5TB.                                                                                                                                   |
| `validUntil`          | No       | A number specifying the timestamp in ms when the token will expire. By default, it's now + 1 hour.                                                                                                                        |
| `allowOverwrite`      | No       | A boolean to allow overwriting blobs. By default an error will be thrown if you try to overwrite a blob by using the same `pathname` for multiple blobs.                                                                  |
| `cacheControlMaxAge`  | No       | A number in seconds to configure how long Blobs are cached. Defaults to one month. Cannot be set to a value lower than 1 minute. See the [caching](/docs/storage/vercel-blob#caching) documentation for more details.     |
| `callbackUrl`         | No       | A string specifying the URL that Vercel Blob will call when the upload completes. See [client uploads](/docs/storage/vercel-blob/client-upload) for examples.                                                             |
| `tokenPayload`        | No       | A string specifying a payload to be sent to your server on upload completion.                                                                                                                                             |

#### [`onUploadCompleted()`](#onuploadcompleted)[](#onuploadcompleted)

The `onUploadCompleted` function receives the following arguments:

*   `blob`: The blob that was uploaded. See the return type of [`put()`](#put) for more details.
*   `tokenPayload`: The payload that was defined in the [`onBeforeGenerateToken()`](#onbeforegeneratetoken) function.

### [Client uploads routes](#client-uploads-routes)[](#client-uploads-routes)

Here's an example Next.js App Router route handler that uses `handleUpload()`:

app/api/post/upload/route.ts

```
import { handleUpload, type HandleUploadBody } from '@vercel/blob/client';
import { NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
 
export async function POST(request: Request): Promise<NextResponse> {
  const body = (await request.json()) as HandleUploadBody;
 
  try {
    const jsonResponse = await handleUpload({
      body,
      request,
      onBeforeGenerateToken: async (pathname, clientPayload) => {
        // Authenticate and authorize users before generating the token.
        // Without this check, anyone can upload to your Blob store.
        const session = await auth();
        if (!session) {
          throw new Error('Not authenticated');
        }
 
        // When using clientPayload, validate it to prevent users from
        // modifying other users' data
        const { postId } = JSON.parse(clientPayload || '{}');
 
        return {
          allowedContentTypes: ['image/jpeg', 'image/png', 'image/webp'],
          tokenPayload: JSON.stringify({
            userId: session.user.id,
            postId,
          }),
        };
      },
      onUploadCompleted: async ({ blob, tokenPayload }) => {
        // This callback won't fire on localhost.
        // Use ngrok or similar for the full upload flow locally.
 
        console.log('blob upload completed', blob, tokenPayload);
 
        try {
          const { userId, postId } = JSON.parse(tokenPayload);
          // Safely update your database since the user was already authenticated
          // await db.update({ imageUrl: blob.url, postId, userId });
        } catch (error) {
          throw new Error('Could not update post');
        }
      },
    });
 
    return NextResponse.json(jsonResponse);
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : String(error) },
      { status: 400 },
    );
  }
}
```

## [Handling errors](#handling-errors)[](#handling-errors)

When you make a request to the SDK using any of the above methods, they will return an error if the request fails due to any of the following reasons:

*   Missing required parameters
*   An invalid token or a token that does not have access to the Blob object
*   Suspended Blob store
*   Blob file or Blob store not found
*   Precondition failed (when using `ifMatch` for [conditional writes](/docs/vercel-blob#conditional-writes) and the ETag doesn't match)
*   Unforeseen or unknown errors

To catch these errors, wrap your requests with a `try/catch` statement as shown below:

TypeScriptPython

```
from vercel.blob import BlobClient
from vercel.blob.errors import BlobError, BlobNotFoundError
 
try:
    client = BlobClient()
    client.put(
        "examples/file.txt", b"hello",
        access="private",  # or "public"
    )
except BlobNotFoundError:
    # handle a recognized error
    ...
except BlobError as e:
    # handle other blob errors
    ...
except Exception as e:
    # handle unknown errors
    ...
```
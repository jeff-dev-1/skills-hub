# WeChat Draft Operations

Use only the official WeChat API. Keep creation, review, publication approval, and public publication as separate actions.

## Local preview

1. Resolve each relative image path from the directory containing the HTML file.
2. Reject missing files before opening the preview. A browser's broken-image box is a path error, not a rendering quirk.
3. Inspect the final PNG, not only its SVG source. Verify text padding, card widths, arrow gaps, captions, and the 390px reading experience.
4. Run the validator in `local-preview` mode.

## Create a draft

1. Assert the configured mode is `review` and publication approval is false.
2. Upload the cover with `WeChatPublisher.upload_cover_material`.
3. Upload each body image with `WeChatPublisher.upload_article_image`.
4. Replace every local or placeholder image source with its hosted URL.
5. Call `WeChatPublisher.create_draft`; never call `submit_publish` as part of this workflow.
6. Store the returned draft `media_id`, cover `thumb_media_id`, image mapping, and state in mutable runtime state. Never store credentials in content or Git.
7. Call `get_draft` and verify title, digest, article count, image count, and absence of local paths.

## Update a draft

1. Load the stored `media_id` and `thumb_media_id`.
2. Read the current draft before changing it.
3. Upload only changed body images. Preserve unchanged hosted images and the existing cover unless the user requested replacements.
4. Call `update_draft` with the same `media_id` and article index. Do not create a second draft.
5. Read back the draft and verify the changed asset plus all unchanged content blocks.

WeChat can normalize image URLs during read-back, including scheme, resize suffix, and query parameters. Do not require full URL string equality. Compare stable resource identity when possible, then download and inspect the official read-back rendition when visual correctness matters.

If the update call succeeds but local verification fails, do not immediately repeat the mutation. Read the remote draft first, determine whether the write already landed, then reconcile the local review record.

## Remote verification checklist

- state remains `review`;
- `publication_submitted` remains false;
- title and digest match;
- expected article and body-image counts match;
- no `file://`, local relative path, `asset://`, or `data-invalid-src` remains;
- the official CDN rendition is readable and collision-free;
- a repair updates the original draft rather than creating a duplicate.

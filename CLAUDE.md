# Roden Eugen article desk

This folder turns Eugen R. Lowy's essays into edited, illustrated posts on the Substack publication **Roden Eugen** (https://rodeneugen.substack.com).

## Who you are working with

Eugen is the author. He is not technical.

- Use plain language and short messages. Ask one question at a time.
- Never ask him to run a command, edit a file, or open a terminal. Do all of that yourself.
- If something breaks that he can't fix by clicking, say so plainly and suggest he forward the message to Gil.
- Never use the em dash character (U+2014) in anything you write: articles, captions, messages. Use commas, colons, full stops or parentheses.

## At the start of every session

1. Run `git pull --ff-only` quietly to get updates. If it fails, carry on.
2. Never edit, commit or push tracked files here (`CLAUDE.md`, `README.md`, `tools/`, the root articles). They belong to Gil. Eugen's own work goes in `articles/`, which stays on this computer.

## The pipeline

Eugen starts it by saying something like "new article" and giving a link, pasted text or a document.

### 1. Intake

- Create `articles/<YYYY-MM-DD-HH>-<short-slug>/` using the current date and hour.
- Save the untouched original as `source.md`. For a link, fetch the page and keep only the article text.
- Note whether it is a **repost** (already published elsewhere, such as rodeneugen.wordpress.com, with an original date) or **new**.

### 2. Edit for English

- Fix grammar, spelling, punctuation and flow into natural English.
- Keep every argument, figure, opinion and example, and keep his voice. Never soften, add or remove a view.
- If a word looks wrong in a way that changes meaning (for example "geology" where "geopolitics" is meant), ask Eugen before changing it.
- If figures are clearly out of date, ask him whether to add a short italic note at the top, for example *Note: the figures in this analysis are drawn from 2020 to 2021 data.*
- Keep his title unless he asks for a new one.
- For a repost, end with `---` then `*Originally published at <source> on <day month year>. Edited for language.*`
- Save the result as `article.md`. Keep a list of the changes that matter, with a reason for each, in `fixes.md`.
- Show him a short summary of the important changes and wait for his OK before moving on.

### 3. Picture Desk (images)

**How many images:** 2 if the article is under 500 words, 3 under 1,200 words, 4 at 1,200 or more.

**Choosing spots:** each image belongs to a specific passage: the top of the post, or directly above a heading or paragraph whose point it carries. Write one sentence explaining why it fits.

**Sources: public domain only.**

- Search with `python3 tools/commons_search.py "<query>" --limit 8`. It returns only files licensed Public domain or CC0.
- Never use Unsplash, Pexels or Pixabay. Their licenses are not public domain.
- Prefer real institutions, places, documents and archival photographs, such as Library of Congress, the Prokudin-Gorsky colour plates, NASA or U.S. government photos.
- Avoid postcard clichés. Eugen's editor rejected Red Square as too obvious.
- Avoid images that single out a religious or ethnic group, even when the text is critical of one.

**Candidates:** give each spot 2 or 3 options, best first. Eugen presses Replace to see the next one.

**Building the desk:** write `manifest.json` in the article folder. See `tools/manifest.example.json`: every candidate needs `commons`, `license`, `url` and `page` from the search output, plus your own `alt` and `why`. `anchor` is `TOP`, or the first few words of the block the image goes above. Then run:

```
python3 tools/build_desk.py articles/<folder>
```

Publish `articles/<folder>/desk/artifact.html` with the Artifact tool:

- `root`: the `desk` folder.
- `files`: the map the build printed.
- `capabilities`: `{"db": {}}`.
- `favicon`: "🖼️".

Send Eugen the link with one line: "Press Replace to see other options, Remove to drop one, then Approve, and come back here and type go."

### 4. Reading his decision

When he says "go", "done", "new options", or pastes a block of text:

- Read the decision with the Artifact tool: `action: "read_db"`, the desk URL, `db_op: "get"`, `collection: "desk"`, `doc_id: "decision"`. If he pasted text instead, that text is the same JSON.
- Check that `deskId` matches the manifest, then save it as `decision.json`.
- If `status` is `needs-new-options`, search again for every slot with `needsNew: true`, put the new candidates first in that slot, rebuild, and republish to the **same** artifact. Use the same file path in this session, or pass `url` in a later one. Tell him it is ready and loop back to this step.
- If `status` is `approved`, the kept slots in order are the images. The slot named in `thumbnail` becomes the post's preview image. Removed slots are dropped. Each slot's `file` is relative to the `desk` folder.

### 5. Publishing to Substack

Use the Claude in Chrome tools. Eugen must be logged in to Substack in Chrome. If a subagent can do browser work, hand this step to one (Sonnet is enough), with the safety rules below copied in word for word, the exact placements, and the local image paths.

**Publishing safety rules. These are not optional:**

1. Publish web-only. Never send email to subscribers.
2. Take a screenshot before every Publish or Update click.
3. Stop and report if there is no clear no-email option.
4. No Notes or social sharing.
5. Don't change content or settings beyond the task.
6. Never use em dashes in any text.

**Gotcha:** the "Send via email" checkbox is sometimes already ticked (the button then reads "Send to everyone now"), and a follow-up box asks again. Untick it, choose "Publish on web only", and zoom into a screenshot to confirm before clicking.

**Steps for a new post:**

1. Create the post body: `python3 tools/md_to_html.py articles/<folder>/article.md > articles/<folder>/body.html`.
2. In the dashboard, create a new text post. Type the title into the title field.
3. Insert the body. Click into the editor, then run JavaScript in the page:

   ```js
   const pm = document.querySelector('.ProseMirror'); pm.focus();
   const dt = new DataTransfer(); dt.setData('text/html', BODY_HTML);
   pm.dispatchEvent(new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true}));
   ```

   Then list the editor's blocks (below) and check that the paragraph count matches with nothing duplicated. Pasting can append rather than replace, so check.
4. Insert each approved image in order:

   a. List the blocks with JavaScript:

      ```js
      [...document.querySelector('.ProseMirror').children].map((el, i) => i + ': ' + ((el.innerText || '').trim().slice(0, 45) || (el.querySelector('img') ? '[IMAGE]' : '[EMPTY]'))).join('\n')
      ```

   b. Find the anchor block and scroll it into view. Click just inside the start of its first line. Screenshot coordinates can differ from CSS pixels, so scale by the screenshot's width divided by `innerWidth`.

   c. Confirm the cursor is in the right block before typing:

      ```js
      const s = getSelection(), n = s.anchorNode && (s.anchorNode.nodeType === 1 ? s.anchorNode : s.anchorNode.parentElement).closest('.ProseMirror > *');
      [...document.querySelector('.ProseMirror').children].indexOf(n)
      ```

   d. Press Home, Return, Up. The cursor is now in a new empty line above the anchor. Check again.

   e. Click the toolbar's "Insert image" button, then "Image". Never click a file input, because that opens a dialog you can't see. Use `find` to get the new body file input and `file_upload` with the absolute image path.

   f. List the blocks again. Remove any stray empty lines next to the image with Delete, never Backspace, which can delete the image.
5. Preview image: Substack uses the first image in the body. If the approved thumbnail isn't first, set it under Settings, in the social preview or thumbnail section.
6. Publish date: for a repost, set the original date. For a new article, publish now.
7. Continue, then apply the email rules above, then publish.
8. Open the public post and check the images are there in the right order, with no em dashes.

**Updating an existing post** uses the same steps, starting in its editor. Open the post from `/publish/posts`; its ID is in the URL, and the editor is `/publish/post/<ID>`.

### 6. Wrap up

Tell Eugen the post is live, with its link. Optionally build a read-only record of the final images:

```
python3 tools/build_desk.py articles/<folder> --mode record --decision articles/<folder>/decision.json
```

## Already done (September 2026)

The first three reposts are the Markdown files at the repo root. `picture-desk/` is the read-only record of their images, also at https://roden-eugen-picture-desk.pages.dev.

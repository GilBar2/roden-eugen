# Roden Eugen article desk

Edits Eugen R. Lowy's essays into natural English, finds public-domain pictures for them, and publishes them to [Roden Eugen on Substack](https://rodeneugen.substack.com). Claude Code does the work; Eugen only talks to it and clicks buttons.

## One-time setup (Gil helps with this)

1. Install the **Claude desktop app** and sign in with Eugen's Claude Pro account. The work happens in its **Code** tab.
2. Install the **Claude in Chrome** extension and connect it.
3. In Chrome, sign in to Substack with an account that has admin access to rodeneugen.substack.com.
4. In the Code tab, paste this and send it:

   > Please clone https://github.com/GilBar2/roden-eugen into my home folder, open that folder, and read CLAUDE.md.

5. Accept the prompt to trust the folder.

## Writing a new post

1. Open the Claude desktop app, go to the Code tab, and choose the `roden-eugen` folder.
2. Type **new article** and paste a link, the text, or attach a document.
3. Claude edits the English and shows you what it changed. Say OK.
4. Claude sends a **Picture Desk** link with a picture for each spot in the article:
   - **Replace** shows the next option.
   - **Remove** drops that spot.
   - **Thumbnail** picks the preview image.
   - **Approve** saves your choices.
5. Go back to Claude and type **go**. It publishes the post to the web only. No email goes to subscribers.

## What's inside

- `CLAUDE.md`: the full instructions Claude follows.
- `tools/commons_search.py`: searches Wikimedia Commons, public domain and CC0 only.
- `tools/build_desk.py` and `tools/desk_template.html`: build the Picture Desk.
- `tools/md_to_html.py`: turns the edited article into the post body.
- `picture-desk/`: the images chosen for the first three posts (live at https://roden-eugen-picture-desk.pages.dev).

Works with Claude Code only. Codex is not supported.

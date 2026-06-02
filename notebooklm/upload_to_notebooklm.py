"""
upload_to_notebooklm.py — upload COMFHA Paper 1 documents to NotebookLM
and generate Audio Overview + Study Guide.

Sources cover the full preparation set: paper, talk script, speaker notes,
literature review, science notes, methods reference, review history,
and plain-language summary.

Requires: storage_state.json from MacBook login
Run:  source ~/research-env/bin/activate && python3 notebooklm/upload_to_notebooklm.py
"""
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── Core paper ────────────────────────────────────────────────────────────────
# ── Presentation prep ─────────────────────────────────────────────────────────
# ── Science background ────────────────────────────────────────────────────────
# ── Review / Q&A prep ─────────────────────────────────────────────────────────
SOURCES = [
    # Core paper
    ROOT / "paper" / "latex" / "main.pdf",          # full manuscript (19 pp)
    ROOT / "brief_me.md",                           # key numbers cheat-sheet
    ROOT / "notebooklm" / "narrative_summary.md",   # plain-language summary

    # Talk preparation
    ROOT / "slides" / "TALK_SCRIPT.md",             # full speaker script
    ROOT / "slides" / "speaker_notes.md",           # per-slide speaker notes
    ROOT / "slides" / "PRESENTATION_CHEATSHEET.md", # quick-reference during talk
    ROOT / "slides" / "SLIDE_OUTLINE.md",           # slide structure overview

    # Science background
    ROOT / "docs" / "LITERATURE_REVIEW.md",         # literature context
    ROOT / "docs" / "COMFHA_Science_Notes.md",      # lab science notes
    ROOT / "docs" / "METHODS.md",                   # methods reference

    # Review & Q&A prep
    ROOT / "review-stage" / "AUTO_REVIEW.md",       # full review history (rounds 1–12)
    ROOT / "CITATION_AUDIT.md",                     # citation audit findings
]

NOTEBOOK_TITLE = "COMFHA Paper 1 — BLG Adsorption at Air-Water Interface"


async def main() -> None:
    try:
        from notebooklm import NotebookLMClient
    except ImportError:
        print("ERROR: notebooklm-py not installed. Run:")
        print("  pip install 'notebooklm-py[browser]'")
        sys.exit(1)

    missing = [s for s in SOURCES if not s.exists()]
    if missing:
        print("ERROR: Missing source files:")
        for m in missing:
            print(f"  {m}")
        sys.exit(1)

    print(f"Connecting to NotebookLM (using saved session)...")
    async with NotebookLMClient.from_storage() as client:

        print(f"\nCreating notebook: '{NOTEBOOK_TITLE}'")
        notebook = await client.notebooks.create(NOTEBOOK_TITLE)
        nb_id = notebook.id
        print(f"  Notebook ID: {nb_id}")

        for source_path in SOURCES:
            print(f"\nUploading: {source_path.name} ...")
            try:
                await client.sources.add_file(nb_id, str(source_path))
                print(f"  ✓ {source_path.name}")
            except Exception as e:
                print(f"  ✗ Failed: {e}")

        print("\nWaiting for sources to process...")
        await asyncio.sleep(15)

        # Audio Overview
        print("\nGenerating Audio Overview (podcast)...")
        try:
            audio = await client.artifacts.generate(nb_id, "audio")
            audio_result = await client.artifacts.poll(nb_id, audio.id)
            out_audio = ROOT / "notebooklm" / "overview_podcast.mp3"
            await client.artifacts.download(nb_id, audio_result.id, str(out_audio))
            print(f"  ✓ Saved: {out_audio}")
        except Exception as e:
            print(f"  ✗ Audio generation failed: {e}")

        # Study Guide
        print("\nGenerating Study Guide...")
        try:
            guide = await client.sources.guide(nb_id)
            out_guide = ROOT / "notebooklm" / "study_guide.md"
            out_guide.write_text(str(guide))
            print(f"  ✓ Saved: {out_guide}")
        except Exception as e:
            print(f"  ✗ Study guide failed: {e}")

        print(f"\n{'='*50}")
        print(f"Done! Notebook: {NOTEBOOK_TITLE}")
        print(f"Notebook ID:   {nb_id}")
        print(f"View at: https://notebooklm.google.com")
        print(f"\nAll sources also accessible locally under:")
        print(f"  {ROOT / 'notebooklm'}/")


if __name__ == "__main__":
    asyncio.run(main())

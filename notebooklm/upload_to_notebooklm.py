"""
upload_to_notebooklm.py — upload COMFHA Paper 1 documents to NotebookLM
and generate Audio Overview + Video.

Requires: storage_state.json from MacBook login
Run:  source ~/research-env/bin/activate && python3 notebooklm/upload_to_notebooklm.py
"""
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SOURCES = [
    ROOT / "paper" / "latex" / "main.pdf",
    ROOT / "notebooklm" / "narrative_summary.md",
    ROOT / "brief_me.md",
    ROOT / "review-stage" / "AUTO_REVIEW.md",
]

NOTEBOOK_TITLE = "COMFHA Paper 1 — BLG Adsorption at Air-Water Interface"


async def main():
    try:
        from notebooklm import NotebookLMClient
    except ImportError:
        print("ERROR: notebooklm-py not installed. Run:")
        print("  pip install 'notebooklm-py[browser]'")
        sys.exit(1)

    # Verify sources exist
    missing = [s for s in SOURCES if not s.exists()]
    if missing:
        print("ERROR: Missing source files:")
        for m in missing:
            print(f"  {m}")
        sys.exit(1)

    print(f"Connecting to NotebookLM (using saved session)...")
    async with NotebookLMClient.from_storage() as client:

        # Create notebook
        print(f"\nCreating notebook: '{NOTEBOOK_TITLE}'")
        notebook = await client.notebooks.create(NOTEBOOK_TITLE)
        nb_id = notebook.id
        print(f"  Notebook ID: {nb_id}")

        # Upload sources one by one
        for source_path in SOURCES:
            print(f"\nUploading: {source_path.name} ...")
            try:
                await client.sources.add_file(nb_id, str(source_path))
                print(f"  ✓ {source_path.name}")
            except Exception as e:
                print(f"  ✗ Failed: {e}")

        print("\nWaiting for sources to process...")
        await asyncio.sleep(10)

        # Generate Audio Overview
        print("\nGenerating Audio Overview (podcast)...")
        try:
            audio = await client.artifacts.generate(nb_id, "audio")
            print(f"  ✓ Audio queued — polling...")
            audio_result = await client.artifacts.poll(nb_id, audio.id)
            out_audio = ROOT / "notebooklm" / "overview_podcast.mp3"
            await client.artifacts.download(nb_id, audio_result.id, str(out_audio))
            print(f"  ✓ Saved: {out_audio}")
        except Exception as e:
            print(f"  ✗ Audio generation failed: {e}")

        # Generate Video
        print("\nGenerating Video Overview...")
        try:
            video = await client.artifacts.generate(nb_id, "video")
            print(f"  ✓ Video queued — polling (this takes a few minutes)...")
            video_result = await client.artifacts.poll(nb_id, video.id, timeout=600)
            out_video = ROOT / "notebooklm" / "overview_video.mp4"
            await client.artifacts.download(nb_id, video_result.id, str(out_video))
            print(f"  ✓ Saved: {out_video}")
        except Exception as e:
            print(f"  ✗ Video generation failed: {e}")

        # Generate Study Guide
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
        print(f"Outputs in: {ROOT / 'notebooklm'}/")


if __name__ == "__main__":
    asyncio.run(main())

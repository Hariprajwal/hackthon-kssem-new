# V20.8 Golden Pipeline Dependency Map

This map shows exactly how the files in your current highly-stabilized V20.8 pipeline relate to each other, both directly (called by) and indirectly (triggered as subprocesses).

## 🗺️ High-Level Flow (Mermaid Diagram)

```mermaid
graph TD
    %% Core Orchestrator
    config["config/manga_config.py &lt;br&gt; (Defines Manga Rules)"] --> CP2
    CP2["checkpoint_2.py &lt;br&gt; (The Main Hub)"]

    %% Phase 1: Scraper
    CP2 --&gt;|1. Triggers| Scraper["modules/scraper/omni_scraper.py"]
    Scraper -.Playwright.-&gt; Web["Web Sites (Weebcentral, etc.)"]

    %% Phase 2: CV
    CP2 --&gt;|2. Triggers| Slicer["modules/vision/panel_segmenter.py"]
    CP2 --&gt;|3. Triggers| OCR["modules/vision/_ocr_worker.py &lt;br&gt; (Using RapidOCR)"]

    %% Phase 3: AI Agents
    CP2 --&gt;|4. Sends Data To| Agents["modules/agents.py &lt;br&gt; (RecapCrew / Cerebras)"]
    Agents -.API.-&gt; Cerebras["Cerebras AI &lt;br&gt; (Epic Brian &amp; Reactor Ana script)"]

    %% Phase 4: Audio Synthesis
    CP2 --&gt;|5. Passes Script To| XTTS["modules/audio/xtts_client.py"]
    XTTS --&gt;|Direct Call| EdgeTTS["modules/audio/edge_tts_client.py &lt;br&gt; (Pitch/Rate Engine)"]
    XTTS -.Fallback.-&gt; Piper["Local Piper TTS"]

    %% Phase 5: Rendering (Indirect)
    CP2 --&gt;|6. Spawns Subprocess| Render["render_worker.py &lt;br&gt; (A/V Sync &amp; Motion)"]
    Render -.Uses.-&gt; FFMPEG_Render["MoviePy &amp; FFMPEG (threads=4)"]

    %% Phase 6: Assembly &amp; Upload
    CP2 --&gt;|7. Stitches Chunks| FFMPEG["FFMPEG CLI Call"]
    CP2 --&gt;|8. Triggers| YT["modules/upload_service/youtube_uploader.py"]
    YT -.Uploads.-&gt; YouTube["YouTube Output"]
```

---

## 🔗 Deep-Dive: File Relationships

### 1. [checkpoint_2.py](file:///d:/downloads/automated_youtube_channel/checkpoint_2.py) (The Master Controller)
This is the heart of the V20.8 pipeline. **Nothing happens unless this file commands it.**
*   **Directly Imports**: [manga_config.py](file:///d:/downloads/automated_youtube_channel/config/manga_config.py), [omni_scraper.py](file:///d:/downloads/automated_youtube_channel/modules/scraper/omni_scraper.py), `panel_segmenter.py`, [agents.py](file:///d:/downloads/automated_youtube_channel/modules/agents.py), [xtts_client.py](file:///d:/downloads/automated_youtube_channel/modules/audio/xtts_client.py), and `youtube_uploader.py`.
*   **Indirectly Controls**: [render_worker.py](file:///d:/downloads/automated_youtube_channel/render_worker.py). It does not *import* the renderer; it invokes it via a terminal subprocess (`subprocess.run(["python", "render_worker.py", ...])`) to ensure memory is completely cleared after each chunk is rendered.

### 2. The Audio Engine ([xtts_client.py](file:///d:/downloads/automated_youtube_channel/modules/audio/xtts_client.py) ➔ [edge_tts_client.py](file:///d:/downloads/automated_youtube_channel/modules/audio/edge_tts_client.py))
*   [checkpoint_2.py](file:///d:/downloads/automated_youtube_channel/checkpoint_2.py) calls [xtts_client.py](file:///d:/downloads/automated_youtube_channel/modules/audio/xtts_client.py) and hands it the script.
*   [xtts_client.py](file:///d:/downloads/automated_youtube_channel/modules/audio/xtts_client.py) parses the script for `[Brian]` and `[Ana]` tags.
*   It then **directly calls** [edge_tts_client.py](file:///d:/downloads/automated_youtube_channel/modules/audio/edge_tts_client.py)'s [sync_synthesize()](file:///d:/downloads/automated_youtube_channel/modules/audio/edge_tts_client.py#26-49) function, passing custom `rate` and `pitch` values based on the Mood map.

### 3. The Vision Engine (`panel_segmenter.py` ➔ `_ocr_worker.py`)
*   [omni_scraper.py](file:///d:/downloads/automated_youtube_channel/modules/scraper/omni_scraper.py) rips large vertical strips from the web.
*   [checkpoint_2.py](file:///d:/downloads/automated_youtube_channel/checkpoint_2.py) passes these strips to `panel_segmenter.py`, which uses OpenCV to slice them at the white/black gutters.
*   The sliced panels are then handed to the OCR engine (`RapidOCR`) to check for watermarks. As of V20.7, this phase also creates `.ocr.json` sidecar files (indirect caching).

### 4. The Render Engine ([render_worker.py](file:///d:/downloads/automated_youtube_channel/render_worker.py))
*   This file is **isolated**. It doesn't import from [checkpoint_2.py](file:///d:/downloads/automated_youtube_channel/checkpoint_2.py), preventing circular dependencies.
*   It runs mathematical motion (Ken Burns zoom/pan).
*   **Indirect System Reliance**: It heavily relies on the `moviepy` library and the [pydub](file:///d:/downloads/automated_youtube_channel/modules/audio/xtts_client.py#38-50) library (for V20.7's silence trimming to fix A/V sync) before handing the ultimate compilation over to FFMPEG.

import webvtt


def vtt_to_text(vtt_content: str) -> str:
    try:
        captions = webvtt.from_string(vtt_content)
        return " ".join(caption.text.strip() for caption in captions)
    except Exception as e:
        raise ValueError(f"Invalid VTT content: {e}") from e

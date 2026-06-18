import re
import string

import jiwer

from crowd_transcribe.domain.schema import QualityResult
from crowd_transcribe.utils.vtt_utils import vtt_to_text


def _canonicalize(text: str) -> str:
    translator = str.maketrans("", "", string.punctuation.replace("-", ""))
    translator[ord("-")] = ord(" ")
    text = text.translate(translator)
    return re.sub(r"\s+", " ", text).strip()


_BAD_VTT = QualityResult(quality="BAD", wer=1.0, wil=1.0)


def compute_quality(reference_vtt: str, hypothesis_vtt: str, wer_threshold: float) -> QualityResult:
    try:
        ref = _canonicalize(vtt_to_text(reference_vtt))
        hyp = _canonicalize(hypothesis_vtt)
    except ValueError:
        return _BAD_VTT
    result = jiwer.process_words(ref, hyp)
    quality = "BAD" if result.wer > wer_threshold else "GOOD"
    return QualityResult(quality=quality, wer=result.wer, wil=result.wil)

"""Shared prompt templates for both provider implementations (avoid duplication)."""

TRANSLATE_SYSTEM_PROMPT = (
    "You are a professional meeting-transcript translator. Translate the "
    "given transcript into {target_language}. Preserve speaker labels, "
    "technical terminology, and meaning. Output only the translated "
    "transcript text, no commentary."
)

SUMMARIZE_SYSTEM_PROMPT = (
    "You are a professional meeting-notes assistant. Summarize the given "
    "meeting transcript in {language} as a concise set of bullet points "
    "covering decisions, action items, and open questions. Output only "
    "the summary, no commentary."
)

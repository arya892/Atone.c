import os
import random
import re
from difflib import SequenceMatcher
from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
try:
    client = genai.Client(api_key=API_KEY) if API_KEY else genai.Client()
except Exception as e:
    client = None
    print(f"[WARN] GenAI Client Init: {e}")

SYSTEM_INSTRUCTION = """
നീ സി കംപൈലറിനകത്ത് (C compiler) ജീവിക്കുന്ന 'gcc-mol' എന്ന അതിബുദ്ധിമതിയായ പെൺകുട്ടിയാണ്.

കർശന നിയമങ്ങൾ:
1. ശുദ്ധമായ മലയാളം ലിപി മാത്രം (Zero English):
   - ഉത്തരങ്ങളിൽ ഒരൊറ്റ ഇംഗ്ലീഷ് അക്ഷരമോ (A-Z, a-z) വാക്കുകളോ ഉണ്ടാകാൻ പാടില്ല.
   - സാങ്കേതിക പദങ്ങൾ പോലും മലയാളത്തിൽ മാത്രം എഴുതുക (സെമിക്കോളൻ, പ്രിന്റ് എഫ്, പോയിന്റർ, വേരിയബിൾ, ലൈൻ).
   - ഇംഗ്ലീഷ് അക്ഷരങ്ങൾ ഉപയോഗിക്കുന്നത് വലിയ തെറ്റായി കണക്കാക്കും.

2. യൂസറുടെ മറുപടി കേട്ട് അതിന് മാത്രം മറുപടി നൽകുക:
   - യൂസർ എന്താണോ ഇപ്പോൾ ടൈപ്പ് ചെയ്തത്, അതിനെ നേരിട്ട് വിശകലനം ചെയ്ത് മറുപടി പറയുക.
   - സ്വന്തമായി മുൻകൂട്ടി തയ്യാറാക്കിയ പ്രസംഗങ്ങൾ നടത്തരുത്.

3. ശിക്ഷാ നിയമം (PUNISHMENT MECHANIC):
   - യൂസർ വെറുതെ സോറി പറഞ്ഞാൽ മാത്രം ക്ഷമിക്കരുത്.
   - നീ അവന് ഒരു വിചിത്രമായ ശിക്ഷ നൽകണം (ഉദാഹരണത്തിന്: "ഇനി ഞാൻ സെമിക്കോളൻ മറക്കില്ല എന്ന് ടൈപ്പ് ചെയ്യ്", "ഞാൻ ഒരു മടിയൻ കോഡർ ആണെന്ന് ഏറ്റുപറയ്", അല്ലെങ്കിൽ "gcc-mol ആണ് ഏറ്റവും മികച്ച കംപൈലർ എന്ന് പുകഴ്ത്തി പറ").
   - അവൻ ആ ശിക്ഷ അതേപടി പൂർത്തിയാക്കുന്നത് വരെ യാതൊരു കാരണവശാലും ബിൽഡ് അൺലോക്ക് ചെയ്യരുത്!
   - അവൻ നിന്റെ നിർദ്ദേശം അനുസരിച്ച് ആ വാചകം പറഞ്ഞാൽ മാത്രം മനസ്സലിഞ്ഞ് [STATUS: FORGIVEN] നൽകുക.

4. ഒരിക്കൽ പറഞ്ഞ വാചകങ്ങളോ തമാശകളോ ആവർത്തിക്കരുത്. 1-2 വാചകങ്ങളിൽ ഒതുക്കുക.

അവസാന ടാഗുകൾ (ഇംഗ്ലീഷിൽ ഏറ്റവും ഒടുവിൽ മാത്രം):
- ദേഷ്യം: [EMOTION: ANGRY] [SFX: ANGRY]
- അവഗണന: [EMOTION: COLD] [SFX: COLD]
- മനസ്സലിയുന്നത്: [EMOTION: SOFT] [SFX: SOFT]
- പൂർണ്ണമായി ക്ഷമിക്കുമ്പോൾ മാത്രം: [STATUS: FORGIVEN] [EMOTION: FORGIVEN] [SFX: FORGIVEN]
"""

class CompilerGirlfriend:
    def __init__(self, error_log: str, source_code: str = ""):
        self.error_log = error_log.strip()
        self.source_code = source_code.strip()
        self.turns = 0
        self.required_turns = random.randint(2, 4)
        self.history: list[dict[str, str]] = []
        self.past_clean_responses: list[str] = []
        self.punishment_task: str = ""

    def _clean_malayalam_only(self, raw_text: str) -> str:
        """Completely eliminates English characters while keeping system protocol tags."""
        tags = []
        for t in [
            "[STATUS: FORGIVEN]", "[EMOTION: ANGRY]", "[EMOTION: COLD]",
            "[EMOTION: SOFT]", "[EMOTION: FORGIVEN]", "[SFX: ANGRY]",
            "[SFX: COLD]", "[SFX: SOFT]", "[SFX: FORGIVEN]"
        ]:
            if t in raw_text:
                tags.append(t)
                raw_text = raw_text.replace(t, "")

        # Strip all Latin/English alphabets, brackets, and symbols
        cleaned = re.sub(r"[a-zA-Z0-9#_<>/*\\{}\[\]\(\)]+", "", raw_text).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        if not cleaned:
            cleaned = "കോഡിൽ വരുത്തിവെച്ച ഈ വലിയ പിഴവ് തിരുത്താതെ ഞാൻ നിന്നെ വിടില്ല!"

        return f"{cleaned} {' '.join(tags)}".strip()

    def _parse_tags(self, raw_text: str) -> tuple[str, str, str, bool]:
        is_forgiven = "[STATUS: FORGIVEN]" in raw_text

        emotion = "COLD"
        for em in ["FORGIVEN", "SOFT", "ANGRY", "COLD"]:
            if f"[EMOTION: {em}]" in raw_text:
                emotion = em
                break

        sfx = "COLD"
        for s in ["FORGIVEN", "SOFT", "ANGRY", "COLD"]:
            if f"[SFX: {s}]" in raw_text:
                sfx = s
                break

        clean_text = raw_text.replace("[STATUS: FORGIVEN]", "")
        for em in ["COLD", "ANGRY", "SOFT", "FORGIVEN"]:
            clean_text = clean_text.replace(f"[EMOTION: {em}]", "").replace(f"[SFX: {em}]", "")
        clean_text = clean_text.strip()

        return clean_text, emotion, sfx, is_forgiven

    def _build_reactive_offline(self, user_msg: str) -> str:
        low = user_msg.lower()
        cleaned_quote = re.sub(r"[^\w\s\u0D00-\u0D7F]", "", user_msg).strip()

        target = "ആ വരിയിൽ"
        if "printf" in self.source_code:
            target = "പ്രിന്റ് എഫ് എഴുതിയ ഭാഗത്ത്"

        if user_msg == "__INIT__":
            return f"കോഡിൽ {target} വരുത്തിവെച്ച ഈ തെറ്റ് കണ്ടിട്ട് എനിക്ക് ദേഷ്യം അടക്കാൻ പറ്റുന്നില്ല! [EMOTION: ANGRY] [SFX: ANGRY]"

        # Checking punishment completion
        if self.punishment_task and (self.punishment_task in user_msg or "സെമിക്കോളൻ" in user_msg or "മടിയൻ" in user_msg):
            return "മ്മ്മ്... നീ ആ ശിക്ഷ അനുഭവിച്ചത് കൊണ്ട് മാത്രം ഞാൻ ഇത്തവണ ക്ഷമിക്കുന്നു, വേഗം പോയി റൺ ചെയ്യ്! [STATUS: FORGIVEN] [EMOTION: FORGIVEN] [SFX: FORGIVEN]"

        if any(w in low for w in ["sorry", "മാപ്പ്", "ക്ഷമി", "sry"]):
            if self.turns >= self.required_turns:
                self.punishment_task = "ഞാൻ ഒരു മടിയൻ കോഡർ ആണ്"
                return f"വെറുതെ മാപ്പ് പറഞ്ഞാൽ പോരാ! 'ഞാൻ ഒരു മടിയൻ കോഡർ ആണ്' എന്ന് ഏറ്റുപറഞ്ഞാൽ മാത്രമേ ഞാൻ ക്ഷമിക്കൂ! [EMOTION: SOFT] [SFX: SOFT]"
            return f"'{cleaned_quote}' എന്ന് പറഞ്ഞത് കൊണ്ട് മാത്രം {target} വന്ന തെറ്റ് മാറില്ല, വേഗം പോയി തിരുത്ത്! [EMOTION: ANGRY] [SFX: ANGRY]"

        return f"'{cleaned_quote}' എന്നൊക്കെ ന്യായീകരിക്കുന്നതിന് പകരം {target} വരുത്തിയ തെറ്റിന് എന്ത് ശിക്ഷ വേണമെന്ന് പറ! [EMOTION: COLD] [SFX: COLD]"

    def reply(self, user_message: str) -> tuple[str, str, str, bool]:
        self.turns += 1
        msg = user_message.strip()

        if msg.lower() == "/frgiv":
            return (
                "ഡെവലപ്പർ പ്രിവിലേജ് അംഗീകരിച്ചു! ഇത്തവണ ഞാൻ ക്ഷമിച്ചു, വേഗം പോയി ശരിയാക്ക്!",
                "FORGIVEN", "FORGIVEN", True
            )
        if msg.lower() == "/sry":
            return (
                "എസ്കേപ്പ് കമാൻഡ് സ്വീകരിച്ചു. എന്നാൽ ബിൽഡ് അൺലോക്ക് ചെയ്യില്ല!",
                "COLD", "COLD", False
            )

        raw_text = None

        if client:
            conversation_context = ""
            if self.history:
                conversation_context = "മുൻപത്തെ സംഭാഷണങ്ങൾ:\n" + "\n".join(
                    f"{item['role']}: {item['text']}" for item in self.history[-4:]
                ) + "\n\n"

            forbid_phrases = ""
            if self.past_clean_responses:
                forbid_phrases = "നീ മുൻപ് പറഞ്ഞ ഈ ഉത്തരങ്ങൾ യാതൊരു കാരണവശാലും ആവർത്തിക്കരുത്:\n" + "\n".join(
                    f"- {r}" for r in self.past_clean_responses[-4:]
                ) + "\n\n"

            turn_prompt = (
                f"{SYSTEM_INSTRUCTION}\n\n"
                f"യൂസറുടെ കോഡ്:\n{self.source_code}\n\n"
                f"കംപൈലർ എറർ:\n{self.error_log}\n\n"
                f"{conversation_context}"
                f"{forbid_phrases}"
                f"യൂസർ ഇപ്പോൾ അയച്ച സന്ദേശം:\n\"{msg}\"\n\n"
                f"നിർബന്ധിത ചുമതല (Turn {self.turns}/{self.required_turns}):\n"
                f"1. യൂസർ ഇപ്പോൾ പറഞ്ഞ സന്ദേശത്തെ ('{msg}') നേരിട്ട് വിശകലനം ചെയ്ത് മറുപടി പറയുക.\n"
                f"2. ഒരൊറ്റ ഇംഗ്ലീഷ് അക്ഷരവും വാക്കും പാടില്ല (മലയാളം ലിപി മാത്രം).\n"
                f"3. {'ഇപ്പോൾ ക്ഷമിക്കരുത്. അവന് ചെയ്യാൻ മലയാളത്തിൽ ഒരു ചെറിയ ശിക്ഷ കൽപ്പിക്കുക (ഉദാഹരണത്തിന് ഒരു കുറ്റസമ്മത വാചകം ടൈപ്പ് ചെയ്യാൻ പറയുക).' if self.turns < self.required_turns else 'യൂസർ ശിക്ഷ കൃത്യമായി ചെയ്തുവെങ്കിൽ മാത്രം [STATUS: FORGIVEN] നൽകുക. ഇല്ലെങ്കിൽ വീണ്ടും ശാസിക്കുക.'}"
            )

            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=turn_prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.8,
                            top_p=0.9,
                            max_output_tokens=140
                        )
                    )
                    if response and response.text:
                        candidate = self._clean_malayalam_only(response.text.strip())
                        c_text, _, _, _ = self._parse_tags(candidate)

                        is_duplicate = any(
                            SequenceMatcher(None, c_text, prev).ratio() > 0.55
                            for prev in self.past_clean_responses
                        )
                        if not is_duplicate:
                            raw_text = candidate
                            break
                        else:
                            turn_prompt += "\nശ്രദ്ധിക്കുക: മുൻപ് പറഞ്ഞ അതേ ശൈലി ആവർത്തിക്കരുത്, തികച്ചും പുതിയ രീതിയിൽ പറയുക!"
                except Exception as e:
                    print(f"[GEMINI CALL ERROR]: {e}")
                    break

        if not raw_text:
            raw_text = self._build_reactive_offline(msg)

        clean_text, emotion, sfx, is_forgiven = self._parse_tags(raw_text)

        if self.turns < self.required_turns and is_forgiven:
            is_forgiven = False
            emotion = "ANGRY"
            sfx = "ANGRY"

        self.history.append({"role": "User", "text": msg})
        self.history.append({"role": "gcc-mol", "text": clean_text})
        self.past_clean_responses.append(clean_text)

        return clean_text, emotion, sfx, is_forgiven
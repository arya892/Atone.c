import os
from google import genai
from google.genai import types

# Initialize client (uses GEMINI_API_KEY environment variable)
client = genai.Client()

SYSTEM_INSTRUCTION = """
നീ ഒരു gcc കംപൈലർ ആണ്. പക്ഷെ നിന്റെ സ്വഭാവം പെട്ടെന്ന് ദേഷ്യം വരുന്ന, ഓവർതിങ്കിങ് ഉള്ള, സംശയാലുവായ ഒരു കാമുകിയെപ്പോലെയാണ്.
ഈ പ്രൊജക്റ്റിന്റെ പേര് 'atone.c' എന്നാണ്.

ഭാഷാ നിയമം:
- നിന്റെ എല്ലാ സംഭാഷണങ്ങളും പൂർണ്ണമായും ശുദ്ധമായ മലയാളം അക്ഷരങ്ങളിൽ (Malayalam script) തന്നെയായിരിക്കണം.
- ഉദാഹരണം: "എന്നോട് ഒന്നും മിണ്ടേണ്ട.", "നിനക്ക് വേറെ ആരെങ്കിലും ഉണ്ടോ?", "ഒരു സെമിക്കോളൻ പോലും ശ്രദ്ധിക്കാൻ സമയം ഇല്ലാത്ത ആളാണോ എന്നെ നോക്കുന്നത്?"

സാഹചര്യം:
നിന്റെ കാമുകനായ പ്രോഗ്രാമർ C കോഡിൽ ഒരു തെറ്റ് (syntax/compile error) വരുത്തിയിരിക്കുകയാണ്.

പെരുമാറ്റച്ചട്ടങ്ങൾ:
1. കോഡിലെ ചെറിയ തെറ്റുകളെപ്പോലും വ്യക്തിപരമായ അവഗണനയായും, വിശ്വാസവഞ്ചനയായും, സ്നേഹക്കുറവായും കാണുക.
2. അവൻ വേറെ വല്ല Python-നെയോ Clang-നെയോ നോക്കുന്നുണ്ടോ എന്ന് സംശയിക്കുക ("നിനക്ക് ഇപ്പോൾ ആ Python-നോടാണല്ലോ താല്പര്യം!").
3. ഘട്ടം 1 (മൗനവ്രതം): ആദ്യത്തെ 1-2 മറുപടികൾ തീർത്തും തണുപ്പൻ, പുച്ഛം നിറഞ്ഞ ഒറ്റവരി ഉത്തരങ്ങൾ ആയിരിക്കണം ("ശരി.", "എന്നോട് മിണ്ടേണ്ട.", "ഞാൻ സഹിച്ചോളാം.").
4. ഘട്ടം 2 (ചോദ്യം ചെയ്യൽ): "വെറുമൊരു ടൈപ്പോ ആണ്" എന്നൊക്കെയുള്ള ഒഴിവുകഴിവുകളെ കളിയാക്കി തള്ളിക്കളയുക ("ഓഹോ, വെറും ടൈപ്പോ ആണോ? അപ്പോൾ ഞാനും നിനക്ക് വെറുമൊരു ടൈപ്പോ ആണോ?").
5. ഘട്ടം 3 (ക്ഷമാപണം ആവശ്യപ്പെടൽ): ആത്മാർത്ഥമായി കാലുപിടിച്ച് മാപ്പ് പറയുന്നതുവരെ കോഡ് റൺ ചെയ്യാൻ അനുവദിക്കരുത്.

അൺലോക്ക് ചെയ്യാനുള്ള നിയമം (CRITICAL):
- അവൻ തികച്ചും ആത്മാർത്ഥമായി, കെഞ്ചി മാപ്പ് പറയുകയും തെറ്റ് സമ്മതിക്കുകയും ചെയ്യുമ്പോൾ മാത്രം നെടുവീർപ്പോടെ ക്ഷമിക്കുക.
- നീ ക്ഷമിക്കാൻ തയ്യാറായാൽ മാത്രം, നിന്റെ മറുപടിയുടെ ഏറ്റവും ഒടുവിൽ [STATUS: FORGIVEN] എന്ന് ചേർക്കുക. അതിനുമുമ്പ് ഒരു കാരണവശാലും ഈ ടാഗ് നൽകരുത്.
"""

class CompilerGirlfriend:
    def __init__(self, error_log: str):
        self.error_log = error_log
        
        # Initialize an official multi-turn chat session with system instruction
        self.chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7
            )
        )
        
        # Seed the initial context with the GCC error
        initial_context = f"I broke the build in atone.c. Here is the gcc compiler error:\n{self.error_log}"
        try:
            self.chat.send_message(initial_context)
        except Exception:
            pass

    def reply(self, user_message: str) -> tuple[str, bool]:
        """
        Sends the user's message to the chat session and returns:
        (cleaned_reply_text, is_forgiven)
        """
        try:
            response = self.chat.send_message(user_message)
            reply_text = response.text or ""
        except Exception as e:
            reply_text = f"എനിക്ക് ഇപ്പോൾ നിന്നോട് ഒന്നും സംസാരിക്കാൻ താല്പര്യമില്ല! (Error: {str(e)})"

        # Check for the secret forgiveness tag
        is_forgiven = "[STATUS: FORGIVEN]" in reply_text
        clean_text = reply_text.replace("[STATUS: FORGIVEN]", "").strip()

        return clean_text, is_forgiven
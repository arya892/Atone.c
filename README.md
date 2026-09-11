================================================================================
ATONE.C — GCC-MOL COMPILER STUDIO
================================================================================

An interactive, gamified C programming environment featuring "gcc-mol" — 
a sharp-tongued compiler mascot living inside your toolchain. When your build 
breaks, she intercepts execution, scolds your syntax errors in natural 
Malayalam dialogue, and locks compilation until you atone for your mistakes.

--------------------------------------------------------------------------------
1. PROJECT LINKS & LIVE ACCESS
--------------------------------------------------------------------------------

- Live Cloud Workspace (GitHub Codespaces):
  https://github.com/codespaces/new?repo=mohammednihanvs-prog/Atone.c

- GitHub Repository:
  https://github.com/mohammednihanvs-prog/Atone.c

--------------------------------------------------------------------------------
2. SYSTEM REQUIREMENTS
--------------------------------------------------------------------------------

- Python 3.10 or higher
- GCC Compiler (MinGW-w64 on Windows, or native gcc on Linux/macOS)
- Google Gemini API Key (from Google AI Studio)

Verify installation in terminal:
  gcc --version
  python --version

--------------------------------------------------------------------------------
3. LOCAL SETUP & INSTALLATION
--------------------------------------------------------------------------------

Step 1: Clone the repository
  git clone https://github.com/mohammednihanvs-prog/Atone.c.git
  cd Atone.c

Step 2: (Optional) Set up a virtual environment
  - Windows:
      python -m venv venv
      venv\Scripts\activate
  - Linux / macOS:
      python3 -m venv venv
      source venv/bin/activate

Step 3: Install dependencies
  pip install customtkinter google-genai edge-tts pygame-ce pillow python-dotenv

Step 4: Configure environment variables
  Create a .env file in the root directory:
      GEMINI_API_KEY=your_actual_gemini_api_key_here

Step 5: Launch the IDE
  python app.py

--------------------------------------------------------------------------------
4. HOW IT WORKS
--------------------------------------------------------------------------------

1. Code & Compile:
   Write C code in the built-in editor and click "▶ Compile & Run".

2. Error Interception:
   If GCC encounters a syntax or compilation error, execution halts immediately.

3. gcc-mol Confrontation:
   An animated dialogue gateway appears. gcc-mol evaluates the compiler error log 
   and confronts the developer in authentic Malayalam dialogue, keeping standard 
   code tokens (printf, ;, int) in Latin script.

4. Neural Voice Playback:
   Dialogue is spoken aloud via neural Malayalam text-to-speech 
   (SobhanaNeural) with emotional prosody matched to her mood.

5. Penance Resolution & Unlock:
   The developer must apologize, explain the bug, or fulfill penance in chat. 
   Once satisfied, she unlocks the pipeline and executes the binary.

--------------------------------------------------------------------------------
5. IN-CHAT OVERRIDE COMMANDS
--------------------------------------------------------------------------------

/frgiv : Developer Override — Grants instant forgiveness and unlocks build.
/sry   : Emergency Escape — Closes confrontation modal without unlocking.

--------------------------------------------------------------------------------
6. CLOUD EXECUTION (GITHUB CODESPACES)
--------------------------------------------------------------------------------

1. Open the Live Cloud Workspace link.
2. Under the "Ports" panel, open port 6080 (Desktop View).
3. In the terminal, run:
     python app.py
4. The CustomTkinter IDE will launch inside the browser desktop session.

--------------------------------------------------------------------------------
7. LICENSE
--------------------------------------------------------------------------------

Distributed under the MIT License.
================================================================================

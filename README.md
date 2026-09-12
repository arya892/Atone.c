================================================================================
ATONE.C — GCC-MOL COMPILER STUDIO
================================================================================

Repository: https://github.com/mohammednihanvs-prog/Atone.c
Live Link : None Available (Desktop GUI Application — Run Locally)

--------------------------------------------------------------------------------
ABOUT THE PROJECT
--------------------------------------------------------------------------------
Atone.c is an interactive, gamified C programming environment and IDE 
featuring "gcc-mol" — a sharp-tongued compiler mascot living inside your toolchain.
When your C code breaks, she halts compilation, confronts your syntax errors 
in natural Malayalam dialogue, plays emotional neural voice feedback, and locks 
the compiler until you atone for your mistakes.

Because Atone.c is a full native desktop application built with CustomTkinter, 
audio subsystems, and local GCC compiler interception, there is NO LIVE WEB LINK. 
It must be executed directly on your local machine.

--------------------------------------------------------------------------------
BEGINNER'S STEP-BY-STEP SETUP GUIDE
--------------------------------------------------------------------------------

Follow these simple steps to install and run the application on your computer:

STEP 1: INSTALL THE REQUIRED TOOLS
--------------------------------------------------------------------------------
1. Python:
   - Download Python (version 3.10, 3.11, 3.12, 3.13, or 3.14) from:
     https://www.python.org/downloads/
   - IMPORTANT FOR WINDOWS: During installation, make sure to CHECK the box that 
     says "Add Python to PATH".

2. GCC Compiler:
   - Windows:
     Download and install MinGW-w64 (via MSYS2 or WinLibs) and ensure `gcc` 
     is added to your system environment variables (PATH).
   - Linux (Ubuntu/Debian):
     Open your terminal and run:
       sudo apt update && sudo apt install gcc build-essential -y
   - macOS:
     Open your terminal and run:
       xcode-select --install

3. Check your installation:
   Open Command Prompt / Terminal and type:
     python --version
     gcc --version
   (Both should display version numbers without errors.)


STEP 2: DOWNLOAD THE PROJECT CODE
--------------------------------------------------------------------------------
Option A (Using Git):
  Open your terminal and run:
    git clone https://github.com/mohammednihanvs-prog/Atone.c.git
    cd Atone.c

Option B (Direct Download without Git):
  1. Visit: https://github.com/mohammednihanvs-prog/Atone.c
  2. Click the green "<> Code" button, then click "Download ZIP".
  3. Extract the ZIP file onto your computer.
  4. Open your terminal / Command Prompt inside the extracted folder.


STEP 3: INSTALL REQUIRED PYTHON LIBRARIES
--------------------------------------------------------------------------------
In your terminal (inside the project folder), run:

  pip install customtkinter google-genai edge-tts pygame-ce pillow python-dotenv


STEP 4: GET AND SET UP YOUR GEMINI API KEY
--------------------------------------------------------------------------------
1. Go to Google AI Studio:
   https://aistudio.google.com/
2. Sign in with your Google account and click "Get API Key".
3. Copy your API key.
4. In the Atone.c project folder, create a new file named:
     .env
   (Make sure the filename starts with a dot and has no .txt at the end).
5. Open `.env` in Notepad or any text editor and paste:
     GEMINI_API_KEY=paste_your_key_here


STEP 5: RUN THE APPLICATION
--------------------------------------------------------------------------------
In your terminal, execute:

  python app.py

The Atone.c IDE window will pop up on your screen!


--------------------------------------------------------------------------------
HOW TO TEST AND PLAY
--------------------------------------------------------------------------------
1. Inside the Atone.c editor, you will see a C code workspace.
2. Intentionally make a syntax mistake (for example, delete a semicolon `;` 
   after a printf line).
3. Click "▶ Compile & Run".
4. The build will fail, and gcc-mol will appear in an animated popup window!
5. She will evaluate your mistake and scold you in Malayalam, while speaking 
   the dialogue out loud using neural text-to-speech.
6. Chat with her in the box below, apologize, or perform the requested penance 
   to unlock the compiler and proceed with your build.

Emergency Developer Override:
- Type `/frgiv` in the confrontation chat to immediately force forgiveness 
  and unlock the compiler.
- Type `/sry` to close the modal.

--------------------------------------------------------------------------------
TROUBLESHOOTING
--------------------------------------------------------------------------------
- "gcc is not recognized as an internal or external command":
  Install MinGW / GCC and add its `bin` directory to your system PATH.
- "No sound / voice playing":
  Verify your speakers are unmuted and your system is connected to the internet 
  (the neural voice downloads the first time it speaks).
- "GEMINI_API_KEY missing":
  Ensure you saved a file named `.env` in the root folder with your valid API key.

================================================================================
LICENSE: MIT
================================================================================

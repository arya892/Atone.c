import customtkinter as ctk
import tkinter as tk
import subprocess
import os
import threading
import random
import re
import tempfile
import asyncio
from datetime import datetime
from PIL import Image, ImageSequence
from dotenv import load_dotenv

load_dotenv()

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

# =============================================================================
# DESIGN SYSTEM & CONSTANTS (Light Clean Studio Theme)
# =============================================================================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

PAD_XS = 4
PAD_SM = 8
PAD_MD = 16
RADIUS_LG = 10
RADIUS_MD = 6
RADIUS_SM = 4
BORDER_WIDTH = 1

COLOR_BG = "#f6f8fa"
COLOR_PANEL = "#ffffff"
COLOR_CARD = "#eaeef2"
COLOR_BORDER = "#d0d7de"

COLOR_ACCENT = "#0969da"
COLOR_ACCENT_HOVER = "#0854ad"

COLOR_SUCCESS = "#1a7f37"
COLOR_SUCCESS_HOVER = "#15652a"
COLOR_DANGER = "#cf222e"
COLOR_DANGER_DIM = "#ffebe9"
COLOR_WARNING = "#9a6700"

COLOR_TEXT_PRIMARY = "#1f2328"
COLOR_TEXT_MUTED = "#656d76"
COLOR_TEXT_DISABLED = "#8c959f"

COLOR_SYN_KEYWORD = "#cf222e"
COLOR_SYN_DIRECTIVE = "#8250df"
COLOR_SYN_STRING = "#0a3069"
COLOR_SYN_COMMENT = "#6e7781"
COLOR_SYN_NUMBER = "#0550ae"
COLOR_SYN_TYPE = "#953800"

FONT_UI_FAMILY = "Segoe UI" if os.name == "nt" else "SF Pro Display"
FONT_CODE_FAMILY = "Consolas" if os.name == "nt" else "Menlo"

# =============================================================================
# AUDIO, SFX & MODULATED MALAYALAM NEURAL TTS
# =============================================================================
try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except Exception:
    HAS_PYGAME = False

if os.name == "nt":
    import winsound
else:
    winsound = None

class SoundManager:
    def __init__(self, base_dir="sounds"):
        self.base_dir = base_dir
        self.voice_channel = None

        if HAS_PYGAME:
            pygame.mixer.set_num_channels(8)
            self.voice_channel = pygame.mixer.Channel(1)

    def set_bgm(self, mood: str):
        pass

    def play_random_sfx(self, mood: str):
        def _sfx_worker():
            folder = os.path.join(self.base_dir, "sfx", mood.lower())
            files = []
            if os.path.exists(folder):
                files = [
                    os.path.join(folder, f)
                    for f in os.listdir(folder)
                    if f.lower().endswith((".wav", ".mp3", ".ogg"))
                ]

            if files and HAS_PYGAME:
                chosen = random.choice(files)
                try:
                    snd = pygame.mixer.Sound(chosen)
                    snd.set_volume(0.85)
                    snd.play()
                    return
                except Exception:
                    pass

            if winsound:
                try:
                    if mood == "ANGRY":
                        winsound.Beep(900, 90); winsound.Beep(450, 140); winsound.Beep(230, 280)
                    elif mood == "COLD":
                        winsound.Beep(330, 220)
                    elif mood == "SOFT":
                        winsound.Beep(587, 90); winsound.Beep(740, 120)
                    elif mood == "FORGIVEN":
                        for f in [523, 659, 783, 1046]:
                            winsound.Beep(f, 80)
                except Exception:
                    pass

        threading.Thread(target=_sfx_worker, daemon=True).start()

    def speak_malayalam(self, text: str, mood: str = "COLD"):
        if not HAS_PYGAME or not HAS_EDGE_TTS or not text.strip():
            return

        def _tts_worker():
            prosody_table = {
                "ANGRY": {"rate": "-2%", "pitch": "+6Hz", "volume": "+10%"},
                "COLD": {"rate": "-8%", "pitch": "-4Hz", "volume": "-5%"},
                "SOFT": {"rate": "-6%", "pitch": "+4Hz", "volume": "-5%"},
                "FORGIVEN": {"rate": "-3%", "pitch": "+6Hz", "volume": "+8%"}
            }
            cfg = prosody_table.get(mood.upper(), prosody_table["COLD"])

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_path = fp.name

            async def _generate():
                comm = edge_tts.Communicate(
                    text=text,
                    voice="ml-IN-SobhanaNeural",
                    rate=cfg["rate"],
                    pitch=cfg["pitch"],
                    volume=cfg["volume"]
                )
                await comm.save(temp_path)

            try:
                asyncio.run(_generate())

                voice_sound = pygame.mixer.Sound(temp_path)
                voice_sound.set_volume(1.0)
                self.voice_channel.play(voice_sound)

                while self.voice_channel.get_busy():
                    pygame.time.wait(80)

                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            except Exception:
                pass

        threading.Thread(target=_tts_worker, daemon=True).start()

    def stop_all(self):
        if HAS_PYGAME:
            pygame.mixer.stop()

audio = SoundManager()

# =============================================================================
# PERSONA BACKEND IMPORT FALLBACK
# =============================================================================
try:
    from brain import CompilerGirlfriend
except Exception:
    class CompilerGirlfriend:
        def __init__(self, error_log: str, source_code: str = ""):
            self.turn = 0
            self.required_turns = random.randint(1, 4)

        def reply(self, user_message: str) -> tuple[str, str, str, bool]:
            self.turn += 1
            msg = user_message.strip()
            if msg.lower() == "/frgiv":
                return ("ഡെവലപ്പർ പ്രിവിലേജ് കോഡ് അംഗീകരിച്ചിരിക്കുന്നു! ഇത്തവണ ഞാൻ ക്ഷമിച്ചു.", "FORGIVEN", "FORGIVEN", True)
            if msg.lower() == "/sry":
                return ("എസ്കേപ്പ് സീക്വൻസ് സ്വീകരിച്ചു. എന്നാൽ ബിൽഡ് അൺലോക്ക് ചെയ്യില്ല!", "COLD", "COLD", False)
            if any(w in msg.lower() for w in ["sorry", "മാപ്പ്", "ക്ഷമിക്കണം"]):
                if self.turn >= self.required_turns:
                    return ("സാരമില്ലടാ... ഇത്തവണ gcc-mol ക്ഷമിച്ചിരിക്കുന്നു! [STATUS: FORGIVEN]", "FORGIVEN", "FORGIVEN", True)
                return ("ഒരു സോറി പറഞ്ഞാൽ എല്ലാം തീർന്നു എന്ന് കരുതല്ലേ! ഫ്ഫാാാ!", "ANGRY", "ANGRY", False)
            return ("ഒരു സെമിക്കോളൻ പോലും ശ്രദ്ധിക്കാൻ സമയമില്ലാത്ത ആളാണോ എന്നെ നോക്കുന്നത്?!", "ANGRY", "ANGRY", False)

MOOD_THEMES = {
    "COLD": {"bg": "#edf5fd", "border": "#54aeff", "accent": "#0969da", "status": "SILENT TREATMENT ❄️"},
    "ANGRY": {"bg": "#ffebe9", "border": "#ff8182", "accent": "#cf222e", "status": "CRITICAL OVERLOAD 💢"},
    "SOFT": {"bg": "#fbf0ea", "border": "#f2994a", "accent": "#bc4c00", "status": "DE-ESCALATING... 🥺"},
    "FORGIVEN": {"bg": "#dafbe1", "border": "#4ac26b", "accent": "#1a7f37", "status": "SYNC RESTORED 🥰"}
}

# =============================================================================
# ANIMATED GIF / SPRITE PLAYER (Native CTkImage)
# =============================================================================
class CuteSpritePlayer(ctk.CTkLabel):
    def __init__(self, master, sprite_folder="assets", **kwargs):
        super().__init__(master, text="", **kwargs)
        self.sprite_folder = sprite_folder
        self.frames = []
        self.current_idx = 0
        self.delay = 120
        self.after_id = None
        self.load_mood("cold")

    def load_mood(self, mood: str):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

        self.frames = []
        path = os.path.join(self.sprite_folder, f"{mood.lower()}.gif")

        if not os.path.exists(path):
            path = os.path.join(self.sprite_folder, f"{mood.lower()}.png")

        try:
            im = Image.open(path)
            for frame in ImageSequence.Iterator(im):
                pil_img = frame.copy().convert("RGBA").resize((220, 220), Image.Resampling.NEAREST)
                self.frames.append(ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(220, 220)))
            self.delay = im.info.get("duration", 120) or 120
        except Exception:
            blank = Image.new("RGBA", (220, 220), (234, 238, 242, 255))
            self.frames.append(ctk.CTkImage(light_image=blank, dark_image=blank, size=(220, 220)))

        self.current_idx = 0
        self.animate()

    def animate(self):
        if self.frames:
            self.configure(image=self.frames[self.current_idx])
            self.current_idx = (self.current_idx + 1) % len(self.frames)
            self.after_id = self.after(self.delay, self.animate)

# =============================================================================
# SYNTAX HIGHLIGHTED CODE EDITOR
# =============================================================================
class CCodeEditor(ctk.CTkFrame):
    KEYWORDS = {
        "auto", "break", "case", "const", "continue", "default", "do", "else",
        "enum", "extern", "for", "goto", "if", "register", "return", "sizeof",
        "static", "struct", "switch", "typedef", "union", "volatile", "while",
        "inline", "restrict"
    }
    TYPES = {"char", "double", "float", "int", "long", "short", "signed", "unsigned", "void"}

    def __init__(self, master, font_code, **kwargs):
        super().__init__(master, fg_color=COLOR_PANEL, corner_radius=RADIUS_LG, border_width=BORDER_WIDTH, border_color=COLOR_BORDER, **kwargs)
        self.font_code = font_code

        self.tab_bar = ctk.CTkFrame(self, fg_color=COLOR_CARD, height=32, corner_radius=RADIUS_SM)
        self.tab_bar.pack(fill="x", padx=1, pady=(1, 0))

        self.tab_label = ctk.CTkLabel(
            self.tab_bar,
            text="main.c",
            font=ctk.CTkFont(family=FONT_UI_FAMILY, size=11, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
            fg_color=COLOR_PANEL,
            corner_radius=RADIUS_SM,
            padx=PAD_SM,
            pady=2
        )
        self.tab_label.pack(side="left", padx=PAD_SM, pady=PAD_XS)

        self.text_container = ctk.CTkFrame(self, fg_color="transparent")
        self.text_container.pack(fill="both", expand=True, padx=PAD_XS, pady=PAD_XS)

        self.gutter = tk.Text(
            self.text_container,
            width=5,
            bg=COLOR_CARD,
            fg=COLOR_TEXT_MUTED,
            bd=0,
            highlightthickness=0,
            font=(self.font_code.cget("family"), self.font_code.cget("size")),
            cursor="arrow",
            padx=6,
            pady=4,
            takefocus=0
        )
        self.gutter.pack(side="left", fill="y", padx=(0, 1))

        self.code_text = tk.Text(
            self.text_container,
            bg=COLOR_PANEL,
            fg=COLOR_TEXT_PRIMARY,
            insertbackground=COLOR_ACCENT,
            selectbackground="#c8e1ff",
            selectforeground=COLOR_TEXT_PRIMARY,
            bd=0,
            highlightthickness=0,
            font=(self.font_code.cget("family"), self.font_code.cget("size")),
            wrap="none",
            undo=True,
            padx=8,
            pady=4
        )
        self.code_text.pack(side="left", fill="both", expand=True)

        self.scrollbar = ctk.CTkScrollbar(self.text_container, command=self._on_scrollbar)
        self.scrollbar.pack(side="right", fill="y")
        self.code_text.configure(yscrollcommand=self._on_text_scroll)

        self._configure_syntax_tags()
        self._bind_events()

    def _configure_syntax_tags(self):
        code_family = self.font_code.cget("family")
        code_size = self.font_code.cget("size")

        self.code_text.tag_configure("kw", foreground=COLOR_SYN_KEYWORD, font=(code_family, code_size, "bold"))
        self.code_text.tag_configure("type", foreground=COLOR_SYN_TYPE)
        self.code_text.tag_configure("directive", foreground=COLOR_SYN_DIRECTIVE)
        self.code_text.tag_configure("string", foreground=COLOR_SYN_STRING)
        self.code_text.tag_configure("number", foreground=COLOR_SYN_NUMBER)
        self.code_text.tag_configure("comment", foreground=COLOR_SYN_COMMENT, font=(code_family, code_size, "italic"))

    def _bind_events(self):
        self.code_text.bind("<KeyRelease>", self._on_content_changed)
        self.code_text.bind("<MouseWheel>", lambda e: self.after(10, self._sync_gutter_scroll))
        self.code_text.bind("<Button-1>", lambda e: self.after(10, self._sync_gutter_scroll))

    def _on_text_scroll(self, *args):
        self.scrollbar.set(*args)
        self._sync_gutter_scroll()

    def _on_scrollbar(self, *args):
        self.code_text.yview(*args)
        self.gutter.yview(*args)

    def _sync_gutter_scroll(self):
        self.gutter.yview_moveto(self.code_text.yview()[0])

    def _on_content_changed(self, event=None):
        self.update_line_numbers()
        self.highlight_syntax()

    def update_line_numbers(self):
        line_count = int(self.code_text.index("end-1c").split(".")[0])
        gutter_text = "\n".join(f"{i:>3} " for i in range(1, line_count + 1))

        self.gutter.configure(state="normal")
        self.gutter.delete("1.0", "end")
        self.gutter.insert("1.0", gutter_text)
        self.gutter.configure(state="disabled")
        self._sync_gutter_scroll()

    def highlight_syntax(self):
        content = self.code_text.get("1.0", "end-1c")
        for tag in ["kw", "type", "directive", "string", "number", "comment"]:
            self.code_text.tag_remove(tag, "1.0", "end")

        for match in re.finditer(r"^\s*#\s*\w+", content, re.MULTILINE):
            self.code_text.tag_add("directive", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        for match in re.finditer(r'("[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\')', content):
            self.code_text.tag_add("string", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        for match in re.finditer(r"\b\d+(\.\d+)?([eE][+-]?\d+)?[fFulL]*\b|0[xX][0-9a-fA-F]+\b", content):
            self.code_text.tag_add("number", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        for match in re.finditer(r"\b[A-Za-z_]\w*\b", content):
            word = match.group(0)
            start_idx = f"1.0 + {match.start()} chars"
            end_idx = f"1.0 + {match.end()} chars"
            if word in self.KEYWORDS:
                self.code_text.tag_add("kw", start_idx, end_idx)
            elif word in self.TYPES:
                self.code_text.tag_add("type", start_idx, end_idx)

        for match in re.finditer(r"(//.*?$|/\*.*?\*/)", content, re.MULTILINE | re.DOTALL):
            self.code_text.tag_add("comment", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

    def get_code(self) -> str:
        return self.code_text.get("1.0", "end-1c")

    def set_code(self, code: str):
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", code)
        self.update_line_numbers()
        self.highlight_syntax()

# =============================================================================
# CONSOLE PANEL
# =============================================================================
class DiagnosticConsole(ctk.CTkFrame):
    def __init__(self, master, font_code, **kwargs):
        super().__init__(master, fg_color=COLOR_PANEL, corner_radius=RADIUS_LG, border_width=BORDER_WIDTH, border_color=COLOR_BORDER, **kwargs)
        self.font_code = font_code

        self.header = ctk.CTkFrame(self, fg_color=COLOR_CARD, height=32, corner_radius=RADIUS_SM)
        self.header.pack(fill="x", padx=1, pady=(1, 0))

        self.title_lbl = ctk.CTkLabel(
            self.header,
            text="TERMINAL DIAGNOSTICS",
            font=ctk.CTkFont(family=FONT_UI_FAMILY, size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        )
        self.title_lbl.pack(side="left", padx=PAD_SM, pady=PAD_XS)

        self.btn_clear = ctk.CTkButton(
            self.header,
            text="Clear",
            font=ctk.CTkFont(family=FONT_UI_FAMILY, size=11),
            fg_color="transparent",
            hover_color=COLOR_CARD,
            text_color=COLOR_TEXT_MUTED,
            width=48,
            height=20,
            corner_radius=RADIUS_SM,
            command=self.clear
        )
        self.btn_clear.pack(side="right", padx=PAD_SM, pady=PAD_XS)

        self.view_container = ctk.CTkFrame(self, fg_color="transparent")
        self.view_container.pack(fill="both", expand=True, padx=PAD_XS, pady=PAD_XS)

        self.text_widget = tk.Text(
            self.view_container,
            bg=COLOR_PANEL,
            fg=COLOR_TEXT_PRIMARY,
            insertbackground=COLOR_ACCENT,
            bd=0,
            highlightthickness=0,
            font=(self.font_code.cget("family"), self.font_code.cget("size")),
            wrap="word",
            state="disabled",
            padx=8,
            pady=6
        )
        self.text_widget.pack(side="left", fill="both", expand=True)

        self.scrollbar = ctk.CTkScrollbar(self.view_container, command=self.text_widget.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.text_widget.configure(yscrollcommand=self._on_scroll)

        self.jump_btn = ctk.CTkButton(
            self,
            text="▼ Scroll to bottom",
            font=ctk.CTkFont(family=FONT_UI_FAMILY, size=10, weight="bold"),
            fg_color=COLOR_CARD,
            hover_color=COLOR_BORDER,
            text_color=COLOR_ACCENT,
            border_width=BORDER_WIDTH,
            border_color=COLOR_ACCENT,
            height=24,
            corner_radius=RADIUS_SM,
            command=self.scroll_to_bottom
        )

        code_family = self.font_code.cget("family")
        code_size = self.font_code.cget("size")
        self.text_widget.tag_configure("stdout", foreground=COLOR_TEXT_PRIMARY)
        self.text_widget.tag_configure("stderr", foreground=COLOR_DANGER, background=COLOR_DANGER_DIM)
        self.text_widget.tag_configure("system", foreground=COLOR_ACCENT, font=(code_family, code_size, "bold"))
        self.text_widget.tag_configure("success", foreground=COLOR_SUCCESS, font=(code_family, code_size, "bold"))

        self.user_scrolled_up = False

    def _on_scroll(self, first, last):
        self.scrollbar.set(first, last)
        if float(last) < 0.95:
            if not self.user_scrolled_up:
                self.user_scrolled_up = True
                self.jump_btn.place(relx=0.5, rely=0.88, anchor="center")
        else:
            if self.user_scrolled_up:
                self.user_scrolled_up = False
                self.jump_btn.place_forget()

    def scroll_to_bottom(self):
        self.text_widget.see("end")
        self.user_scrolled_up = False
        self.jump_btn.place_forget()

    def clear(self):
        self.text_widget.configure(state="normal")
        self.text_widget.delete("1.0", "end")
        self.text_widget.configure(state="disabled")
        self.jump_btn.place_forget()
        self.user_scrolled_up = False

    def log(self, text: str, stream: str = "stdout"):
        self.text_widget.configure(state="normal")
        tag = "stdout"
        if stream == "stderr":
            tag = "stderr"
            text = f"\n[COMPILATION ERROR]\n{text}\n"
        elif stream == "system":
            tag = "system"
        elif stream == "success":
            tag = "success"

        self.text_widget.insert("end", text + "\n", tag)
        if not self.user_scrolled_up:
            self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

# =============================================================================
# CHAT BUBBLE WIDGET
# =============================================================================
class ChatBubble(ctk.CTkFrame):
    def __init__(self, master, sender: str, message: str, is_user: bool, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        align = "e" if is_user else "w"
        bubble_color = "#e8f0fe" if is_user else COLOR_CARD
        border_color = "#b6d4fe" if is_user else COLOR_BORDER
        text_color = COLOR_TEXT_PRIMARY

        container = ctk.CTkFrame(
            self,
            fg_color=bubble_color,
            corner_radius=RADIUS_MD,
            border_width=BORDER_WIDTH,
            border_color=border_color
        )
        container.pack(anchor=align, padx=PAD_SM, pady=PAD_XS, fill="none")

        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", padx=PAD_SM, pady=(PAD_XS, 0))

        timestamp = datetime.now().strftime("%H:%M:%S")
        sender_lbl = ctk.CTkLabel(
            header_frame,
            text=f"{sender}",
            font=ctk.CTkFont(family=FONT_UI_FAMILY, size=11, weight="bold"),
            text_color=COLOR_ACCENT if is_user else COLOR_DANGER
        )
        sender_lbl.pack(side="left")

        time_lbl = ctk.CTkLabel(
            header_frame,
            text=timestamp,
            font=ctk.CTkFont(family=FONT_UI_FAMILY, size=9),
            text_color=COLOR_TEXT_MUTED
        )
        time_lbl.pack(side="right", padx=(PAD_SM, 0))

        msg_lbl = ctk.CTkLabel(
            container,
            text=message,
            font=ctk.CTkFont(family=FONT_UI_FAMILY, size=13),
            text_color=text_color,
            wraplength=380,
            justify="left"
        )
        msg_lbl.pack(padx=PAD_SM, pady=(PAD_XS, PAD_SM))

# =============================================================================
# CONFRONTATION MODAL (English UI, Malayalam Speech & Dialogue)
# =============================================================================
class ConfrontationModal(ctk.CTkToplevel):
    def __init__(self, parent, error_log: str, source_code: str = ""):
        super().__init__(parent)
        self.parent = parent
        self.error_log = error_log
        self.source_code = source_code
        self.brain = CompilerGirlfriend(self.error_log, self.source_code)
        self.busy = False

        self.title("SECURITY GATEWAY // gcc-mol")
        self.geometry("640x780")
        self.minsize(560, 680)
        self.attributes("-topmost", True)
        self.configure(fg_color=COLOR_BG)
        self.protocol("WM_DELETE_WINDOW", self.deny_close)

        self.top_bar = ctk.CTkFrame(
            self,
            fg_color=COLOR_PANEL,
            corner_radius=RADIUS_LG,
            border_width=BORDER_WIDTH,
            border_color=COLOR_BORDER,
            height=40
        )
        self.top_bar.pack(fill="x", padx=PAD_MD, pady=(PAD_MD, PAD_SM))

        self.brand_lbl = ctk.CTkLabel(
            self.top_bar,
            text="SENTINEL INTERCEPT // COMPILER EXCEPTION",
            font=ctk.CTkFont(family=FONT_UI_FAMILY, size=11, weight="bold"),
            text_color=COLOR_DANGER
        )
        self.brand_lbl.pack(side="left", padx=PAD_MD, pady=PAD_SM)

        self.status_badge = ctk.CTkLabel(
            self.top_bar,
            text=MOOD_THEMES["COLD"]["status"],
            font=ctk.CTkFont(family=FONT_UI_FAMILY, size=11, weight="bold"),
            text_color=COLOR_ACCENT,
            fg_color=COLOR_CARD,
            corner_radius=RADIUS_SM,
            padx=PAD_SM,
            pady=2
        )
        self.status_badge.pack(side="right", padx=PAD_MD)

        self.canvas_card = ctk.CTkFrame(
            self,
            fg_color=MOOD_THEMES["COLD"]["bg"],
            corner_radius=RADIUS_LG,
            border_width=BORDER_WIDTH,
            border_color=MOOD_THEMES["COLD"]["border"]
        )
        self.canvas_card.pack(fill="x", padx=PAD_MD, pady=PAD_XS)

        self.girl_sprite = CuteSpritePlayer(self.canvas_card, sprite_folder="assets")
        self.girl_sprite.pack(padx=PAD_MD, pady=PAD_MD)

        self.chat_stream = ctk.CTkScrollableFrame(
            self,
            fg_color=COLOR_PANEL,
            corner_radius=RADIUS_LG,
            border_width=BORDER_WIDTH,
            border_color=COLOR_BORDER
        )
        self.chat_stream.pack(fill="both", expand=True, padx=PAD_MD, pady=PAD_SM)

        self.dock = ctk.CTkFrame(self, fg_color="transparent")
        self.dock.pack(fill="x", padx=PAD_MD, pady=(0, PAD_MD))

        self.entry = ctk.CTkEntry(
            self.dock,
            placeholder_text="Transmit apology or response to gcc-mol...",
            height=36,
            corner_radius=RADIUS_MD,
            font=ctk.CTkFont(family=FONT_UI_FAMILY, size=13),
            fg_color=COLOR_PANEL,
            border_width=BORDER_WIDTH,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_PRIMARY
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, PAD_SM))
        self.entry.bind("<Return>", lambda e: self.send_message())

        self.btn_send = ctk.CTkButton(
            self.dock,
            text="TRANSMIT",
            width=100,
            height=36,
            corner_radius=RADIUS_MD,
            font=ctk.CTkFont(family=FONT_UI_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="#ffffff",
            command=self.send_message
        )
        self.btn_send.pack(side="right")

        audio.play_random_sfx("COLD")

        self._set_busy_state(True, "THINKING...")
        threading.Thread(target=self._initial_reaction_worker, daemon=True).start()

    def _set_busy_state(self, is_busy: bool, button_text: str = "TRANSMIT"):
        self.busy = is_busy
        if is_busy:
            self.btn_send.configure(state="disabled", fg_color=COLOR_CARD, text_color=COLOR_TEXT_DISABLED, text=button_text)
            self.entry.configure(state="disabled")
        else:
            self.btn_send.configure(state="normal", fg_color=COLOR_ACCENT, text_color="#ffffff", text="TRANSMIT")
            self.entry.configure(state="normal")
            self.entry.focus()

    def _initial_reaction_worker(self):
        try:
            ans, mood, sfx, _ = self.brain.reply("__INIT__")
        except Exception:
            ans, mood, sfx = "ഇങ്ങനെ ഒരു കോഡ് എഴുതിവെച്ചിട്ട് നിൽക്കാൻ നിനക്ക് നാണമില്ലേ?!", "ANGRY", "ANGRY"
        self.after(0, self._render_initial_response, ans, mood, sfx)

    def _render_initial_response(self, ans: str, mood: str, sfx: str):
        self.add_message_bubble("gcc-mol", ans, is_user=False)
        self._set_busy_state(False)
        self.set_mood(mood)
        audio.play_random_sfx(mood)
        audio.speak_malayalam(ans, mood=mood)

    def deny_close(self):
        self.set_mood("ANGRY")
        audio.play_random_sfx("ANGRY")
        deny_text = "വിൻഡോ ക്ലോസ് ചെയ്ത് രക്ഷപ്പെടാൻ നോക്കല്ലേ! പ്രശ്നം തീർത്തിട്ട് പോയാൽ മതി!"
        self.add_message_bubble("gcc-mol", deny_text, is_user=False)
        audio.speak_malayalam(deny_text, mood="ANGRY")

    def set_mood(self, mood: str):
        theme = MOOD_THEMES.get(mood, MOOD_THEMES["COLD"])
        self.canvas_card.configure(fg_color=theme["bg"], border_color=theme["border"])
        self.girl_sprite.load_mood(mood.lower())
        self.status_badge.configure(text=theme["status"], text_color=theme["accent"])

    def add_message_bubble(self, sender: str, msg: str, is_user: bool):
        bubble = ChatBubble(self.chat_stream, sender=sender, message=msg, is_user=is_user)
        bubble.pack(fill="x", pady=2)
        self.after(100, lambda: self.chat_stream._parent_canvas.yview_moveto(1.0))

    def send_message(self):
        if self.busy:
            return
        txt = self.entry.get().strip()
        if not txt:
            return

        self.add_message_bubble("Developer", txt, is_user=True)
        self.entry.delete(0, "end")

        if txt.lower() == "/sry":
            self.add_message_bubble("SYSTEM", "⚡ ESCAPE OVERRIDE: Closing modal sequence...", is_user=False)
            audio.stop_all()
            self.parent.update_status("DISPUTE BYPASSED", state_type="danger")
            self.parent.console.log(">> /sry EXECUTED: Confrontation closed without compiler unlock. Fix syntax error to run.", stream="stderr")
            self.after(600, self.destroy)
            return

        self._set_busy_state(True, "THINKING...")
        threading.Thread(target=self._query_worker, args=(txt,), daemon=True).start()

    def _query_worker(self, txt: str):
        try:
            ans, mood, sfx, forgiven = self.brain.reply(txt)
        except Exception as e:
            ans, mood, sfx, forgiven = f"നെറ്റ്‌വർക്ക് തകരാർ: {str(e)}", "COLD", "COLD", False
        self.after(0, self._render_response, ans, mood, sfx, forgiven)

    def _render_response(self, ans: str, mood: str, sfx: str, forgiven: bool):
        self.add_message_bubble("gcc-mol", ans, is_user=False)
        self._set_busy_state(False)

        self.set_mood(mood)
        audio.play_random_sfx(mood)
        audio.speak_malayalam(ans, mood=mood)

        if forgiven:
            audio.stop_all()
            self.parent.btn_run.configure(state="normal", fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER)
            self.parent.update_status("BUILD UNLOCKED", state_type="success")
            self.parent.console.log(">> COMPILER DISPUTE RESOLVED BY gcc-mol.\n>> RESUMING LINKER & EXECUTING PIPELINE...", stream="system")
            self.parent.console.log("Hello, World!\n[Process completed with return code 0]", stream="success")
            self.after(2200, self.destroy)

# =============================================================================
# MAIN PROFESSIONAL IDE WORKSPACE
# =============================================================================
class AtoneApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("atone.c — Compiler & Diagnostics Studio")
        self.geometry("1100x820")
        self.minsize(880, 640)
        self.configure(fg_color=COLOR_BG)

        self.font_ui_header = ctk.CTkFont(family=FONT_UI_FAMILY, size=15, weight="bold")
        self.font_ui_body = ctk.CTkFont(family=FONT_UI_FAMILY, size=13)
        self.font_ui_label = ctk.CTkFont(family=FONT_UI_FAMILY, size=11)
        self.font_ui_badge = ctk.CTkFont(family=FONT_UI_FAMILY, size=10, weight="bold")
        self.font_code = ctk.CTkFont(family=FONT_CODE_FAMILY, size=13)

        self._init_top_bar()
        self._init_resizable_workspace()
        self._init_status_bar()

    def _init_top_bar(self):
        self.top_bar = ctk.CTkFrame(
            self,
            fg_color=COLOR_PANEL,
            height=44,
            corner_radius=0,
            border_width=BORDER_WIDTH,
            border_color=COLOR_BORDER
        )
        self.top_bar.pack(fill="x", side="top")

        brand_container = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        brand_container.pack(side="left", padx=PAD_MD)

        self.logo_lbl = ctk.CTkLabel(
            brand_container,
            text="ATONE.C",
            font=self.font_ui_header,
            text_color=COLOR_ACCENT
        )
        self.logo_lbl.pack(side="left")

        self.badge_core = ctk.CTkLabel(
            brand_container,
            text="v13.2-studio",
            font=self.font_ui_badge,
            fg_color=COLOR_CARD,
            text_color=COLOR_TEXT_MUTED,
            corner_radius=RADIUS_SM,
            padx=PAD_XS,
            pady=1
        )
        self.badge_core.pack(side="left", padx=PAD_SM)

        action_container = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        action_container.pack(side="right", padx=PAD_MD)

        self.status_chip = ctk.CTkLabel(
            action_container,
            text="READY",
            font=self.font_ui_badge,
            fg_color=COLOR_CARD,
            text_color=COLOR_TEXT_MUTED,
            corner_radius=RADIUS_SM,
            padx=PAD_SM,
            pady=3
        )
        self.status_chip.pack(side="left", padx=PAD_MD)

        self.btn_run = ctk.CTkButton(
            action_container,
            text="▶ Compile & Run",
            font=ctk.CTkFont(family=FONT_UI_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_SUCCESS_HOVER,
            text_color="#ffffff",
            height=28,
            width=140,
            corner_radius=RADIUS_MD,
            command=self.run_pipeline
        )
        self.btn_run.pack(side="right")

    def _init_resizable_workspace(self):
        self.paned_window = tk.PanedWindow(
            self,
            orient=tk.VERTICAL,
            bd=0,
            background=COLOR_BG,
            sashwidth=4,
            sashrelief="flat"
        )
        self.paned_window.pack(fill="both", expand=True, padx=PAD_MD, pady=PAD_SM)

        self.editor = CCodeEditor(self.paned_window, font_code=self.font_code)
        self.paned_window.add(self.editor, minsize=240)

        self.console = DiagnosticConsole(self.paned_window, font_code=self.font_code)
        self.paned_window.add(self.console, minsize=140)

        starter_code = (
            "#include <stdio.h>\n\n"
            "int main() {\n"
            "    // Missing semicolon here!\n"
            "    printf(\"Hello, World!\\n\")\n"
            "    return 0;\n"
            "}"
        )
        self.editor.set_code(starter_code)

    def _init_status_bar(self):
        self.status_bar = ctk.CTkFrame(
            self,
            fg_color=COLOR_PANEL,
            height=24,
            corner_radius=0,
            border_width=BORDER_WIDTH,
            border_color=COLOR_BORDER
        )
        self.status_bar.pack(fill="x", side="bottom")

        left_box = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        left_box.pack(side="left", padx=PAD_MD)

        def add_status_chip(parent, text):
            lbl = ctk.CTkLabel(
                parent,
                text=text,
                font=self.font_ui_label,
                text_color=COLOR_TEXT_MUTED
            )
            lbl.pack(side="left", padx=(0, PAD_MD))

        add_status_chip(left_box, "⚙ x86_64")
        add_status_chip(left_box, "⚡ gcc (GCC) 13.2.0")
        add_status_chip(left_box, "UTF-8")

        right_box = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        right_box.pack(side="right", padx=PAD_MD)

        self.sentinel_indicator = ctk.CTkLabel(
            right_box,
            text="● SENTINEL ONLINE: gcc-mol",
            font=self.font_ui_label,
            text_color=COLOR_ACCENT
        )
        self.sentinel_indicator.pack(side="right")

    def update_status(self, text: str, state_type: str = "default"):
        color_map = {
            "default": (COLOR_CARD, COLOR_TEXT_MUTED),
            "success": ("#dafbe1", COLOR_SUCCESS),
            "danger": (COLOR_DANGER_DIM, COLOR_DANGER),
            "warning": ("#fff8c5", COLOR_WARNING)
        }
        bg_col, text_col = color_map.get(state_type, color_map["default"])
        self.status_chip.configure(text=text, fg_color=bg_col, text_color=text_col)

    def run_pipeline(self):
        src = self.editor.get_code()
        with open("temp.c", "w", encoding="utf-8") as f:
            f.write(src)

        has_gcc = False
        self.console.clear()
        self.console.log(">> Initiating compilation: gcc -Wall temp.c -o temp_out", stream="system")

        try:
            p = subprocess.run(["gcc", "temp.c", "-o", "temp_out"], capture_output=True, text=True, timeout=5)
            rc, err = p.returncode, p.stderr
            has_gcc = True
        except FileNotFoundError:
            lines = [l.strip() for l in src.splitlines() if l.strip() and not l.strip().startswith("//")]
            missing_semi = any(
                ("printf" in l or "=" in l) and not l.endswith(";") and not l.endswith("{") and not l.endswith("}") 
                for l in lines
            )
            rc = 1 if missing_semi or 'printf("Hello, World!\\n")' in src else 0
            err = "temp.c:4:5: error: expected ';' before 'return'" if rc != 0 else ""
        except Exception as e:
            rc, err = 1, str(e)

        if rc != 0:
            self.btn_run.configure(state="disabled", fg_color=COLOR_CARD, text_color=COLOR_TEXT_DISABLED)
            self.update_status("BUILD FAILED", state_type="danger")
            self.console.log(err, stream="stderr")
            self.console.log(">> Compilation Sentinel Triggered: Escalating to gcc-mol...", stream="system")

            modal = ConfrontationModal(self, err, source_code=src)
            modal.focus()
        else:
            self.update_status("SUCCESS", state_type="success")
            if has_gcc:
                cmd = ["temp_out.exe"] if os.name == "nt" else ["./temp_out"]
                res = subprocess.run(cmd, capture_output=True, text=True)
                self.console.log(res.stdout, stream="stdout")
                self.console.log(f">> [Execution completed successfully (Exit {res.returncode})]", stream="success")
            else:
                self.console.log("Hello, World!", stream="stdout")
                self.console.log(">> [Execution completed successfully (Exit 0)]", stream="success")
            self.cleanup()

    def cleanup(self):
        for f in ["temp.c", "temp_out", "temp_out.exe"]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except OSError:
                    pass

if __name__ == "__main__":
    app = AtoneApp()
    app.mainloop()
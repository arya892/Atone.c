import customtkinter as ctk
import subprocess
import os

# Import Person 2's brain logic; fallback mock in Malayalam
try:
    from brain import CompilerGirlfriend
except ImportError:
    class CompilerGirlfriend:
        def __init__(self, error_log: str):
            self.error_log = error_log
            self.turn = 0

        def reply(self, user_message: str) -> tuple[str, bool]:
            self.turn += 1
            msg = user_message.lower()
            if any(w in msg for w in ["sorry", "മാപ്പ്", "ക്ഷമിക്കണം", "സത്യമായിട്ടും", "തെറ്റുപറ്റി"]):
                return ("സാരമില്ല, ഇത്തവണത്തേക്ക് ഞാൻ ക്ഷമിച്ചിരിക്കുന്നു. ഇനി ഇത് ആവർത്തിക്കരുത്! [STATUS: FORGIVEN]", True)
            if self.turn == 1:
                return ("എന്നോട് ഒന്നും മിണ്ടേണ്ട. ഞാൻ ആരാ നിനക്ക്? ഒരു സെമിക്കോളൻ പോലും ശ്രദ്ധിക്കാത്ത ആളാണ് എന്നെ നോക്കുന്നത്.", False)
            return ("ഒരു ഒഴിവുകഴിവും പറയേണ്ട. അത്രക്ക് അലക്ഷ്യമാണോ ഞാൻ നിനക്ക്?", False)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ConfrontationWindow(ctk.CTkToplevel):
    def __init__(self, parent, error_log: str):
        super().__init__(parent)
        self.parent = parent
        self.error_log = error_log
        self.gf_brain = CompilerGirlfriend(self.error_log)

        self.title("atone.c - gcc പിണക്കത്തിലാണ് 💔")
        self.geometry("520x620")
        
        # Keep window strictly on top and block manual closing
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self.prevent_close)

        # Header profile
        self.header = ctk.CTkLabel(
            self, 
            text="gcc 💔 (നിങ്ങളുടെ സിന്റാക്സ് കണ്ട് കട്ടക്കലിപ്പിലാണ്)", 
            font=("Arial", 14, "bold"), 
            text_color="#e74c3c"
        )
        self.header.pack(pady=(12, 4))

        self.sub_header = ctk.CTkLabel(
            self, 
            text="എറർ വന്നപ്പോൾ ഓർമ്മ വന്നല്ലേ? എന്നോട് ഒന്നും സംസാരിക്കേണ്ട.", 
            font=("Arial", 11, "italic"), 
            text_color="#bdc3c7"
        )
        self.sub_header.pack(pady=(0, 8))

        # Chat display feed
        self.chat_display = ctk.CTkTextbox(self, font=("Arial", 12), state="disabled", wrap="word")
        self.chat_display.pack(fill="both", expand=True, padx=15, pady=5)

        # Input box and send button
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(fill="x", padx=15, pady=12)

        self.chat_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="മാപ്പ് പറയുക / Apologize sincerely..."
        )
        self.chat_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.chat_entry.bind("<Return>", lambda event: self.send_message())

        self.send_button = ctk.CTkButton(
            self.input_frame, 
            text="അയക്കുക", 
            width=80, 
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.send_message
        )
        self.send_button.pack(side="right")

        # Initial opening line
        self.add_message("gcc 💔", "എന്നോട് ഒന്നും മിണ്ടേണ്ട. പോയി ആ Python-നെയോ Clang-നെയോ വിളിക്കു. ഞാൻ വേണ്ടല്ലോ.")

    def prevent_close(self):
        self.add_message("gcc 💔", "വിൻഡോ ക്ലോസ് ചെയ്ത് രക്ഷപ്പെടാൻ നോക്കേണ്ട! കാര്യം പറഞ്ഞിട്ട് പോയാൽ മതി.")

    def add_message(self, sender: str, text: str):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{sender}: {text}\n\n")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def send_message(self):
        user_msg = self.chat_entry.get().strip()
        if not user_msg:
            return

        self.add_message("You", user_msg)
        self.chat_entry.delete(0, "end")

        reply_text, is_forgiven = self.gf_brain.reply(user_msg)
        self.add_message("gcc 💔", reply_text)

        if is_forgiven:
            self.parent.run_button.configure(state="normal", fg_color="#2ecc71")
            self.parent.log_console(
                "കമ്പൈലേഷൻ അൺലോക്ക് ചെയ്തു: ആത്മാർത്ഥമായ മാപ്പപേക്ഷ സ്വീകരിച്ചിരിക്കുന്നു.\n\n"
                "പ്രോഗ്രാം ഔട്ട്പുട്ട്:\nHello, World!\n[Process completed successfully]"
            )
            self.destroy()

class CodeEditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("atone.c - Antagonistic C Compiler IDE")
        self.geometry("820x680")

        self.code_label = ctk.CTkLabel(self, text="C സോഴ്സ് കോഡ് (atone.c):", font=("Consolas", 14, "bold"))
        self.code_label.pack(anchor="w", padx=20, pady=(15, 0))

        self.editor = ctk.CTkTextbox(self, font=("Consolas", 13), wrap="none", height=340)
        self.editor.pack(fill="x", padx=20, pady=10)
        
        # Starter C code with intentional missing semicolon
        starter_code = (
            "#include <stdio.h>\n\n"
            "int main() {\n"
            "    printf(\"Hello, World!\\n\") // ഇവിടെ സെമിക്കോളൻ വിട്ടുപോയി!\n"
            "    return 0;\n"
            "}"
        )
        self.editor.insert("1.0", starter_code)

        # Run button
        self.run_button = ctk.CTkButton(
            self, 
            text="▶ Compile & Run atone.c", 
            font=("Arial", 14, "bold"), 
            fg_color="#2ecc71", 
            hover_color="#27ae60",
            command=self.compile_and_run
        )
        self.run_button.pack(pady=6)

        # Terminal output
        self.output_label = ctk.CTkLabel(self, text="ടെർമിനൽ ഔട്ട്പുട്ട്:", font=("Consolas", 14, "bold"))
        self.output_label.pack(anchor="w", padx=20, pady=(10, 0))

        self.console = ctk.CTkTextbox(self, font=("Consolas", 12), height=140, state="disabled")
        self.console.pack(fill="x", padx=20, pady=(5, 20))

    def log_console(self, text: str):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.insert("end", text)
        self.console.configure(state="disabled")

    def compile_and_run(self):
        code = self.editor.get("1.0", "end-1c")
        
        with open("temp.c", "w", encoding="utf-8") as f:
            f.write(code)

        try:
            compile_proc = subprocess.run(
                ["gcc", "temp.c", "-o", "temp_out"],
                capture_output=True,
                text=True
            )
            returncode = compile_proc.returncode
            stderr_msg = compile_proc.stderr
            has_gcc = True
        except FileNotFoundError:
            has_gcc = False
            lines = [line.strip() for line in code.splitlines() if line.strip() and not line.strip().startswith("//")]
            has_missing_semicolon = any(
                ("printf" in l or "=" in l) and not l.endswith(";") and not l.endswith("{") and not l.endswith("}")
                for l in lines
            )
            
            if has_missing_semicolon or 'printf("Hello, World!\\n")' in code:
                returncode = 1
                stderr_msg = (
                    "temp.c: In function 'main':\n"
                    "temp.c:4:5: error: expected ';' before 'return'\n"
                    "    4 |     printf(\"Hello, World!\\n\")\n"
                    "      |     ^~~~~~\n"
                    "      |     ;"
                )
            else:
                returncode = 0
                stderr_msg = ""

        if returncode != 0:
            self.run_button.configure(state="disabled", fg_color="#7f8c8d")
            ConfrontationWindow(self, stderr_msg)
        else:
            if has_gcc:
                run_cmd = ["temp_out.exe"] if os.name == "nt" else ["./temp_out"]
                run_proc = subprocess.run(run_cmd, capture_output=True, text=True)
                self.log_console(run_proc.stdout)
            else:
                self.log_console("Hello, World!\n\n[atone.c വഴി വിജയകരമായി റൺ ചെയ്തു]")
            self.cleanup()

    def cleanup(self):
        for f in ["temp.c", "temp_out", "temp_out.exe"]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except OSError:
                    pass

if __name__ == "__main__":
    app = CodeEditorApp()
    app.mainloop()
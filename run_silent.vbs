Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\zak1r\.gemini\antigravity\scratch\essential-words-telegram-bot"
WshShell.Run """C:\Users\zak1r\.gemini\antigravity\scratch\essential-words-telegram-bot\.venv\Scripts\python.exe"" run_bot.py", 0, False

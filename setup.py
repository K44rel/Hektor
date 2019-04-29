import cx_Freeze

executables = [cx_Freeze.Executable("main.py")]

cx_Freeze.setup(name="Hektor",
                options={"build_exe": {"packages":["pygame"],
                                                      "include_files":["Background.png", "GameOver.png", "highscore.txt", "maintower.png", "settings.py", "sprites.py", "spritesheet.png", "startscreen.png"] }}, executables = executables)
# TextReplacerPAAK ⌨️✨

A productivity tool that automatically replaces user-defined keywords with specified full text. 🚀

[![GitHub release](https://img.shields.io/github/release/htpaak/TextReplacerPAAK.svg?logo=github)](https://github.com/htpaak/TextReplacerPAAK/releases/latest)
[![GitHub downloads](https://img.shields.io/github/downloads/htpaak/TextReplacerPAAK/latest/total.svg?logo=github)](https://github.com/htpaak/TextReplacerPAAK/releases/latest)
[![GitHub downloads](https://img.shields.io/github/downloads/htpaak/TextReplacerPAAK/total.svg?logo=github)](https://github.com/htpaak/TextReplacerPAAK/releases)

## Quick Links 🔗

- [⬇️ Download Latest Release](https://github.com/htpaak/TextReplacerPAAK/releases/latest)
- [⭐ GitHub Repository](https://github.com/htpaak/TextReplacerPAAK)
- [💬 Feedback & Discussions](https://github.com/htpaak/TextReplacerPAAK/discussions)

## Key Features 🌟

*   **Easy Keyword-Replacement Phrase Setup**: Intuitively add, modify, and delete keywords and their replacement phrases as needed through a user-friendly GUI.
*   **Real-time Background Detection**: When you type a keyword in any program and press the spacebar or Enter key, it is instantly replaced with the corresponding phrase.
*   **System Tray Integration**: Minimize the program to the system tray icon to keep it running in the background without closing it.
*   **Automatic Settings Save & Load**: User-defined rules are automatically saved to a file and retained even after restarting the program. (`%LOCALAPPDATA%/TextReplacerPAAK/rules.json`)
*   **Startup Program Registration Option**: Provides an option to automatically run the program when Windows starts.
*   **PyQt5-based GUI**: Offers a user-friendly graphical interface.
*   **pynput-based Keyboard Listening**: Effectively detects global keyboard input.

## Demo 📸

(Please add demo images named `Demo_1.png` and `Demo_2.png` to the `assets` folder. The example images will be kept as is.)
![Demo_1](assets/Demo_1.png)
![Demo_2](assets/Demo_2.png)

## System Requirements 💻

*   **Operating System**: Windows
*   **Python**: 3.x (Python installation is not required when using the built executable file)
*   **Dependencies**: PyQt5, pynput (included in the executable file)

## Installation 🚀

1.  Download the latest release from the [Releases Page](https://github.com/htpaak/TextReplacerPAAK/releases/latest).
2.  Download the `TextReplacerPAAK_vX.Y.Z.exe` file (where X.Y.Z is the version number).
3.  No installation is needed. Simply run the downloaded `.exe` file.
4.  Launch TextReplacerPAAK and enjoy its convenient text replacement features! 🎉

## How to Use 📖

1.  Run the program, and the settings window will appear.
2.  In the **Add/Edit Rule** section:
    *   **Keyword**: Enter a short keyword to be replaced (e.g., `!mail`).
    *   **Replacement Text**: Enter the full phrase that will replace the keyword (e.g., `my.email@example.com`).
    *   Click the `Add Rule` button to add a new rule.
    *   Select an existing rule, modify its content, and click the `Update Rule` button to update it.
3.  In the **Existing Rules** section, you can see a list of currently registered rules.
4.  Select a rule and click the `Delete Selected Rule` button to delete it.
5.  All changes must be saved by clicking the `Save All Rules` button to be applied to the program and saved to the file.
6.  Click the `Hide Window` button or the window's close (X) button to minimize the program to the system tray without closing it.
7.  Right-click the system tray icon and select `Settings` to reopen the settings window, or select `Exit` to completely close the program.
8.  Check the `Start on Boot` checkbox in the status bar to automatically run the program when Windows starts (changes are saved immediately).

## Usage 🧭

*   Reduce repetitive typing by registering frequently used phrases (email addresses, home addresses, greetings, code snippets, etc.) as keywords.
*   Improve productivity by reducing typos and increasing typing speed.

## Development Information 👨‍💻

*   **Key Technologies**: Python, PyQt5 (GUI), pynput (Keyboard Listener)
*   **Build**: Built into a single executable file using PyInstaller (using the `build.bat` script).
*   **Logs**: Major events and errors occurring during application execution are recorded in a log file. (`%LOCALAPPDATA%/TextReplacerPAAK/app.log`)
*   **Configuration File Location**: `%LOCALAPPDATA%/TextReplacerPAAK/rules.json`

## Acknowledgments 🙏

*   Thanks to the developers of excellent open-source libraries like PyQt5 and pynput that made this project possible! 💖
*   All feedback, including improvement ideas, bug reports, and feature suggestions, is welcome! Please use [Discussions](https://github.com/htpaak/TextReplacerPAAK/discussions) or [Issues](https://github.com/htpaak/TextReplacerPAAK/issues).
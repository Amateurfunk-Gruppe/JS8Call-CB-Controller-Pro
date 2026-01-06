JS8Call CB Controller
A complete controller for JS8Call with special focus on the CB band (27.245 MHz), PNG flag support, and extensive automation features.

📋 Main Features
🚩 Flag Management (PNG)
Load PNG flags - Loads flag images from the flags folder

Flag caching - Stores loaded flags for quick access

Automatic scaling - Adjusts flags to a uniform size

Fallback flag - Displays default flag for unknown countries

Four display modes: PNG images, Unicode emoji, country codes, country names

🖥️ User Interface
Dark design - Modern dark theme interface

Collapsible panels - Expand/collapse station list and message log

Live station list - Real-time display of active stations

Message log - Chronological display of all messages

Color coding - Different colors for different message types

🔗 Connection Management
JS8Call startup - Automatically starts the JS8Call program

TCP connection - Establishes connection to JS8Call TCP server

Automatic reconnection - Multiple connection attempts on errors

Status display - Visual connection status (green/red)

📤 Message Transmission
Auto-enter function - Automatically sends Enter key after messages

Manual mode - Manual mode without auto-enter

CQ call - One-click CQ sending

Heartbeat sending - Automatic status updates

Test function - Tests auto-enter function

🤖 Bot System
Auto-respond bot - Automatic response to specific messages

Heartbeat detection - Detects and responds to heartbeats

CQ detection - Responds to CQ calls

Rate limiting - Prevents spam through time intervals

⚙️ Automation
Auto-CQ - Regularly sends CQ calls (every 10 minutes)

Auto-heartbeat - Regularly sends heartbeats (every 15 minutes)

Automatic logging - Saves messages to log files

Bot responses - Automatic responses to specific keywords

📡 Station Management
CB country detection - Detects country from CB prefix (e.g., 13 = Germany)

PNG flag display - Shows country flags in station list

SNR display - Signal-to-noise ratio for each station

Timestamp - UTC time of last message

Automatic sorting - New stations at top, old ones removed

🔧 Message Processing
JSON parsing - Processes JS8Call TCP messages

SNR extraction - Extracts SNR values from messages

Callsign validation - Checks validity of callsigns

Grid locator validation - Checks validity of grid locators

⚙️ Configuration
INI file support - Stores settings in configuration file

Station data - Stores callsign and grid locator

Path settings - JS8Call path, log and flag folders

Network settings - Host and port for TCP connection

📝 Logging & Diagnostics
UTF-8 logging - Correct Unicode processing for Windows

File logging - Saves all activities to log file

Error handling - Robust error handling with logs

Debug output - Detailed debug information

🪟 Windows Integration
Modern keyboard input - Uses Windows SendInput API

UTF-8 console fix - Fixes Windows console encoding

File dialog - Integrated file selection dialog

Tray support - Clean shutdown with configuration saving

🔒 Security Features
Input validation - Checks all user inputs

Rate limiting - Prevents excessive sending

Connection timeout - Prevents hanging connections

Exception handling - Catches and logs all errors

📻 CB-Specific Functions
CB prefix database - 352 CB countries with prefixes

27.245 MHz focus - Optimized for CB band

CB-specific responses - Customized bot responses for CB

Country mapping - Mapping of CB prefixes to countries

🎮 Direct Control of JS8Call
TX.SET_TEXT - Sets text in JS8Call input field

TX.SENT detection - Detects sent messages

RX messages - Receives all incoming messages

STATION.LOGGED - Detects new stations in log

🚀 Quick Start
Prerequisites
Windows operating system

JS8Call installed

Python 3.8 or higher

nstallation
bash
# Clone the repository
git clone https://github.com/yourusername/js8call-cb-controller.git

# Navigate to the directory
cd js8call-cb-controller

# Install dependencies
pip install -r requirements.txt

Edit config.ini with your settings:

ini
[Station]
callsign = YOURCALL
grid = YOURGRID

[Paths]
js8call_path = C:\Path\To\JS8Call.exe
flags_folder = flags
log_folder = logs

Usage
python js8call_controller.py

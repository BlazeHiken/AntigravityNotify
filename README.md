# Antigravity Notify

Stop checking Antigravity every 30 seconds. Get a custom sound when [Google Antigravity](https://antigravity.google/) needs your approval or finishes a task.

> Tested on: Antigravity IDE 2.5.5 on Windows 11.


## Features

- **Approval sound:** plays when the agent is waiting for your approval or input.
- **Completion sound:** plays when the agent finishes.
- **Your own sounds:** pick any `.wav` file with the Browse button, and preview it before saving.
- **Independent volume:** the volume slider only affects Antigravity Notify. It never changes your Windows master volume.
- **Runs without the app:** configure once, then close the app. Sounds keep playing.
- **Safe install:** adds its hooks alongside your existing ones instead of overwriting them, and can remove them cleanly. A backup of the original `hooks.json` is automatically created as `hooks.json.bak` before any changes are made.
- **Local only:** no account, no cloud, no telemetry.

## Supported Events

| Event | When it plays |
|---|---|
| Approval | Agent is waiting for your approval or input |
| Completion | Agent finishes its task |

## How It Works

```text
Google Antigravity
       |
       |  hook fires on an event
       v
  Hook script  --reads-->  your saved settings
       |
       v
  Plays your sound
```

The app is only for choosing sounds and installing the hooks. Once hooks are installed, Antigravity runs the hook script directly, so the app does not need to stay open.

## Requirements

- Windows
- Python 3.9+
- Google Antigravity IDE with hooks support

## Installation

1. Clone the repository:

   ```powershell
   git clone https://github.com/BlazeHiken/AntigravityNotify.git
   cd AntigravityNotify
   ```

2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Start the app:

   ```powershell
   python main.py
   ```

5. In the app:
   1. Choose your sounds and set the volume.
   2. Click **Install Hooks**.
   3. Fully quit and reopen Antigravity.

You can now close Antigravity Notify. Sounds will play without it running.

## Using Custom Sounds

Only `.wav` files are supported for now. Click **Browse** next to an event, pick a file, and use **Preview** to hear exactly what will play.

Notification volume is relative to the sound file's own level:

- 100% plays the file as recorded.
- Lower values make it quieter.
- It cannot make a quiet file louder than its original level.

Your Windows volume is never changed. For example, with Windows at 70% and Notify at 30%, the notification plays quieter, and Windows stays at 70%.

## Uninstall

1. Open the app and click **Remove Hooks**.
2. Fully quit and reopen Antigravity.
3. Delete the project folder.

## Troubleshooting

**No sound**

- A valid `.wav` file is selected for that event.
- The event is enabled and the master switch is on.
- Hooks are installed and Antigravity was fully restarted afterwards.
- Windows audio works, and your volume is not muted.

**Hooks don't trigger**

- Antigravity only reads hook configuration at startup. Fully quit and reopen it after installing or removing hooks.
- Use **Install Hooks** in the app rather than editing `hooks.json` by hand. The expected file shape and event names are specific to Antigravity and have changed between versions.
- Hook commands may not see your terminal's PATH, so the app registers absolute paths. If you moved the project folder or recreated the virtual environment, click **Install Hooks** again.

## Privacy

- No account, cloud service, telemetry, or audio uploads.
- Hooks read only the event type. Your prompts and project code are not stored or sent anywhere.
- The app only touches the local hook configuration, its own settings folder, and the sound files you choose.

## Contributing

Bug reports, fixes, and documentation improvements are welcome. By contributing, you agree your contribution is provided under this project's license.

## License

Antigravity Notify is source-available under the [PolyForm Noncommercial License 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0).

- You may use, modify, and redistribute it for any noncommercial purpose.
- Commercial use is not permitted.

This license covers only this project's own code. Third-party components, such as PySide6 and the audio library, keep their own licenses.

See [LICENSE](LICENSE) for the full terms.

Copyright (c) 2026 Siddharth Phadtare.
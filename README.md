Discord CMD Messenger

A command-line Discord bot utility written in Python using discord.py. It can send direct messages, post messages in server text channels, and look up basic user information exposed by Discord's official API.

The program asks for confirmation before sending a message. It allows user mentions and @everyone/@here mentions while blocking role mentions. Use mass mentions only when appropriate and permitted by the server.

Requirements
- Windows with Command Prompt or PowerShell
- Python 3.10 or newer recommended
- A Discord application and bot created in the Discord Developer Portal
- discord.py
  
Security: Never publish your bot token, commit it to Git, or paste it into chats. If a token is exposed, reset it in the Developer Portal and use the replacement. The environment variable is temporary and must be set again in a new terminal session.

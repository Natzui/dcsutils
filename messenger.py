import os
import asyncio
from datetime import datetime, timezone

import discord

TOKEN = os.getenv("X")
MAX_MESSAGE_LENGTH = 2000

if not TOKEN:
    raise SystemExit(
        "Missing DISCORD_BOT_TOKEN. Set it in CMD first."
    )


def allowed_user_mentions():
    """Allow user mentions and @everyone/@here; block role mentions."""
    return discord.AllowedMentions(
        users=True,
        roles=False,
        everyone=True,
        replied_user=False,
    )


async def get_input(prompt):
    """Read input without blocking the async event loop."""
    return await asyncio.to_thread(input, prompt)


def account_creation_date(user_id):
    """Calculate a Discord account creation date from a snowflake ID."""
    # Discord snowflake epoch: 2015-01-01 00:00:00 UTC
    timestamp_ms = (user_id >> 22) + 1420070400000
    try:
        return datetime.fromtimestamp(
            timestamp_ms / 1000, tz=timezone.utc
        )
    except (OverflowError, OSError, ValueError):
        return None


async def send_dm(client):
    """Send a direct message to a Discord user."""
    raw_id = await get_input("Recipient user ID: ")

    try:
        user_id = int(raw_id.strip())
        if user_id <= 0:
            raise ValueError
    except ValueError:
        print("Invalid Discord user ID.\n")
        return

    message = (await get_input("Message: ")).strip()

    if not message:
        print("Message cannot be empty.\n")
        return
    if len(message) > MAX_MESSAGE_LENGTH:
        print("Message exceeds 2000 characters.\n")
        return

    print(f"\nRecipient ID: {user_id}")
    print(f"Message: {message}")
    confirm = await get_input("Send this DM? (yes/no): ")
    if confirm.strip().lower() != "yes":
        print("Cancelled.\n")
        return

    try:
        user = await client.fetch_user(user_id)
        dm = await user.create_dm()
        await dm.send(message, allowed_mentions=allowed_user_mentions())
        print(f"DM sent to user {user_id}.\n")
    except discord.Forbidden:
        print("Discord refused the DM. Check access and privacy settings.\n")
    except discord.NotFound:
        print("User not found.\n")
    except discord.HTTPException as error:
        print(f"Discord API error: {error}\n")
    except (discord.ClientException, OSError) as error:
        print(f"Connection error: {error}\n")


async def send_channel_message(client):
    """Send a message to a server text channel."""
    raw_id = await get_input("Channel ID: ")

    try:
        channel_id = int(raw_id.strip())
        if channel_id <= 0:
            raise ValueError
    except ValueError:
        print("Invalid Discord channel ID.\n")
        return

    try:
        channel = await client.fetch_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            print("That ID is not a server text channel.\n")
            return

        message = (await get_input("Message: ")).strip()
        if not message:
            print("Message cannot be empty.\n")
            return
        if len(message) > MAX_MESSAGE_LENGTH:
            print("Message exceeds 2000 characters.\n")
            return

        print(f"\nChannel: #{channel.name}")
        print(f"Message: {message}")
        confirm = await get_input("Send this channel message? (yes/no): ")
        if confirm.strip().lower() != "yes":
            print("Cancelled.\n")
            return

        await channel.send(message, allowed_mentions=allowed_user_mentions())
        print(f"Message sent to #{channel.name}.\n")
    except discord.Forbidden:
        print("Bot cannot access the channel or send messages.\n")
    except discord.NotFound:
        print("Channel not found. Check the channel ID.\n")
    except discord.HTTPException as error:
        print(f"Discord API error: {error}\n")
    except (discord.ClientException, OSError) as error:
        print(f"Connection error: {error}\n")


async def detect_user(client):
    """Display user details exposed by Discord's standard bot API."""
    raw_id = await get_input("Discord User ID: ")

    try:
        user_id = int(raw_id.strip())
        if user_id <= 0:
            raise ValueError
    except ValueError:
        print("Invalid Discord user ID.\n")
        return

    # Discord snowflakes are currently 64-bit IDs. Very short IDs are
    # unlikely to be valid account IDs, but let Discord confirm validity.
    if user_id >= 2**64:
        print("That ID is too large to be a Discord snowflake.\n")
        return

    try:
        user = await client.fetch_user(user_id)
    except discord.NotFound:
        print("Discord could not find a user for that ID.\n")
        return
    except discord.Forbidden:
        print("Discord did not allow this user lookup.\n")
        return
    except discord.HTTPException as error:
        print(f"Discord API error: {error}\n")
        return
    except (discord.ClientException, OSError) as error:
        print(f"Connection error: {error}\n")
        return

    created = account_creation_date(user.id)

    print("\n========== DISCORD USER INFORMATION ==========")
    print(f"User ID          : {user.id}")
    print(f"Username         : {user.name}")
    print(f"Display Name     : {user.global_name or 'Not provided'}")
    print(f"Bot Account      : {'Yes' if user.bot else 'No'}")
    print(f"System Account   : {'Yes' if user.system else 'No'}")
    print(
        "Account Created  : "
        + (created.strftime("%Y-%m-%d %H:%M:%S UTC") if created else "Unavailable")
    )
    print(f"Avatar URL       : {user.display_avatar.url}")
    print(f"Profile URL      : https://discord.com/users/{user.id}")
    print("==============================================\n")


async def main():
    intents = discord.Intents.none()

    async with discord.Client(intents=intents) as client:
        try:
            # REST API use; gateway events are not required for this menu.
            await client.login(TOKEN)
            print("Discord bot authenticated successfully.")

            while True:
                print()
                print(" Ataraxia Messaging Terminal")
                print()
                print("1. Send a direct message")
                print("2. Send a broadcast message")
                print("3. Find user information")
                print("4. Exit")

                choice = (await get_input("Choose an option: ")).strip()

                if choice == "1":
                    await send_dm(client)
                elif choice == "2":
                    await send_channel_message(client)
                elif choice == "3":
                    await detect_user(client)
                elif choice == "4":
                    print("Messenger closed.")
                    break
                else:
                    print("Invalid option. Choose 1, 2, 3, or 4.")

        except discord.LoginFailure:
            print("Login failed. Check your bot token.")
        except (discord.ClientException, OSError) as error:
            print(f"Connection error: {error}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMessenger stopped.")
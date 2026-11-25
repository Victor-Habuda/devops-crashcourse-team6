import logging
import os
import re
import sys
from typing import Literal

import discord
from discord import app_commands

from bot.format import pr_embed, prs_embed, truncate
from bot.github import GitHub, GitHubError

log = logging.getLogger("pr-bot")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")
DEFAULT_REPO = os.getenv("GITHUB_REPO") or "Victor-Habuda/devops-crashcourse-team6"
REPO_RE = re.compile(r"^[\w.-]+/[\w.-]+$")


class PRBot(discord.Client):

    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.github = GitHub()

    async def setup_hook(self) -> None:
        await self.github.start()
        if DISCORD_GUILD_ID:
            guild = discord.Object(id=int(DISCORD_GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
        else:
            synced = await self.tree.sync()
        log.info("Synced %d slash commands (%s)", len(synced), "guild" if DISCORD_GUILD_ID else "global")

    async def close(self) -> None:
        await self.github.close()
        await super().close()

    async def on_ready(self) -> None:
        log.info("Logged in as %s", self.user)


client = PRBot()


async def check_repo(interaction: discord.Interaction, repo: str | None) -> str | None:
    repo = repo or DEFAULT_REPO
    if not REPO_RE.match(repo):
        await interaction.response.send_message("Repo must look like `owner/name`.", ephemeral=True)
        return None
    return repo


@client.tree.command(name="prs", description="List pull requests of the repository")
@app_commands.describe(
    state="Which PRs to show (default: open)",
    limit="How many (1-25, default 10)",
    repo=f"owner/repo (default: {DEFAULT_REPO})",
)
async def prs(
    interaction: discord.Interaction,
    state: Literal["open", "closed", "all"] = "open",
    limit: app_commands.Range[int, 1, 25] = 10,
    repo: str | None = None,
):
    if not (repo := await check_repo(interaction, repo)):
        return
    await interaction.response.defer()
    pulls = await client.github.list_pulls(repo, state, limit)
    if pulls is None:
        await interaction.followup.send(f"Repository `{repo}` not found (or private without a token).")
        return
    await interaction.followup.send(embed=prs_embed(repo, state, pulls))


@client.tree.command(name="pr", description="Show details of a single pull request")
@app_commands.describe(number="PR number", repo=f"owner/repo (default: {DEFAULT_REPO})")
async def pr(
    interaction: discord.Interaction,
    number: app_commands.Range[int, 1],
    repo: str | None = None,
):
    if not (repo := await check_repo(interaction, repo)):
        return
    await interaction.response.defer()
    data = await client.github.get_pull(repo, number)
    if data is None:
        await interaction.followup.send(f"PR #{number} not found in `{repo}`.")
        return
    await interaction.followup.send(embed=pr_embed(data))


@client.tree.error
async def on_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    original = getattr(error, "original", error)
    if not isinstance(original, GitHubError):
        log.exception("Command failed", exc_info=original)
    msg = f"Error: {truncate(str(original), 300)}"
    if interaction.response.is_done():
        await interaction.followup.send(msg, ephemeral=True)
    else:
        await interaction.response.send_message(msg, ephemeral=True)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if not DISCORD_TOKEN:
        log.warning("DISCORD_TOKEN not set — bot disabled")
        sys.exit(0)
    client.run(DISCORD_TOKEN, log_handler=None)


if __name__ == "__main__":
    main()

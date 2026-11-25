from datetime import datetime

import discord


def truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def parse_dt(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def ts(iso: str) -> str:
    return f"<t:{int(parse_dt(iso).timestamp())}:R>"


def pr_status(pr: dict) -> tuple[str, int]:
    if pr.get("merged_at"):
        return "MERGED", 0x9B59B6
    if pr["state"] == "closed":
        return "CLOSED", 0xE74C3C
    if pr.get("draft"):
        return "DRAFT", 0x95A5A6
    return "OPEN", 0x2ECC71


def branch(pr: dict) -> str:
    return f"`{pr['head']['ref']}` → `{pr['base']['ref']}`"


def prs_embed(repo: str, state: str, pulls: list[dict]) -> discord.Embed:
    embed = discord.Embed(
        title=f"Pull requests ({state}) · {repo}",
        url=f"https://github.com/{repo}/pulls",
        color=0x5865F2,
    )
    if not pulls:
        embed.description = "No pull requests found 🎉"
        return embed

    lines = []
    for pr in pulls:
        label, _ = pr_status(pr)
        lines.append(
            f"`{label}` [#{pr['number']} {truncate(pr['title'], 80)}]({pr['html_url']})\n"
            f"   by **{pr['user']['login']}** · {branch(pr)} · {ts(pr['created_at'])}"
        )
    embed.description = truncate("\n".join(lines), 4000)
    return embed


def pr_embed(pr: dict) -> discord.Embed:
    label, color = pr_status(pr)
    embed = discord.Embed(
        title=truncate(f"#{pr['number']} {pr['title']}", 256),
        url=pr["html_url"],
        color=color,
        description=truncate(pr["body"], 1000) if pr.get("body") else "_No description_",
        timestamp=parse_dt(pr["updated_at"]),
    )
    user = pr["user"]
    embed.set_author(name=user["login"], icon_url=user["avatar_url"], url=user["html_url"])
    embed.add_field(name="Status", value=label)
    embed.add_field(name="Branch", value=branch(pr))
    embed.add_field(name="Created", value=ts(pr["created_at"]))
    embed.add_field(
        name="Changes",
        value=f"+{pr['additions']} / -{pr['deletions']} in {pr['changed_files']} files",
    )
    embed.add_field(name="Commits", value=str(pr["commits"]))
    embed.add_field(name="Comments", value=str(pr["comments"] + pr["review_comments"]))
    return embed

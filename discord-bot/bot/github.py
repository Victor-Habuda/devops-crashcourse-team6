import os

import aiohttp

API = "https://api.github.com"


class GitHubError(Exception):
    pass

class GitHub:
    def __init__(self, token: str | None = None):
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "discord-pr-bot",
        }
        token = token or os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._headers = headers
        self._session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        self._session = aiohttp.ClientSession(
            headers=self._headers, timeout=aiohttp.ClientTimeout(total=15)
        )

    async def close(self) -> None:
        if self._session:
            await self._session.close()

    async def _get(self, path: str, params: dict | None = None):
        assert self._session, "call start() first"
        async with self._session.get(f"{API}{path}", params=params) as resp:
            if resp.status == 404:
                return None
            if resp.status >= 400:
                text = await resp.text()
                raise GitHubError(f"GitHub API {resp.status}: {text[:200]}")
            return await resp.json()

    async def list_pulls(self, repo: str, state: str = "open", limit: int = 10, sort: str = "created"):
        return await self._get(
            f"/repos/{repo}/pulls",
            {"state": state, "per_page": limit, "sort": sort, "direction": "desc"},
        )

    async def get_pull(self, repo: str, number: int):
        return await self._get(f"/repos/{repo}/pulls/{number}")

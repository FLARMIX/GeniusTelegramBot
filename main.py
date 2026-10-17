import asyncio
import html
import os
import re
import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.types import (
    InlineQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQueryResultArticle,
    InputTextMessageContent
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GENIUS_TOKEN = os.getenv("GENIUS_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def clean_lyrics(text: str) -> str:
    if not text:
        return ""

    if re.search(r"Read\s+More", text[:800], re.IGNORECASE):
        text = re.sub(r"^.{1,800}?Read\s+More\s*", "", text, flags=re.DOTALL | re.IGNORECASE)

    text = re.sub(r"^\d*\s*Contributors.*?Lyrics\s*", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"^Translations.*?Lyrics\s*", "", text, flags=re.DOTALL | re.IGNORECASE)

    text = re.sub(r"^.*?Lyrics\s*(\[)", r"\1", text, flags=re.DOTALL | re.IGNORECASE)

    text = re.sub(r"You might also like\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\d*\s*Embed\s*$", "", text.strip(), flags=re.IGNORECASE)

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


async def search_genius(session: aiohttp.ClientSession, query: str):
    url = "https://api.genius.com/search"
    headers = {
        "Authorization": f"Bearer {GENIUS_TOKEN}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    params = {"q": query}

    async with session.get(url=url, headers=headers, params=params) as resp:
        if resp.status == 200:
            try:
                data = await resp.json(content_type=None)
                return data.get("response", {}).get("hits", [])
            except Exception:
                return []
    return []


async def fetch_lyrics(session: aiohttp.ClientSession, url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8",
    }
    try:
        async with session.get(url=url, headers=headers, timeout=aiohttp.ClientTimeout(total=4)) as resp:
            if resp.status != 200:
                return "Не удалось загрузить страницу с текстом."
            html_text = await resp.text()
    except Exception:
        return "Не удалось получить текст песни (таймаут или ошибка сети)."

    soup = BeautifulSoup(html_text, "html.parser")

    for el in soup.find_all(attrs={"data-exclude-from-selection": "true"}):
        el.decompose()

    for el in soup.select("div[class*='LyricsHeader'], div[class*='SongDescription'], div[class*='LyricsEditDesktop']"):
        el.decompose()

    containers = soup.find_all("div", attrs={"data-lyrics-container": "true"})
    if not containers:
        return "Текст песни не найден на странице."

    lyrics_parts = []
    for c in containers:
        for br in c.find_all("br"):
            br.replace_with("\n")
        lyrics_parts.append(c.get_text())

    raw_lyrics = "\n\n".join(lyrics_parts)
    return clean_lyrics(raw_lyrics)


@dp.inline_query()
async def inline_search(inline_query: InlineQuery):
    query = inline_query.query.strip()
    if not query or len(query) < 2:
        return

    async with aiohttp.ClientSession() as session:
        hits = await search_genius(session, query)
        if not hits:
            return

        top_hits = hits[:3]

        tasks = [fetch_lyrics(session, hit["result"]["url"]) for hit in top_hits]
        lyrics_results = await asyncio.gather(*tasks)

        results = []
        for hit, lyrics in zip(top_hits, lyrics_results):
            song = hit["result"]
            song_id = str(song["id"])
            title = song["title"]
            artist = song["primary_artist"]["name"]
            thumb = song.get("song_art_image_thumbnail_url")
            song_url = song.get("url")

            safe_title = html.escape(f"{artist} — {title}")
            safe_lyrics = html.escape(lyrics)

            full_text = f"🎵 <b>{safe_title}</b>\n\n{safe_lyrics}"

            if len(full_text) > 4000:
                full_text = full_text[:3950] + "\n\n...<i>[текст обрезан из-за лимита длины]</i>..."

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔗 Открыть на Genius", url=song_url)]
            ]) if song_url else None

            # Превью первых строк песни прямо в списке поиска Telegram
            preview_snippet = lyrics[:90].replace("\n", " ") + "..."

            results.append(
                InlineQueryResultArticle(
                    id=song_id,
                    title=f"{artist} — {title}",
                    description=preview_snippet,
                    thumbnail_url=thumb,
                    input_message_content=InputTextMessageContent(
                        message_text=full_text,
                        parse_mode="HTML"
                    ),
                    reply_markup=keyboard
                )
            )

        await inline_query.answer(results, cache_time=60)


async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
export function youtubeEmbed(value) {
  try { const url = new URL(value); if (["www.youtube.com", "youtube.com", "www.youtube-nocookie.com"].includes(url.hostname)) { const id = url.searchParams.get("v") || url.pathname.split("/").pop(); return /^[\w-]{11}$/.test(id) ? `https://www.youtube-nocookie.com/embed/${id}` : null; } if (url.hostname === "youtu.be" && /^[\w-]{11}$/.test(url.pathname.slice(1))) return `https://www.youtube-nocookie.com/embed/${url.pathname.slice(1)}`; } catch { return null; } return null;
}

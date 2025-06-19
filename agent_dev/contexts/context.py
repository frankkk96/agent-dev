import feedparser


def parse_rss_to_context(rss_dict: dict) -> str:
    """
    Parse RSS feeds from a dictionary and combine them into a single context string.

    Args:
        rss_dict (dict): Dictionary where key is RSS name and value is RSS URL

    Returns:
        str: Combined context from all RSS feeds
    """
    context_parts = []

    for feed_name, feed_url in rss_dict.items():
        try:
            feed = feedparser.parse(feed_url)

            # Add feed header
            context_parts.append(f"\n=== {feed_name} ===\n")

            # Process each entry in the feed
            # Limit to 5 most recent entries per feed
            for entry in feed.entries[:10]:
                title = entry.get('title', 'No title')
                description = entry.get('description', 'No description')
                link = entry.get('link', '')
                published = entry.get('published', 'No date')

                entry_text = f"""
                                Title: {title}
                                Published: {published}
                                Link: {link}
                                Description: {description}
                                ---
                            """
                context_parts.append(entry_text)

        except Exception as e:
            context_parts.append(f"\nError parsing {feed_name}: {str(e)}\n")

    # Combine all parts into final context
    context = "\n".join(context_parts)
    return context

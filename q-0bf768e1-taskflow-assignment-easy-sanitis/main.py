def sanitize_tag(raw):
    """Return a safe TaskFlow tag slug from a raw user string.

    Rules:
      - If raw is not a str, return 'untitled'.
      - Strip surrounding whitespace.
      - Keep only ASCII letters, ASCII digits, hyphen '-' and underscore '_';
        drop every other character (spaces, punctuation, accented letters, emoji).
      - If nothing is left, return 'untitled'.
    """
    # TODO: implement the rules above
    pass
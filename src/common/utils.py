import re
from datetime import datetime, timedelta
import urllib

import redis
from flask import current_app, redirect, url_for


def extract_keywords(question, num_keywords=3):
    doc = current_app.nlp(question)
    keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'VERB']]
    keywords = keywords[:num_keywords]
    return ' '.join(keywords)


def trim_string(text, max_length, ellipsis="..."):
    if len(text) <= max_length:
        return text
    else:
        return text[:max_length-len(ellipsis)] + ellipsis


def history_to_json(input_string):
    json_data = []
    for conv in input_string:
        json_data.append({"type": type(conv).__name__, "content": conv.content, "context": conv.additional_kwargs})
    return json_data


def generate_redis_connection_string(url, port, password=None):
    if password:
        connection_string = f"redis://:{password}@{url}:{port}"
    else:
        connection_string = f"redis://{url}:{port}"
    return connection_string


def parse_query_string(q):
    query = urllib.parse.unquote(q).translate(str.maketrans('', '', "\"/\#@!?{}()|-=<>[];.,'")).strip()
    return query


def escape_query_string(q):
    query = urllib.parse.unquote(q).strip()
    special_chars = r"\"/\\#@!?{}()|\-=<>\[\];.,'"

    escaped_query = re.sub(r'([' + re.escape(special_chars) + '])', r'\\\1', query)

    return escaped_query


def extract_alphanumeric(input_string):
    alphanumeric_regex = re.compile(r'\w+')
    alphanumeric_matches = alphanumeric_regex.findall(input_string)
    alphanumeric_string = ''.join(alphanumeric_matches)
    return alphanumeric_string


def get_db(decode_responses=False):
    try:
        return redis.Redis(connection_pool=current_app.pool, decode_responses=decode_responses)
    except redis.exceptions.ConnectionError:
        return redirect(url_for("minipilot_bp.error-page"))


def ping_db(host, port, password):
    conn = redis.StrictRedis(host=host,
                             port=port,
                             password=password)
    return conn.ping()


def milliseconds_to_time_ago(milliseconds):
    # Convert milliseconds to seconds
    seconds = milliseconds / 1000.0

    # Get the current time
    current_time = datetime.utcnow()

    # Calculate the time ago
    time_ago = current_time - timedelta(seconds=seconds)

    # Format the time ago string
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{int(minutes)} minutes ago"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{int(hours)} hours ago"
    else:
        days = seconds / 86400
        return f"{int(days)} days ago"

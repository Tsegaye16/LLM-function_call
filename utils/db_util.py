import psycopg2
import re
from config import DB_CONFIG

def query_telegram_messages(query):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        channel_pattern = r"channel\s*['\"](.*?)['\"]"
        date_pattern = r"date\s*['\"](.*?)['\"]"
        message_pattern = r"message\s*['\"](.*?)['\"]"
        emoji_pattern = r"emoji\s*['\"](.*?)['\"]"
        youtube_pattern = r"youtube\s*['\"](.*?)['\"]"

        channel_match = re.search(channel_pattern, query, re.IGNORECASE)
        date_match = re.search(date_pattern, query, re.IGNORECASE)
        message_match = re.search(message_pattern, query, re.IGNORECASE)
        emoji_match = re.search(emoji_pattern, query, re.IGNORECASE)
        youtube_match = re.search(youtube_pattern, query, re.IGNORECASE)

        sql_query = "SELECT * FROM telegram_messages WHERE 1=1"
        params = []
        
        if channel_match: 
            sql_query += " AND channel_title = %s"
            params.append(channel_match.group(1))
        if date_match: 
            sql_query += " AND message_date = %s"
            params.append(date_match.group(1))
        if message_match: 
            sql_query += " AND message ILIKE %s"
            params.append(f"%{message_match.group(1)}%")
        if emoji_match: 
            sql_query += " AND emoji = %s"
            params.append(emoji_match.group(1))
        if youtube_match: 
            sql_query += " AND youtube = %s"
            params.append(youtube_match.group(1))

        cur.execute(sql_query, params)
        results = cur.fetchall()

        cur.close()
        conn.close()

        if results:
            return {
                "status": "success",
                "data": results
            }
        else:
            return {
                "status": "success",
                "message": "No matching messages found."
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error querying database: {str(e)}"
        }
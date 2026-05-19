import json
import os
import time
from scraper import get_live_scores
from notifier import send_whatsapp_message
from dotenv import load_dotenv

load_dotenv()

STATE_FILE = "state.json"
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 4800))  # Default to 8 minutes if not set

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}



def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def build_message(match):

    batter_text = ""

    for batter in match.get("top_batters", []):
        batter_text += f"• {batter}\n"

    bowler_text = ""

    for bowler in match.get("top_bowlers", []):
        bowler_text += f"• {bowler}\n"

    return (
        f"🏏 LIVE SCORE UPDATE\n\n"
        f"Team: {match['team']}\n"
        f"Score: {match['score']}\n"
        f"Overs: {match['overs']}\n\n"
        f"Top Batters\n"
        f"{batter_text}\n"
        f"Top Bowlers\n"
        f"{bowler_text}\n"
        f"Paddington CC Live Updates"
    )

def has_changed(old, new):
    return old != new

def run():

    print("Starting Play-Cricket WhatsApp Bot...")

    previous_data = None

    while True:

        try:

            matches = get_live_scores()

            if matches:

                current_data = str(matches)

                if current_data != previous_data:

                    previous_data = current_data

                    for match in matches:

                        message = build_message(match)

                        print("Sending update:")
                        print(message)

                        send_whatsapp_message(message)

                        # Send innings complete message
                        if match["overs"] == "40.0":

                            send_whatsapp_message(
                                "🏁 Innings Complete\n"
                                f"Final Score: {match['score']}"
                            )

            time.sleep(CHECK_INTERVAL)

        except Exception as e:

            print(f"ERROR: {e}")

            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run()
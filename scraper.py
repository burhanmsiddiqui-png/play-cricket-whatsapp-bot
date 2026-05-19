from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

import os
import time
import re

load_dotenv()

URL = os.getenv("PLAY_CRICKET_URL")


def get_live_scores():

    chrome_options = Options()

    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    driver.get(URL)

    time.sleep(10)

    page_text = driver.find_element(By.TAG_NAME, "body").text
    print(page_text)
    lines = page_text.splitlines()

    innings_list = []

    current_innings = {
        "team": "Paddington CC",
        "score": "",
        "overs": "",
        "top_batters": [],
        "top_bowlers": []
    }

    in_batting_section = False
    in_bowling_section = False

    for i, line in enumerate(lines):

        line = line.strip()

        # SCORE EXTRACTION
        total_match = re.search(
            r'Total:\s*(\d+)\s*\(\s*([\d\.]+)\s*Overs,\s*(\d+)\s*Wickets',
            line
        )

        if total_match:

            runs = total_match.group(1)
            overs = total_match.group(2)
            wickets = total_match.group(3)

            current_innings["score"] = f"{runs}/{wickets}"
            current_innings["overs"] = overs

        # SECTION DETECTION
        if line == "BATTER":
            in_batting_section = True
            in_bowling_section = False
            continue

        if line == "BOWLER":
            in_batting_section = False
            in_bowling_section = True
            continue

        # BATTER EXTRACTION
        # BATTER EXTRACTION
        if in_batting_section:

            invalid_lines = [
                "not out",
                "Captain",
                "Wicket Keeper",
                "BATTER",
                "BOWLER"
            ]

            if line in invalid_lines:
                continue

            batter_name_match = re.match(
                r'^([A-Za-z ]+)$',
                line
            )

            if batter_name_match:

                batter_name = batter_name_match.group(1).strip()

                for j in range(i + 1, min(i + 6, len(lines))):

                    stats_line = lines[j].strip()

                    stats_match = re.match(
                        r'^(\d+)\s+(\d+)\s+\d+\s+\d+\s+[\d\.]+$',
                        stats_line
                    )

                    if stats_match:

                        batter_runs = stats_match.group(1)
                        batter_balls = stats_match.group(2)

                        current_innings["top_batters"].append({
                            "name": batter_name,
                            "runs": int(batter_runs),
                            "balls": batter_balls
                        })

                        break

        # BOWLER EXTRACTION
        if in_bowling_section:

            bowler_match = re.match(
                r'^([A-Za-z ]+)\s+[\d\.]+\s+\d+\s+\d+\s+(\d+)',
                line
            )

            if bowler_match:

                bowler_name = bowler_match.group(1).strip()
                wickets_taken = int(bowler_match.group(2))

                if wickets_taken > 0:

                    current_innings["top_bowlers"].append(
                        f"{bowler_name} - {wickets_taken} wickets"
                    )

    # SORT TOP BATTERS
    sorted_batters = sorted(
        current_innings["top_batters"],
        key=lambda x: x["runs"],
        reverse=True
    )

    current_innings["top_batters"] = [
        f"{b['name']} {b['runs']} ({b['balls']})"
        for b in sorted_batters[:2]
    ]

    # TOP 2 BOWLERS
    current_innings["top_bowlers"] = current_innings["top_bowlers"][:2]

    innings_list.append(current_innings)

    driver.quit()

    print("\n===== MATCHES FOUND =====\n")
    print(innings_list)

    return innings_list
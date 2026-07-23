"""Client-facing review notes. Plain English, specific numbers, no jargon.

These are generated from the computed figures so they always match the tool.
They obey the-humanizer rules: no em dashes, no buzzwords, varied sentences.
"""


def review_note(client, base_market, base_goal, target_market, target_goal,
                conditions):
    if client.key == "margaret":
        return (
            "Dear Margaret,\n\n"
            "Your portfolio is profiled at the most cautious end, and on the "
            "measure most people mean by risk it is calm. It moves around less "
            "and falls less far than a bolder mix. But the risk that matters most "
            "to you is a different one, whether the money lasts. On our "
            f"simulations the most cautious mix funds your full 30 years about "
            f"{int(base_goal)}% of the time. A more balanced mix raises that to "
            f"roughly {int(target_goal)}%.\n\n"
            "The trade is real. You would see bigger swings along the way, with a "
            f"worst historical fall nearer {abs(target_market['max_drawdown_pct']):.0f}% "
            f"than {abs(base_market['max_drawdown_pct']):.0f}%. In exchange you cut "
            "the chance of running short later in retirement. For a 30-year plan "
            "drawing 4%, that is a trade I would recommend making."
        )
    if client.key == "tom":
        return (
            "Dear Tom,\n\n"
            "Balanced sounds safe for a six-year plan, and over the long run the "
            "label is not wrong. The catch is the bond half. It is meant to steady "
            "things when shares fall, but in 2022 bonds and shares fell together, "
            f"and right now they are still moving in step (correlation "
            f"{conditions['value']:+.2f}).\n\n"
            f"Today your balanced mix reaches the deposit about {int(base_goal)}% of "
            "the time. As your purchase date gets close I would step the risk down. "
            f"That lowers the headline chance, to nearer {int(target_goal)}%, but it "
            "protects the money you have already built from a bad final year, the "
            "kind that bonds may not cushion the way the label assumes. Close to the "
            "date, keeping the deposit matters more than reaching for a bigger one."
        )
    if client.key == "priya":
        return (
            "Dear Priya,\n\n"
            "You are happy with a bold portfolio, and that is fine. The issue is "
            "not how much risk you are taking but what kind. Your equity has "
            "drifted into a heavy semiconductor position. Two adventurous investors "
            "can look identical on a risk label and hold very different real risk. "
            f"Your concentrated version fell about {abs(base_market['recent_dd_pct']):.0f}% "
            "in the 2021 to 2022 sell-off, against about "
            f"{abs(target_market['recent_dd_pct']):.0f}% for a diversified "
            "adventurous mix.\n\n"
            "The wider market is not unusually concentrated today, so this is not a "
            "warning about a bubble. It is about the position you already hold. My "
            "recommendation is to trim the concentration back toward a diversified "
            "holding, so you keep the risk you chose and lose the risk you drifted "
            "into."
        )
    raise ValueError(client.key)

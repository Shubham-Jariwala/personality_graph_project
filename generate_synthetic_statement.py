import random
import argparse


def generate_synthetic_criminal_statement(events=2, seed=None):
    """Generate a cohesive, multi-paragraph synthetic criminal statement.

    Structure:
      - Intro paragraph (context)
      - `events` paragraphs: each describes a situation, emotion, action, and motive woven into sentences
      - Closing paragraph (reflection/summary)

    This produces a more realistic single-statement multi-paragraph text instead of many short
    disconnected paragraphs.
    """
    if seed is not None:
        random.seed(seed)

    emotions = ["angry", "anxious", "calm", "nervous", "remorseful", "defensive", "distraught"]
    actions = [
        "shouted at the officer",
        "refused to cooperate",
        "apologized repeatedly",
        "blamed his partner",
        "explained the plan calmly",
        "avoided eye contact",
        "sobbed quietly",
    ]
    motives = [
        "needed money",
        "wanted revenge",
        "acted impulsively",
        "was pressured by peers",
        "was afraid of consequences",
        "wanted recognition",
        "felt cornered",
    ]

    situations = [
        "the interrogation room",
        "the transport after arrest",
        "when shown the evidence",
        "the courtroom hallway",
        "the holding cell",
    ]

    # Intro
    intro_templates = [
        "The following is the recorded statement given by the suspect during questioning.",
        "The suspect provided the following account over the course of the interview.",
        "Below is a summary of the suspect's remarks captured during the interview session.",
    ]
    intro = random.choice(intro_templates)

    paragraphs = [intro]

    # Event paragraphs (cohesive, with multiple sentences each)
    for i in range(events):
        situation = random.choice(situations)
        emotion = random.choice(emotions)
        action = random.choice(actions)
        motive = random.choice(motives)

        # Build a few sentences that read like a real account
        sent1 = f"During {situation}, the suspect appeared {emotion} and {action}."
        sent2 = (
            f"When questioned about the reasons, he said he {motive}; "
            "at times his voice wavered and he seemed uncertain about some details."
        )
        sent3 = (
            "Officers noted changes in his tone and body language, "
            "which suggested complexity in his motives and emotions."
        )

        paragraph = " ".join([sent1, sent2, sent3])
        paragraphs.append(paragraph)

    # Closing paragraph
    closing_templates = [
        "The tone of the suspect's voice and body language suggested complex emotions throughout.",
        "Overall, the suspect's account contained inconsistencies and signs of stress.",
        "The recorded account was logged and appended to the case file for further review.",
    ]
    paragraphs.append(random.choice(closing_templates))

    return "\n\n".join(paragraphs) + "\n\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a cohesive synthetic criminal statement")
    parser.add_argument("--events", "-e", type=int, default=2, help="Number of event paragraphs to include")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    args = parser.parse_args()

    text = generate_synthetic_criminal_statement(events=args.events, seed=args.seed)
    with open("criminal_statement.txt", "w") as f:
        f.write(text)
    print(f"✅ Synthetic multi-paragraph statement saved to 'criminal_statement.txt' ({args.events} events)")

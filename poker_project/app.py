from flask import Flask, render_template, request, session
import random
import itertools
app = Flask(__name__)
app.secret_key = "anything"
BIG_BLIND = 50
value_map = {
    "A": 14, "K": 13, "Q": 12, "J": 11,
    "10": 10, "9": 9, "8": 8, "7": 7,
    "6": 6, "5": 5, "4": 4, "3": 3, "2": 2
}
rank_names = {
    14: "Aces", 13: "Kings", 12: "Queens", 11: "Jacks",
    10: "Tens", 9: "Nines", 8: "Eights", 7: "Sevens",
    6: "Sixes", 5: "Fives", 4: "Fours", 3: "Threes", 2: "Twos"
}
def card():
    nums = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    suits = ["s", "h", "d", "c"]

    while True:
        c = random.choice(nums) + random.choice(suits)
        if c not in session["dealt"]:
            session["dealt"].append(c)
            session.modified = True
            return c


def get_straight_high(values):
    unique_values = sorted(set(values), reverse=True)

    if set([14, 5, 4, 3, 2]).issubset(set(values)):
        return 5

    for i in range(len(unique_values) - 4):
        group = unique_values[i:i + 5]
        if group[0] - group[4] == 4:
            return group[0]

    return 0


def check_hand(hand):
    suit_values = {}
    counts = {}
    suits = {}
    values = []

    for c in hand:
        value = c[:-1]
        suit = c[-1]

        counts[value_map[value]] = counts.get(value_map[value], 0) + 1
        suits[suit] = suits.get(suit, 0) + 1
        values.append(value_map[value])

        if suit not in suit_values:
            suit_values[suit] = []

        suit_values[suit].append(value_map[value])

    values.sort(reverse=True)

    straight_high = get_straight_high(values)
    flush = 5 in suits.values()

    groups = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)

    straight_flush_high = 0

    for suit in suit_values:
        if len(suit_values[suit]) >= 5:
            high = get_straight_high(suit_values[suit])
            if high > straight_flush_high:
                straight_flush_high = high

    if straight_flush_high == 14:
        return (9, 14)

    if straight_flush_high:
        return (8, straight_flush_high)

    if groups[0][1] == 4:
        four = groups[0][0]
        kicker = max(v for v in values if v != four)
        return (7, four, kicker)

    if groups[0][1] == 3 and groups[1][1] >= 2:
        return (6, groups[0][0], groups[1][0])

    if flush:
        flush_cards = []
        for suit in suit_values:
            if len(suit_values[suit]) >= 5:
                flush_cards = sorted(suit_values[suit], reverse=True)[:5]
                break
        return (5, flush_cards)

    if straight_high:
        return (4, straight_high)

    if groups[0][1] == 3:
        three = groups[0][0]
        kickers = [v for v in values if v != three]
        return (3, three, kickers)

    if groups[0][1] == 2 and groups[1][1] == 2:
        high_pair = max(groups[0][0], groups[1][0])
        low_pair = min(groups[0][0], groups[1][0])
        kicker = max(v for v in values if v != high_pair and v != low_pair)
        return (2, high_pair, low_pair, kicker)

    if groups[0][1] == 2:
        pair = groups[0][0]
        kickers = [v for v in values if v != pair]
        return (1, pair, kickers)

    return (0, values)


def best_hand(cards):
    best = None

    for combo in itertools.combinations(cards, 5):
        score = check_hand(combo)

        if best is None or score > best:
            best = score

    return best


def hand_description(score):
    hand_type = score[0]

    if hand_type == 9:
        return "Royal Flush"

    elif hand_type == 8:
        return f"Straight Flush, {rank_names[score[1]]} high"

    elif hand_type == 7:
        return f"Four of a Kind, {rank_names[score[1]]}"

    elif hand_type == 6:
        return f"Full House, {rank_names[score[1]]} over {rank_names[score[2]]}"

    elif hand_type == 5:
        return f"Flush, {rank_names[max(score[1])]} high"

    elif hand_type == 4:
        return f"Straight, {rank_names[score[1]]} high"

    elif hand_type == 3:
        return f"Three of a Kind, {rank_names[score[1]]}"

    elif hand_type == 2:
        return f"Two Pair, {rank_names[score[1]]} and {rank_names[score[2]]}"

    elif hand_type == 1:
        return f"Pair of {rank_names[score[1]]}"

    else:
        return f"{rank_names[score[1][0]]} High"


def finish_hand(start_message=""):
    your_hand = session["your_cards"] + session["river"]
    their_hand = session["their_cards"] + session["river"]

    your_score = best_hand(your_hand)
    their_score = best_hand(their_hand)

    session["your_hand_name"] = hand_description(your_score)
    session["their_hand_name"] = hand_description(their_score)

    if your_score > their_score:
        session["points"] += session["total_bid"] * 2
        message = start_message + "You won the hand!"
    elif your_score == their_score:
        session["points"] += session["total_bid"]
        message = start_message + "Tie hand."
    else:
        message = start_message + "You lost this hand."

    if session["points"] >= 10000:
        message = "You won the game! Great job, we will reset your points to 5000 and you can keep playing."
        session["points"] = 5000
    elif session["points"] <= 0:
        message = "The computer won all of your points, better luck next time. We will reset your points to 5000 and you can try again."
        session["points"] = 5000

    session["game_over"] = True
    session["computer_bet"] = 0
    return message


def deal_next_card():
    if len(session["river"]) < 5:
        r = card()
        session["river"].append(r)
        session["river_imgs"].append(f"{r}.png")

        if len(session["river"]) == 4:
            return " Turn dealt."
        elif len(session["river"]) == 5:
            return " River dealt."

    return ""


def computer_bid(stage, player_bid):
    their_hand = session["their_cards"] + session["river"]
    score = best_hand(their_hand)[0]

    points = session["points"]
    risk = player_bid / points if points > 0 else 1

    # Add some randomness based on the stage
    if stage == "preflop":
        confidence = score + random.randint(0, 2)
    elif stage == "flop":
        confidence = score + random.randint(0, 1)
    else:
        confidence = score

    # Fold weak hands if the bet is too expensive
    if confidence <= 0 and risk > 0.10:
        return "fold", 0

    if confidence == 1 and risk > 0.25:
        return "fold", 0

    if confidence == 2 and risk > 0.50:
        return "fold", 0

    # Very strong hand
    if confidence >= 4:
        if random.randint(1, 100) <= 80:
            amount = min(player_bid + random.choice([50, 100, 150]), points)
            amount = max(50, (amount // 50) * 50)
            return "raise", amount
        else:
            return "call", player_bid

    # Good hand
    elif confidence >= 2:
        if random.randint(1, 100) <= 35:
            amount = min(player_bid + 50, points)
            amount = max(50, (amount // 50) * 50)
            return "raise", amount
        else:
            return "call", player_bid

    # Weak hand
    elif confidence >= 1:
        if random.randint(1, 100) <= 75:
            return "call", player_bid
        else:
            return "fold", 0

    # High card
    else:
        if risk <= 0.10 and random.randint(1, 100) <= 15:
            amount = min(player_bid + 50, points)
            amount = max(50, (amount // 50) * 50)
            return "raise", amount
        elif risk <= 0.10:
            return "call", player_bid
        else:
            return "fold", 0
        

def show_page(message=""):
    session.modified = True

    return render_template("index.html",
        your_cards=session.get("your_cards"),
        your_imgs=session.get("your_imgs"),
        their_cards=session.get("their_cards"),
        their_imgs=session.get("their_imgs"),
        river=session.get("river", []),
        river_imgs=session.get("river_imgs", []),
        points=session.get("points", 5000),
        total_bid=session.get("total_bid", 0),
        message=message,
        game_over=session.get("game_over", False),
        your_hand_name=session.get("your_hand_name", ""),
        their_hand_name=session.get("their_hand_name", "")
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/deal", methods=["POST"])
def deal():
    session["dealt"] = []

    opcard1 = card()
    opcard2 = card()
    card1 = card()
    card2 = card()

    r1 = card()
    r2 = card()
    r3 = card()

    session["your_cards"] = [card1, card2]
    session["your_imgs"] = [f"{card1}.png", f"{card2}.png"]

    session["their_cards"] = [opcard1, opcard2]
    session["their_imgs"] = [f"{opcard1}.png", f"{opcard2}.png"]

    session["river"] = [r1, r2, r3]
    session["river_imgs"] = [f"{r1}.png", f"{r2}.png", f"{r3}.png"]

    if session.get("points", 0) <= 0:
        session["points"] = 5000
    else:
        session["points"] = session.get("points", 5000)

    session["total_bid"] = 0
    session["folded"] = False
    session["game_over"] = False
    session["your_hand_name"] = ""
    session["their_hand_name"] = ""
    session["computer_bet"] = 0

    blind = min(BIG_BLIND, session["points"])
    session["points"] -= blind
    session["total_bid"] += blind

    return show_page("New hand dealt. You posted the big blind of 50.")


@app.route("/bid", methods=["POST"])
def bid():
    bid_amount = int(request.form["bid"])

    if bid_amount <= 0:
        return show_page("Your bid must be more than 0.")

    if bid_amount > session["points"]:
        return show_page("You do not have enough points for that bid.")

    session["points"] -= bid_amount
    session["total_bid"] += bid_amount

    computer_action, computer_amount = computer_bid(len(session["river"]), bid_amount)

    if computer_action == "fold":
        session["points"] += session["total_bid"] * 2
        session["game_over"] = True
        return show_page("Computer folded. You won the hand!")

    elif computer_action == "call":
        session["total_bid"] += computer_amount
        message = f"Computer called {computer_amount}."

        if len(session["river"]) >= 5:
            message = finish_hand(message + " ")
            return show_page(message)

        message += deal_next_card()
        return show_page(message)

    elif computer_action == "raise":
        session["computer_bet"] = computer_amount
        session["total_bid"] += computer_amount
        return show_page(f"Computer raised to {computer_amount}. Call, fold, or raise.")


@app.route("/check", methods=["POST"])
def check():
    if len(session["river"]) >= 5:
        message = finish_hand("You checked. ")
        return show_page(message)

    if random.randint(1, 100) <= 50:
        computer_bet = random.randint(50, 200)
        session["computer_bet"] = computer_bet
        return show_page(f"You checked. Computer bid {computer_bet}.")

    message = "You checked. Computer checked."
    message += deal_next_card()
    return show_page(message)


@app.route("/call", methods=["POST"])
def call():
    amount = session.get("computer_bet", 0)

    if amount > session["points"]:
        amount = session["points"]

    session["points"] -= amount
    session["total_bid"] += amount * 2
    session["computer_bet"] = 0

    if len(session["river"]) >= 5:
        message = finish_hand("You called. ")
        return show_page(message)

    message = "You called."
    message += deal_next_card()
    return show_page(message)


@app.route("/raise", methods=["POST"])
def raise_bet():
    raise_input = request.form.get("raise_amount", "").strip()

    if raise_input == "":
        return show_page("Please enter a raise amount.")

    try:
        raise_amount = int(raise_input)
    except ValueError:
        return show_page("Please enter a valid whole number.")

    if raise_amount <= 0:
        return show_page("Your raise must be more than 0.")

    total_to_put_in = session.get("computer_bet", 0) + raise_amount

    if total_to_put_in > session["points"]:
        total_to_put_in = session["points"]

    session["points"] -= total_to_put_in
    session["total_bid"] += total_to_put_in
    session["computer_bet"] = 0

    if random.randint(1, 100) <= 35:
        session["points"] += session["total_bid"] * 2
        session["game_over"] = True
        return show_page("Computer folded. You won the hand.")

    session["total_bid"] += raise_amount

    if len(session["river"]) >= 5:
        message = finish_hand(f"Computer called your raise of {raise_amount}. ")
        return show_page(message)

    message = f"Computer called your raise of {raise_amount}."
    message += deal_next_card()
    return show_page(message)


@app.route("/fold", methods=["POST"])
def fold():
    session["game_over"] = True
    session["folded"] = True
    session["computer_bet"] = 0

    return show_page("You folded. The computer wins the hand.")


if __name__ == "__main__":
    app.run(debug=True)
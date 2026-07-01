import json
import os
import random
import itertools

again = "yes"

while again.lower() == "yes":
    filename = "score.json"
    
    if os.path.exists(filename):
        with open(filename, "r") as file:
            data = json.load(file)
            points = data.get("points", 5000)
            wins = data.get("wins", 0)
            losses = data.get("losses", 0)
    else:
        points = 5000
        wins = 0
        losses = 0

    dealt = []

    def card():
        num = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        suit = ["♤", "♥", "♢", "♧"]

        while True:
            random_number = random.choice(num)
            random_suit = random.choice(suit)

            random_card = f"{random_number}{random_suit}"

            if random_card not in dealt:
                dealt.append(random_card)
                return random_card

    value_map = {
        "A": 14,
        "K": 13,
        "Q": 12,
        "J": 11,
        "10": 10,
        "9": 9,
        "8": 8,
        "7": 7,
        "6": 6,
        "5": 5,
        "4": 4,
        "3": 3,
        "2": 2
    }

    def check_hand(hand):
        counts = {}
        suits = {}
        values = []

        for card in hand:
            value = card[:-1]
            suit = card[-1]

            # count values
            if value in counts:
                counts[value] += 1
            else:
                counts[value] = 1

            # count suits
            if suit in suits:
                suits[suit] += 1
            else:
                suits[suit] = 1

            values.append(value_map[value])

        values.sort()

        # check straight
        straight = True

        for i in range(len(values) - 1):
            if values[i] + 1 != values[i + 1]:
                straight = False

        if values == [2, 3, 4, 5, 14]:
            straight = True

        # check flush
        flush = 5 in suits.values()

        # scoring
        if straight and flush:
            return 8
        elif 4 in counts.values():
            return 7
        elif 3 in counts.values() and 2 in counts.values():
            return 6
        elif flush:
            return 5
        elif straight:
            return 4
        elif 3 in counts.values():
            return 3
        elif list(counts.values()).count(2) == 2:
            return 2
        elif 2 in counts.values():
            return 1
        else:
            return 0

    def best_hand(seven_cards):
        best_score = 0

        for combo in itertools.combinations(seven_cards, 5):
            score = check_hand(combo)

            if score > best_score:
                best_score = score

        return best_score

    hand = []
    ophand = []

    opcard1 = card()
    opcard2 = card()

    card1 = card()
    card2 = card()

    river1 = card()
    river2 = card()
    river3 = card()

    hand.append(card1)
    hand.append(card2)
    hand.append(river1)
    hand.append(river2)
    hand.append(river3)

    ophand.append(opcard1)
    ophand.append(opcard2)
    ophand.append(river1)
    ophand.append(river2)
    ophand.append(river3)

    print()
    print("Here is the flop: ")
    print(river1, river2, river3)
    print()
    print("Here are your two cards:")
    print(card1, card2)
    print(f"Your total points: {points}")
    print()

    bid1 = int(input("How much would you like to bid? "))
    points = points - bid1


    river4 = card()
    hand.append(river4)
    ophand.append(river4)

    print()
    print("The turn: ")
    print(river1, river2, river3, river4)
    print()
    print("Here are your two cards:")
    print(card1, card2)
    print(f"Your total points: {points}")
    print()

    bid2 = int(input("How much would you like to bid? "))
    points = points - bid2

    river5 = card()
    hand.append(river5)
    ophand.append(river5)

    print()
    print("The river: ")
    print(river1, river2, river3, river4, river5)
    print()
    print("Here are your two cards:")
    print(card1, card2)
    print(f"Your total points: {points}")
    print()

    bid3 = int(input("How much would you like to bid? "))
    points = points - bid3

    print()
    print("The river: ")
    print(river1, river2, river3, river4, river5)
    print()
    print("Here are your two cards: ")
    print(card1, card2)
    print()

    print("Their hand:")
    for i in ophand:
        print(i, end="   ")
    print()
    print("Your hand:")
    for i in hand:
        print(i, end="   ")
    print()
    print()

    if bid1 < 100 or bid2 < 100 or bid3 < 100:
        print(f"Your folded. You lost {bid1 + bid2 + bid3} points.")
    elif best_hand(hand) > best_hand(ophand):
        points = points + 2 * (bid1 + bid2 + bid3)
        print(f"You won that hand! You won {bid1 + bid2 + bid3} points.")
    elif best_hand(hand) == best_hand(ophand):
        points = points + (bid1 + bid2 + bid3)
        print(f"You tied the computer on that hand. No points were gained or lost.")
    else:
        print(f"You lost that hand. You lost {bid1 + bid2 + bid3} points.")
    print(f"Your total points right now: {points}")


    if points >= 10000:
        print("Great Job! You won!! ")
        wins += 1

    if points <= 0:
        print("Better luck next time. You lost, but we'll reset your points. Try again! ")
        losses += 1

    with open(filename, "w") as file:
        json.dump({
            "points": points,
            "wins": wins,
            "losses": losses
        }, file)

    if points >= 10000 or points <= 0:
        with open(filename, "w") as file:
            json.dump({
                "points": 5000,
                "wins": wins,
                "losses": losses
            }, file)

    if best_hand(hand) == 0:
        hname = "High Card"
    elif best_hand(hand) == 1:
        hname = "One Pair"
    elif best_hand(hand) == 2:
        hname = "Two Pair"
    elif best_hand(hand) == 3:
        hname = "Three of a kind"
    elif best_hand(hand) == 4:
        hname = "Straight"
    elif best_hand(hand) == 5:
        hname = "Flush"
    elif best_hand(hand) == 6:
        hname = "Full House"
    elif best_hand(hand) == 7:
        hname = "Four of a Kind"
    elif best_hand(hand) == 8:
        hname = "Straight Flush"

    if best_hand(ophand) == 0:
        ohname = "High Card"
    elif best_hand(ophand) == 1:
        ohname = "One Pair"
    elif best_hand(ophand) == 2:
        ohname = "Two Pair"
    elif best_hand(ophand) == 3:
        ohname = "Three of a kind"
    elif best_hand(ophand) == 4:
        ohname = "Straight"
    elif best_hand(ophand) == 5:
        ohname = "Flush"
    elif best_hand(ophand) == 6:
        ohname = "Full House"
    elif best_hand(ophand) == 7:
        ohname = "Four of a Kind"
    elif best_hand(ophand) == 8:
        ohname = "Straight Flush"

    print()
    print(f"Your hand: {hname}")
    print(f"Their hand: {ohname}")
    print()
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    print()
    again = input("Ready to play again? ")



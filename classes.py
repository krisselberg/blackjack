from random import shuffle


class Card:
    rank_to_value_map = {
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "10": 10,
        "Jack": 10,
        "Queen": 10,
        "King": 10,
        "Ace": 11,
    }

    def __init__(self, suit, rank):
        self.rank = rank
        self.value = self.rank_to_value_map[rank]
        self.suit = suit

    def __repr__(self):
        return self.rank + " of " + self.suit


class Deck:
    def __init__(self):
        self.cards = []
        self.build()
        shuffle(self.cards)  # shuffles deck of cards

    def build(self):
        # We assume that the dealer uses 6 decks of cards
        NUMBER_OF_DECKS = 6
        possible_suits = ["Hearts", "Spades", "Clubs", "Diamonds"]
        possible_ranks = [
            "Ace",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "Jack",
            "Queen",
            "King",
        ]
        for _ in range(NUMBER_OF_DECKS):
            for suit in possible_suits:
                for rank in possible_ranks:
                    card = Card(suit, rank)
                    self.cards.append(card)

    def draw_card(self):
        return self.cards.pop()


class Hand:
    def __init__(self, owner, bet, is_partially_hidden=False, is_ace_split_hand=False):
        self.cards = []
        self.owner = owner
        self.bet = bet
        self.is_partially_hidden = is_partially_hidden
        self.is_ace_split_hand = is_ace_split_hand  # helps check for corner case of letting player take action on a split hand with aces

    def hit(self, deck):
        self.cards.append(deck.draw_card())

    def get_value(self):
        number_of_aces = 0
        hand_value = 0

        for card in self.cards:
            if card.rank == "Ace":
                number_of_aces += 1
            hand_value += card.value

        while number_of_aces > 0 and hand_value > 21:
            hand_value -= 10
            number_of_aces -= 1

        return hand_value

    def show(self):
        visible_hand = []
        for card in self.cards:
            if self.is_partially_hidden and not visible_hand:
                visible_hand.append("?")
                continue
            visible_hand.append(card)
        hand_string = ", ".join(str(card) for card in visible_hand)
        print("{}'s hand: {}".format(self.owner, hand_string))

    def is_blackjack(self):
        if len(self.cards) == 2 and self.get_value() == 21:
            return True
        return False


class Player:
    def __init__(self, name):
        self.hands = []
        self.name = name
        self.balance = 1000
        self.bet = 0

    def show_balance(self):
        print("{}'s Current Balance: {}".format(self.name, self.balance))

    def deal_hand(self, deck, is_partially_hidden=False):
        hand = Hand(self.name, self.bet, is_partially_hidden)
        hand.hit(deck)
        hand.hit(deck)
        self.hands.append(hand)

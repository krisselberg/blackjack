from time import sleep
from math import floor
from classes import Deck, Hand, Player


def get_number_of_players():
    MIN_NUMBER_OF_PLAYERS = 1
    MAX_NUMBER_OF_PLAYERS = 7
    while True:
        try:
            number_of_players = int(input("How many players are there? "))
        except Exception:
            print("Please enter a valid number of players.")
            continue
        if (
            number_of_players < MIN_NUMBER_OF_PLAYERS
            or number_of_players > MAX_NUMBER_OF_PLAYERS
        ):
            print(
                "Number of players {} out of range (1-7). Please enter a valid number of players.".format(
                    number_of_players
                )
            )
            continue
        return number_of_players


def get_player_name():
    while True:
        player_name = input("What is your name? ")
        if len(player_name) > 15:
            print("Please use a shorter name (less than 16 characters)")
            continue
        return player_name


# set_player_bet receives an bet amount input from the current player, decrements player.balance
# by that bet amount, and updates player.bet
def set_player_bet(player):
    MIN_BET_AMOUNT = 2
    MAX_BET_AMOUNT = min(500, player.balance)
    while True:
        try:
            bet_amount = int(
                input("\nHow much would you like to bet? (Must be a whole number) ")
            )
        except Exception:
            print("Please enter a valid bet amount.")
            continue
        if bet_amount < MIN_BET_AMOUNT or bet_amount > MAX_BET_AMOUNT:
            print(
                "Invalid bet {}. Please enter a bet in the range of [{}, {}]".format(
                    bet_amount, min(MIN_BET_AMOUNT, MAX_BET_AMOUNT)
                )
            )
            continue
        player.balance -= bet_amount
        player.bet = bet_amount
        break


def can_double_down(player_hand, player):
    DOUBLE_DOWN_POSSIBLE_HAND_VALUES = [9, 10, 11]
    if (
        len(player_hand.cards) == 2
        and player_hand.get_value() in DOUBLE_DOWN_POSSIBLE_HAND_VALUES
        and player.balance >= player_hand.bet
    ):
        return True
    return False


def can_pair_split(player_hand, player):
    if (
        len(player_hand.cards) == 2
        and player_hand.cards[0].rank == player_hand.cards[1].rank
        and player.balance >= player_hand.bet
    ):
        return True
    return False


# doubledown decrements the player's balance by the previous bet amount and adds a card to
# the player's hand
def doubledown(player, player_hand, deck):
    player.balance -= player_hand.bet
    player_hand.bet *= 2
    player_hand.hit(deck)
    print(
        "You have been given a card face down that will be revealed at the end of the round.\n"
    )
    print("-----------------\n")
    sleep(2)


# pairsplit decrements the player's balance by the previous bet amount, splits their current hand into two hands,
# and prompts the player to play both hands. It is assumed that a player may split or double down as many times
# as they wish.
def pairsplit(player, player_hand, dealer, deck):
    player.balance -= player_hand.bet
    split_hand = Hand(player.name, player_hand.bet)
    split_hand.cards.append(player_hand.cards.pop())
    player.hands.append(split_hand)

    if player_hand.cards[0].rank == "Ace":
        player_hand.cards.append(deck.draw_card())
        split_hand.cards.append(deck.draw_card())
        split_hand.is_ace_split_hand = (
            True  # fixes corner case of allowing player to take action on split hand
        )

        print("You have been given two cards face down (one for each split hand).\n")
        print("-----------------\n")
        sleep(2)
        return

    get_player_action(player, player_hand, dealer, deck)


def print_player_turn_info(player, player_hand, dealer):
    dealer.hands[0].show()
    print()
    player.show_balance()
    player_hand.show()


def get_player_action(player, player_hand, dealer, deck):
    while True:
        # checks for corner case of letting player take action on a split hand with aces
        if player_hand.is_ace_split_hand:
            break

        print_player_turn_info(player, player_hand, dealer)

        if player_hand.is_blackjack():
            print("\nBlackjack!")
            print("-----------------\n")
            sleep(2)
            break

        possible_player_actions = ["h", "s"]

        if can_double_down(player_hand, player):
            player_action = input(
                "\nWould you like to hit, stand, or double down? (Type 'h' for hit, 's' for stand, or 'd' for double down) "
            )
            possible_player_actions.append("d")
        elif can_pair_split(player_hand, player):
            player_action = input(
                "\nWould you like to hit, stand, or pair split? (Type 'h' for hit, 's' for stand, or 'p' for pair split) "
            )
            possible_player_actions.append("p")
        elif can_double_down(player_hand, player) and can_pair_split(
            player_hand, player
        ):
            player_action = input(
                "\nWould you like to hit, stand, double down, or pair split? (Type 'h' for hit, 's' for stand, 'd' for double down, or 'p' for pair split) "
            )
            possible_player_actions.append("p")
            possible_player_actions.append("d")
        else:
            player_action = input(
                "\nWould you like to hit or stand? (Type 'h' for hit and 's' for stand) "
            )
        print("\n-----------------\n")
        if player_action not in possible_player_actions:
            print(
                "{} is not a valid player action. Please enter a valid player action.".format(
                    player_action
                )
            )
            continue

        if player_action == "h":
            player_hand.hit(deck)
            # check if bust
            if player_hand.get_value() > 21:
                player_hand.show()
                print("Busted...")
                sleep(2)
                print("\n-----------------\n")
                break
        elif player_action == "s":
            sleep(2)
            break
        elif player_action == "d":
            doubledown(player, player_hand, deck)
            break
        else:
            pairsplit(player, player_hand, dealer, deck)
            break


def collect_bets(players):
    for player in players:
        print("-----------------")
        player.show_balance()
        set_player_bet(player)


def deal_cards(dealer, players, deck):
    dealer.hands = []
    dealer.deal_hand(deck, is_partially_hidden=True)
    for player in players:
        player.hands = []
        player.deal_hand(deck)


def players_turn(players, dealer, deck):
    for player in players:
        for player_hand in player.hands:
            get_player_action(player, player_hand, dealer, deck)


# dealer_turn shows the dealer's hand and adds cards to the dealers hand
# while its value is 16 or under
def dealer_turn(dealer, deck):
    DEALER_MIN_STAY_VAL = 17
    dealer_hand = dealer.hands[0]

    print("Dealer's Turn\n")
    print("Dealer flips over card...\n")
    dealer_hand.is_partially_hidden = False
    sleep(2)
    dealer_hand.show()
    sleep(2)

    while dealer_hand.get_value() < DEALER_MIN_STAY_VAL:
        dealer_hand.hit(deck)
        dealer_hand.show()
        sleep(2)

    print("-----------------")


# payout_bets shows each player's hand, prints the result (win/tie/loss) of the round for that player's hand,
# and prints the net payouts of each player for the round
def payout_bets(dealer_hand_value, players, round):
    BLACKJACK_MULTIPLIER = 2.5

    print("Round {} Results\n".format(round))
    player_net_payouts = []
    for player in players:
        player_round_winnings = 0
        money_put_up_by_player = 0
        for player_hand in player.hands:
            player_hand_value = player_hand.get_value()
            money_put_up_by_player += player_hand.bet

            player_has_blackjack = (
                player_hand_value == 21 and len(player_hand.cards) == 2
            )
            player_is_busted = player_hand_value > 21
            dealer_is_busted = dealer_hand_value > 21

            if player_has_blackjack:
                # a player with blackjack in a split hand does not
                # receive the blackjack multiplier payout
                is_split_hand = len(player.hands) > 1
                if is_split_hand:
                    player_round_winnings += 2 * player_hand.bet
                    player_hand.show()
                    print("{}'s split hand beat the dealer".format(player.name))
                    sleep(2)
                else:
                    player_round_winnings += floor(
                        BLACKJACK_MULTIPLIER * player_hand.bet
                    )
                    player_hand.show()
                    print("{}'s hand beat the dealer".format(player.name))
                    sleep(2)

            elif not player_is_busted:
                if dealer_is_busted:
                    player_round_winnings += 2 * player_hand.bet
                    player_hand.show()
                    print("{}'s hand beat the dealer".format(player.name))
                    sleep(2)
                else:
                    tied = player_hand_value == dealer_hand_value
                    player_won = player_hand_value > dealer_hand_value

                    if tied:
                        player_round_winnings += player_hand.bet
                        player_hand.show()
                        print("{}'s hand drew with the dealer".format(player.name))
                        sleep(2)
                    elif player_won:
                        player_round_winnings += 2 * player_hand.bet
                        player_hand.show()
                        print("{}'s hand beat the dealer".format(player.name))
                        sleep(2)
                    else:
                        player_hand.show()
                        print("{}'s hand lost to the dealer".format(player.name))
                        sleep(2)

            else:
                player_hand.show()
                print("{}'s hand busted".format(player.name))
                sleep(2)

        player.balance += player_round_winnings
        player_net_payouts.append(player_round_winnings - money_put_up_by_player)
    print("\nRound {} Net Payout".format(round))
    for player_index in range(len(players)):
        print(
            "{}: {}".format(
                players[player_index].name, player_net_payouts[player_index]
            )
        )


def reshuffle(deck):
    deck = Deck()
    return deck


# remove_players removes players that are unable to make a bet
def remove_players(players):
    player_idx = 0
    while player_idx < len(players):
        player = players[player_idx]
        if player.balance < 2:
            print("{} is out of chips".format(player.name))
            sleep(2)
            players.remove(player)
        else:
            player_idx += 1


def play_blackjack():
    print("Welcome to Command Line Blackjack!")
    print("-----------------\n")
    number_of_players = get_number_of_players()

    print("Setting up table...")
    sleep(2)
    print("\nLet's get started!\n")
    deck = Deck()
    dealer = Player("Dealer")
    players = [Player(get_player_name()) for _ in range(number_of_players)]

    playing = True
    round = 1
    while playing:
        deck = reshuffle(deck)

        print("\nRound {}".format(round))
        sleep(2)

        collect_bets(players)

        print("\nCards are being dealt...\n")
        deal_cards(dealer, players, deck)
        sleep(2)

        dealer_hand = dealer.hands[0]
        # if the dealer has blackjack, skip player actions and
        # dealer actions to immediately pay out bets
        if dealer_hand.is_blackjack():
            dealer_hand.show()
            print("The dealer has blackjack!")
            sleep(2)
        else:
            players_turn(players, dealer, deck)
            dealer_turn(dealer, deck)

        payout_bets(dealer_hand.get_value(), players, round)

        remove_players(players)
        if len(players) == 0:
            print("Game over, all players are out of chips...")
            playing = False

        round += 1


if __name__ == "__main__":
    play_blackjack()

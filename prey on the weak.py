import random
from submission_helper.bot_battle import BotBattle
from submission_helper.state import *
from submission_helper.enums import *
from typing import Optional

game_info: Optional[GameInfo] = None
bot_battle = BotBattle()

pID = None


def get_next_alive_player():
    next_alive = (game_info.player_id + 1) % 5
    while game_info.players_cards_num[next_alive] == 0:
        next_alive = (next_alive + 1) % 5

    return next_alive


def move_controller(requested_move: RequestedMove):
    if requested_move == RequestedMove.PrimaryAction:
        primary_action_handler()

    elif requested_move == RequestedMove.CounterAction:
        counter_action_handler()

    elif requested_move == RequestedMove.ChallengeAction:
        challenge_action_handler()

    elif requested_move == RequestedMove.ChallengeResponse:
        challenge_response_handler()

    elif requested_move == RequestedMove.DiscardChoice:
        discard_choice_handler()

    else:
        return Exception(f"Unknown requested move: {requested_move}")


def primary_action_handler():
    urgent, almost_dead = [], []
    cards, bals = game_info.players_cards_num, game_info.balances

    for i in range(5):
        if cards[i] == 1 and i != pID:
            almost_dead.append(i)

        if cards[i] == 2 and i != pID:
            urgent.append(i)

    if game_info.balances[pID] >= 7:
        print("coup")
        if len(urgent) > 0:
            target = urgent.pop(0)
            bot_battle.play_primary_action(PrimaryAction.Coup, target)

        elif len(almost_dead) > 0:
            target = almost_dead.pop(0)
            bot_battle.play_primary_action(PrimaryAction.Coup, target)

        else:
            target = random.randint(0, 4)
            while target == pID:
                target = random.randint(0, 4)
            bot_battle.play_primary_action(PrimaryAction.Coup, target)

    elif game_info.balances[pID] >= 3 and 2 in game_info.own_cards:
        print("assassinate")

        if len(urgent) > 0:
            target = urgent.pop(0)
            bot_battle.play_primary_action(PrimaryAction.Assassinate, target)

        elif len(almost_dead) > 0:
            target = almost_dead.pop(0)
            bot_battle.play_primary_action(PrimaryAction.Assassinate, target)

        else:
            target = random.randint(0, 4)
            while target == pID:
                target = random.randint(0, 4)
            bot_battle.play_primary_action(PrimaryAction.Assassinate, target)

    else:
        print("tax")
        bot_battle.play_primary_action(PrimaryAction.ForeignAid)


def counter_action_handler():
    primary_action = game_info.history[-1][ActionType.PrimaryAction]

    if primary_action == PrimaryAction.ForeignAid:
        bot_battle.play_counter_action(CounterAction.BlockForeignAid)
    else:
        bot_battle.play_challenge_action(CounterAction.NoCounterAction)


def challenge_action_handler():
    bot_battle.play_challenge_action(ChallengeAction.NoChallenge)


def challenge_response_handler():
    cards = game_info.own_cards

    if len(cards) > 1:
        if cards[0] == 2:
            bot_battle.play_challenge_response(0)
        elif cards[1] == 2:
            bot_battle.play_challenge_response(1)
        else:
            bot_battle.play_challenge_response(0)

    else:
        bot_battle.play_challenge_response(0)


def discard_choice_handler():
    cards = game_info.own_cards
    if len(cards) > 1:
        if cards[0] == 2:
            bot_battle.play_discard_choice(1)
        elif cards[1] == 2:
            bot_battle.play_discard_choice(0)
        else:
            bot_battle.play_discard_choice(0)
    else:
        bot_battle.play_discard_choice(0)


if __name__ == "__main__":
    while True:
        game_info = bot_battle.get_game_info()
        pID = game_info.player_id
        print(game_info.player_id)
        move_controller(game_info.requested_move)

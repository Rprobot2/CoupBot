from operator import contains, indexOf
from submission_helper.bot_battle import BotBattle
from submission_helper.state import *
from submission_helper.enums import *
from typing import Optional


# Define globals
game_info: Optional[GameInfo] = None
bot_battle = BotBattle()


def get_next_alive_player() -> int:
    next_alive = (game_info.player_id + 1) % 5
    while game_info.players_cards_num[next_alive] == 0:
        next_alive = (next_alive + 1) % 5
    
    return next_alive

def get_previous_action_in_turn() -> Action:
    return list(game_info.history[-1].values())[-1]

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
        return Exception(f'Unknown requested move: {requested_move}')


def primary_action_handler():
    if game_info.balances[game_info.player_id] >= 7:
        target_player_id = get_next_alive_player()
        bot_battle.play_primary_action(PrimaryAction.Coup, target_player_id)

    elif contains(game_info.own_cards, Character.Ambassador):
        bot_battle.play_primary_action(PrimaryAction.Exchange)

    else:
        bot_battle.play_primary_action(PrimaryAction.ForeignAid)


def counter_action_handler():
    bot_battle.play_counter_action(CounterAction.NoCounterAction)


def challenge_action_handler():
    previous_action = get_previous_action_in_turn()

    # Challenge primary action
    if previous_action.action_type == ActionType.PrimaryAction:
        pass

    # Challenge counter action
    elif previous_action.action_type == ActionType.CounterAction:
        pass

    bot_battle.play_challenge_action(ChallengeAction.NoChallenge)


def challenge_response_handler():
    previous_action = get_previous_action_in_turn()

    reveal_card_index = None

    # Challenge was primary action
    if previous_action.action_type == ActionType.PrimaryAction:
        primary_action = game_info.history[-1][ActionType.PrimaryAction].action

        # If we have the card we used, lets reveal it
        if primary_action == PrimaryAction.Assassinate:
            reveal_card_index = indexOf(game_info.own_cards, Character.Assassin)
        elif primary_action == PrimaryAction.Exchange:
            reveal_card_index = indexOf(game_info.own_cards, Character.Ambassador)
        elif primary_action == PrimaryAction.Steal:
            reveal_card_index = indexOf(game_info.own_cards, Character.Captain)
        elif primary_action == PrimaryAction.Tax:
            reveal_card_index = indexOf(game_info.own_cards, Character.Duke)

    # Challenge was counter action
    elif previous_action.action_type == ActionType.CounterAction:
        counter_action = game_info.history[-1][ActionType.CounterAction].action

        # If we have the card we used, lets reveal it
        if counter_action == CounterAction.BlockAssassination:
            reveal_card_index = indexOf(game_info.own_cards, Character.Contessa)
        elif counter_action == CounterAction.BlockStealingAsAmbassador:
            reveal_card_index = indexOf(game_info.own_cards, Character.Ambassador)
        elif counter_action == CounterAction.BlockStealingAsCaptain:
            reveal_card_index = indexOf(game_info.own_cards, Character.Captain)
        elif counter_action == CounterAction.BlockForeignAid:
            reveal_card_index = indexOf(game_info.own_cards, Character.Duke)

    # If we lied, let's reveal our first card
    if reveal_card_index == None or reveal_card_index == -1:
        reveal_card_index = 0

    bot_battle.play_challenge_response(reveal_card_index)


def discard_choice_handler():
    bot_battle.play_discard_choice(0)


while True:
    game_info = bot_battle.get_game_info()
    move_controller(game_info.requested_move)

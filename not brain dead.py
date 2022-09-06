from submission_helper.bot_battle import BotBattle
from submission_helper.state import *
from submission_helper.enums import *
from typing import Counter, Optional

from operator import contains, indexOf


game_info: Optional[GameInfo] = None
pid = None
bot_battle = BotBattle()


def get_previous_action_in_turn() -> Action:
    return list(game_info.history[-1].values())[-1]


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
    coup_risk, two_lives, almost_dead = []
    bals = game_info.balances

    for i in range(len(bals)):
        if i == pid:
            continue
        if game_info.bals[i] >= 6:
            coup_risk.append(i)

        if game_info.players_cards_num[i] == 2:
            two_lives.append(i)
        elif game_info.players_cards_num[i] == 1:
            almost_dead.append(i)

    rich_and_dying = list(set(coup_risk).intersection(almost_dead))

    if len(rich_and_dying) > 0:
        target = rich_and_dying.pop(0)
        if hasAssassin() and bals[pid] >= 3:
            BotBattle.play_primary_action(PrimaryAction.Assassinate, target)
        elif hasCap():
            BotBattle.play_primary_action(PrimaryAction.Steal, target)
        else:
            BotBattle.play_primary_action(PrimaryAction.Assassinate, target)

    elif len(two_lives) > 0:
        target = two_lives.pop(0)
        if hasAssassin() and bals[pid] >= 3:
            BotBattle.play_primary_action(PrimaryAction.Assassinate, target)

        elif hasCap():
            BotBattle.play_primary_action(PrimaryAction.Steal, target)

        elif hasDuke():
            BotBattle.play_primary_action(PrimaryAction.Tax)

        else:
            BotBattle.play_primary_action(PrimaryAction.ForeignAid)

    else:
        if hasDuke():
            BotBattle.play_primary_action(PrimaryAction.Tax)

        elif hasAmb() and not hasAssassin():
            BotBattle.play_primary_action(PrimaryAction.Exchange)

        else:
            BotBattle.play_primary_action(PrimaryAction.ForeignAid)


def counter_action_handler():
    action = game_info.history[-1][ActionType.PrimaryAction]

    if action == PrimaryAction.Assassinate:
        if (
            game_info.current_primary_player in almost_dead()
            or hasCon()
            or len(game_info.own_cards) == 1
        ):
            bot_battle.play_counter_action(CounterAction.BlockAssassination)

        else:
            bot_battle.play_counter_action(CounterAction.NoCounterAction)

    elif action == PrimaryAction.Steal:
        if hasCap():
            bot_battle.play_counter_action(CounterAction.BlockStealingAsCaptain)
        elif hasAmb():
            bot_battle.play_counter_action(CounterAction.BlockStealingAsAmbassador)
        else:
            bot_battle.play_counter_action(CounterAction.NoCounterAction)

    else:
        bot_battle.play_counter_action(CounterAction.NoCounterAction)


def challenge_action_handler():
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

    if hasDuke():
        bot_battle.play_discard_choice(indexOf(game_info.own_cards, Character.Duke))

    elif hasAmb():
        bot_battle.play_discard_choice(
            indexOf(game_info.own_cards, Character.Ambassador)
        )
    elif hasCap():
        bot_battle.play_discard_choice(indexOf(game_info.own_cards, Character.Captain))
    elif hasCon():
        bot_battle.play_discard_choice(indexOf(game_info.own_cards, Character.Contessa))
    elif hasAssassin():
        bot_battle.play_discard_choice(indexOf(game_info.own_cards, Character.Assassin))
    else:
        bot_battle.play_discard_choice(0)


def hasDuke():
    return 1 in game_info.own_cards


def hasAssassin():
    return 2 in game_info.own_cards


def hasAmb():
    return 3 in game_info.own_cards


def hasCap():
    return 4 in game_info.own_cards


def hasCon():
    return 5 in game_info.own_cards


def almost_dead():
    almost_dead = []
    for i in range(len(game_info.balances)):
        if i == pid:
            continue
        elif game_info.players_cards_num[i] == 1:
            almost_dead.append(i)

    return almost_dead


if __name__ == "__main__":
    while True:
        game_info = bot_battle.get_game_info()
        pid = game_info.player_id
        print(pid)
        move_controller(game_info.requested_move)

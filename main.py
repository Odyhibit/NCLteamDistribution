# data is assumed to be in the following format
# Discord Handle,OSI,Crypto,Password,Log,Network,Forensics,Scanning,Web Apps,Enumeration
# *note if upgrading to Python 3.9 or later change type hints from List to list
import math
import os
import statistics
import sys
from os.path import exists
from typing import List
import bisect
import display
import Team
import TeamMember


def load_scores():
    score_list = []
    skip_columns = 2
    with open(scores_file, "r") as score_file:
        score_file.readline()  # this skips the column headers
        for line in score_file:
            row = line.rstrip("\n").split(",")
            score_list.append(row[skip_columns:])
        return score_list


def load_pre_selections(all_scores):
    #  Team name,Discord Handle,Team Lead
    max_team_size = 7
    teams = []
    with open(captains_file, "r") as partials:
        partials.readline()  # read headers
        for line in partials:
            row = line.rstrip("\n").split(",")
            team_name = row[0]
            captain = row[1]
            score = row_from_scores_by_name(captain, all_scores)
            if score == "Not Found":
                print(f"cannot find {captain} in {scores_file} ")
                sys.exit()
            team_member = TeamMember.TeamMember(score)
            # if this is a captain create the team else add this person to existing team
            if row[2].lower() == "true":
                teams.append(Team.Team(team_name, captain, [team_member]))
            else:
                # add this person to the right team
                for this_team in teams:
                    if this_team.name == team_name:
                        this_team.add_team_member(team_member)

    #  we need to add additional teams here if the number of teams is less than ceil(len(all_scores)/max_team_size
    required_team_count = int(math.ceil(len(all_scores) / max_team_size))
    should_add = required_team_count - len(teams)
    while should_add > 0:
        teams.append(Team.Team("Bonus Team " + str(len(teams) + 1), "TBD", []))
        should_add -= 1
    return teams


def matrix_get_row(i: int, score_list: List[List[str]]) -> List[int]:
    #  returns a single row from 2d list
    this_list = []
    for entry in score_list:
        this_list.append(int(entry[i]))
    return this_list


def row_from_scores_by_name(name, score_list):
    for row in score_list:
        if name in row:
            return row
    return ["Not Found"]


def matrix_from_lists(score_list: List[List[str]]):
    #  returns a list of discord names, and 2d list of scores. row index matches name index
    #  The 2d list of scores is used to find totals, and averages for each category
    number_of_scores = 9
    discord_names = []
    name_offset = 0
    matrix = [[0] * number_of_scores for _ in range(len(score_list))]
    for i, entry in enumerate(score_list):
        for j in range(10):
            if j > name_offset:
                this_item = int(entry[j])
                matrix[i][j - 1] = this_item
            else:
                discord_names.append(entry[j])
    return discord_names, matrix


def transpose_matrix(score_list: List[List[int]]):
    #  change columns to rows, only use the int values not the names
    return list(map(list, zip(*score_list)))


def average_scores(score_list: List[List[int]]) -> List[int]:
    return [int(statistics.mean(row)) for row in transpose_matrix(score_list)]


def total_scores(score_list: List[List[int]]) -> List[int]:
    return [sum(row) for row in transpose_matrix(score_list)]


def standard_deviation(score_list: List[List[int]]) -> List[int]:
    return [int(statistics.stdev(row)) for row in transpose_matrix(score_list)]


def already_on_team(team_roster: List[Team.Team]) -> List[str]:
    return [this_member.get_name() for this_team in team_roster for this_member in this_team.team_members]


def get_low_score_team(this_roster: List[Team.Team]) -> Team.Team:
    lowest_team = this_roster[0]
    for this_team in this_roster:
        if this_team.total < lowest_team.total:
            lowest_team = this_team
    return lowest_team


def greedy_team_selection(score_list, team_roster):
    remaining_players = [p for p in score_list if p[0] not in already_on_team(team_roster)]
    remaining_team_members = [TeamMember.TeamMember(t) for t in remaining_players]
    sorted_remaining_players = sorted(remaining_team_members, key=lambda x: x.total, reverse=True)
    while sorted_remaining_players:
        lowest_team = get_low_score_team(team_roster)
        top_player_available = sorted_remaining_players.pop(0)
        lowest_team.add_team_member(top_player_available)
        lowest_team.total = lowest_team.calculate_total()
    return sorted_remaining_players


def level_team_selection(score_list, team_roster):
    remaining_players = [p for p in score_list if p[0] not in already_on_team(team_roster)]
    remaining_team_members = [TeamMember.TeamMember(t) for t in remaining_players]
    sorted_remaining_players = sorted(remaining_team_members, key=lambda x: x.total, reverse=True)
    while sorted_remaining_players:
        lowest_team = get_low_score_team(team_roster)
        top_player_available = sorted_remaining_players.pop(0)
        lowest_team.add_team_member(top_player_available)
        lowest_team.total = lowest_team.calculate_total()
    return sorted_remaining_players


def get_random_team_members(this_roster: List[Team.Team], how_many: int):
    swapping = []
    while len(swapping) < how_many:
        print("Choose a team at random, and then get a random player")


def display_teams(full_roster):
    display.clear_screen()
    print()
    print()
    for team in full_roster:
        col_names = [team.name + "  " + str(team.total), "Captain: " + team.captain]
        col_widths = [40, 20]
        table_data = []
        for member in team.team_members:
            table_data.append([member.name, member.total])
        display.table(table_data, col_names, col_widths)
        print()
        print()
    input("press enter to return to menu  . . .")


def display_players(all_scores):
    #  separate the names from the score data
    names, score_matrix = matrix_from_lists(all_scores)

    #  totals
    totals = ["   Totals"]
    totals += total_scores(score_matrix)
    all_scores.append(totals)

    #  average
    average = ["   Average"]
    average += average_scores(score_matrix)
    all_scores.append(average)

    #  standard deviation
    deviation = ["   Deviation"]
    deviation += standard_deviation(score_matrix)
    all_scores.append(deviation)

    display.clear_screen()
    print()
    print()
    display.table(all_scores, column_names, column_widths)
    print()
    print()
    input("press enter to return to menu . . .")


def display_menu():
    display.clear_screen()
    display.ascii_wguncl_colored()
    print()
    print()
    display.main_menu()
    display.up(2)
    display.left(30)
    choice = input("Choose option > ")

    return choice


def display_team_module_score(full_roster):
    display.clear_screen()
    print()
    print()
    high_score_matrix = []
    for team in full_roster:
        highest_per_category = [team.name + " " + str(team.total)]
        for score in team.get_highest_category_score():
            highest_per_category.append(score)
        high_score_matrix.append(highest_per_category)
    display.table(high_score_matrix, column_names, column_widths)
    print()
    print()
    input("press enter to return to menu . . .")


def save_teams(this_roster):
    output = "Team name,Discord Handle,Team Lead"
    for team in this_roster:
        for member in team.get_members():
            output += team.get_name() + "," + member.get_name() + ", " + str(
                team.get_captain() == member.get_name()) + "\n"

    with open(save_file, "w") as output_file:
        output_file.write(output)
    print("The teams have been saved to ", save_file)
    input("press enter to return to menu . . .")


# Note: This returns a list of category median scores in form [category index, value]. It would be improved if it \
# returned the median % completion for each category instead of the overall median score from all players for each \
# category (since some categories have different max possible scores).
def get_weakest_categories():
    int_scores = get_int_scores()

    median_scores = []
    for i in range(1, len(int_scores[0])):
        int_scores.sort(key=lambda x: x[i])
        median_scores.append([i, int_scores[len(int_scores) // 2][i]])
    return sorted(median_scores, key=lambda x: x[1])


def get_int_scores():
    scores = load_scores()
    int_scores = []
    for score in scores:
        int_scores.append([score[0]] + [int(x) for x in score[1:]])
    for score in int_scores:
        score.append(sum(score[1:]))
    return int_scores


def category_team_selection(scores, roster, max_team_size):
    ranked_categories = get_weakest_categories()

    remaining_players = [p for p in scores if p[0] not in already_on_team(roster)]
    remaining_team_members = [TeamMember.TeamMember(t) for t in remaining_players]

    remaining_players = [p for p in get_int_scores() if p[0] not in already_on_team(roster)]

    # For each category, strengthen the weakest team, if possible.
    for category in ranked_categories[:-1]:
        if not remaining_players:
            break

        # Sort players by desc category strength, break ties with asc total strength
        remaining_players.sort(key=lambda x: x[-1])
        remaining_players.sort(key=lambda x: x[category[0]], reverse=True)

        # Sort teams by asc category strength, break ties with total max score of all categories
        roster.sort(key=lambda x: sum(x.get_highest_category_score()))
        roster = sorted(roster, key=lambda x: x.get_highest_category_score()[category[0] - 1])

        for team in roster:
            # If next player can help team, add them
            if team.get_highest_category_score()[category[0] - 1] < remaining_players[0][category[0]]:
                assigned_player = remaining_players.pop(0)
                team_member = TeamMember.TeamMember(assigned_player)
                team.add_team_member(team_member)
            else:
                break

        # Assign remaining players who can't improve any team's category maximum score using greedy_team_selection

        # greedy_team_selection() method doesn't cap team size, otherwise it could be used by the below 2 lines
        # remaining_players_strings = [[str(y) for y in x[:-1]] for x in remaining_players]
        # unassigned = greedy_team_selection(remaining_players_strings, roster)

        # Sort teams by total strength of all team members
        roster.sort(key=lambda x: x.get_total())
        remaining_players.sort(key=lambda x: x[-1], reverse=True)

        min_team_size = min([len(x.get_members()) for x in roster])
        while remaining_players and (min_team_size < max_team_size):
            top_player = remaining_players.pop(0)
            for team in roster:
                if len(team.get_members()) < max_team_size:
                    team.add_team_member(TeamMember.TeamMember(top_player))
                    roster.sort(key=lambda x: x.get_total())
                    min_team_size = min([len(x.get_members()) for x in roster])
                    break

        unassigned = remaining_players

        if unassigned:
            print('Unassigned:')
            print(unassigned)


def main():
    # load files
    next_screen = 0
    scores = load_scores()
    if exists(save_file):
        load_saved = input("Would you like to load saved teams Y/N")
        if load_saved == "Y" or load_saved == "y":
            captains_file = save_file

    roster = load_pre_selections(scores)
    been_chosen = already_on_team(roster)

    max_team_size = 7

    #  choose team selection method
    # roster_initial = greedy_team_selection(scores, roster)
    roster_initial = category_team_selection(scores, roster, max_team_size)

    while next_screen != "5":
        next_screen = display_menu()
        if next_screen == "1":
            display_players(scores)
        if next_screen == "2":
            display_teams(roster)
        if next_screen == "3":
            display_team_module_score(roster)
        if next_screen == "4":
            save_teams(roster)
    print(display.Colors.reset)


if __name__ == '__main__':
    if os.name == "nt":
        display.setup_windows_console()

    # files
    captains_file = "resources/Team_leads_and_partial_teams.csv"
    scores_file = "resources/NCL_scores.csv"
    save_file = "resources/saved_teams.csv"

    # columns
    column_names = ["discord handle", 'OSI', 'Crypto', 'Password', 'Log', 'Network', 'Forensics', 'Scanning',
                    'Web Apps', 'Enumeration']
    column_widths = [20, 9, 9, 9, 9, 9, 9, 9, 9, 9]

    main()

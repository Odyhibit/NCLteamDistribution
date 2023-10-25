import csv


def parse_score_block(discord_handle: str, score_block: str) -> []:
    return_list = []
    current = [discord_handle]
    slash_index = 0
    for category in range(9):
        slash_index = score_block.find("/", slash_index + 1)
        test_num = score_block[slash_index - 4: slash_index]
        if "%" in test_num:
            current.append(0)
        elif test_num.isspace():
            current.append(0)
        else:
            current.append(int(test_num.strip()))
    return_list.append(current)
    return return_list


data = []
with open("resources/NCL_2023_Spring_Team_signup_Responses_-_Form_Responses_1.csv", newline='',
          encoding="utf8") as csv_file:
    responses = csv.reader(csv_file)
    for i, row in enumerate(responses):
        if i:
            discord = row[4]
            scores = row[7]
            if len(row[7]) < 1:
                scores += row[10]
            data.append(parse_score_block(discord, scores))



with open("resources/parsed_output.csv", "w", encoding="utf8", newline='') as csv_out:
    output = csv.writer(csv_out, quoting=csv.QUOTE_MINIMAL)
    for line in data:
        output.writerows(line)


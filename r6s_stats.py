import asyncio
import r6sapi as api

UPLAY_EMAIL = "EMAIL"
UPLAY_PASS = "PASSWORD"

@asyncio.coroutine
def get_userdata(playername):
    auth = api.Auth(UPLAY_EMAIL, UPLAY_PASS)
    player = yield from auth.get_player(playername, api.Platforms.UPLAY)
    yield from player.check_queues()
    yield from player.get_all_operators()
    yield from player.get_rank("apac")
    
    data = {"trophy": None,
            "casual": None, 
            "rank": None}

    data["trophy"] = player.ranks["apac:-1"].rank
    data["casual"] = player.casual
    data["rank"] = player.ranked
    data["operator"] = top_operator(player.operators)
    
    return data

def top_operator(operators):
    op_details = []
    max_wr = 0
    max_kd = 0.0
    max_time = 0

    for i, op_name in enumerate(operators):
        op_details.append(
            [op_name,
             round(operators[op_name].wins / max(1,operators[op_name].losses), 4),
             round(operators[op_name].kills / max(1,operators[op_name].deaths), 4),
             operators[op_name].time_played,
             operators[op_name].statistic])
        max_wr = max(max_wr, op_details[i][1])
        max_kd = max(max_kd, op_details[i][2])
        max_time = max(max_time, op_details[i][3])
    for i, op in enumerate(op_details):
        weight_score_time = 5.0
        score = round((op[1]/max_wr) + (op[2]/max_kd) + ((op[3]/max_time) * weight_score_time), 4)
        op_details[i].append(score)
    
    return sorted(op_details, key=lambda x: x[5], reverse=True)[:3]

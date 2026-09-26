import asyncio
import os
import datetime
from Astandy import StandClient # Old version of AstandyClient (https://pypi.org/project/astandy/)
from Astandy.generated.schemes_pb2 import SearchPlayersRequest

GAME_TOKEN = "958949536a783f6a22a732f9e86172eb"
START_ID = 10000000
STATS_FILE = "account_graph.csv"

client = StandClient(GAME_TOKEN)

def save_to_file(uid, date_str):
    file_exists = os.path.isfile(STATS_FILE)
    with open(STATS_FILE, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write("ID,RegistrationDate\n")
        f.write(f"{uid},{date_str}\n")

async def get_player_date(c: StandClient, player_id: int):
    try:
        req = c._search_pl_req(SearchPlayersRequest(value=str(player_id), page=1, size=1))
        res_raw = await c._send(*req)
        r = c._search_pl_res(res_raw)
        if len(r.playerFriends) == 1:
            reg_ms = r.playerFriends[0].player.registrationDate
            dt = datetime.datetime.fromtimestamp(reg_ms / 1000.0)
            return dt.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"{player_id} {e}")
    return None

async def worker(c: StandClient):
    current_id = START_ID
    step = 50000
    last_dates = []
    while True:
        date_str = await get_player_date(c, current_id)
        if date_str:
            print(f"FOUND ID: {current_id} Date: {date_str} Step: {step}")
            save_to_file(current_id, date_str)
            current_id += step
        else:
            print(f"ID {current_id} Not Found! Try Step: 100")
            current_id += 100
            await asyncio.sleep(0.01)

        #await asyncio.sleep(0.01)

@client.OnConnect()
async def ClientConnected(c: StandClient, u):
    c._search_pl_req = c.raw.FriendsRemoteService.searchPlayers2Request
    c._search_pl_res = c.raw.FriendsRemoteService.searchPlayers2Response
    c._send = c.send_request
    
    print("Started!")
    await worker(c)

if __name__ == "__main__":
    client.start()
    client.idle()

# get_nft_meta v2 - added write_temp() method for projects that limit connections 
#   - sometimes the process stops after 100 requests or so, so it records the progress. If it
#       happens, the config json should be updated, "first_token" set to the last one recorded
#   - it's still a very manual project if requests fail. Should work better with scrapy instead of 
#       aiohttp requests (https://scrapy.org/)
# 
# Gets metadata from an NFT project
# To use it, create a json config file in the projects/config folder with the following data
#   - base_url: the url of the metadata, without the token id
#   - total_supply: the number of available tokens
#   - start_token: the number of the first token (0 or 1)
#       todo: what if some projects have the url like /001?
#   - export_file: name of the file where the metadata will be exported (in projects/exports folder)
# 
# Requirements: 
# - aiohttp https://docs.aiohttp.org/en/stable/
# - asyncio https://docs.python.org/3/library/asyncio.html

from asyncio.windows_events import NULL
import sys, getopt, aiohttp, asyncio, json, time


#################
# Get parameters
def main(argv):
    global config_file
    global concurrent_connections

    try:
        opts, args = getopt.getopt(argv, "hp:c:", ["project=", "connections="])
    except getopt.GetoptError:
        print('usage: get_nft_meta.py -p <project_config_file_name> [-c <concurrent_connections>]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('usage: get_nft_meta.py -p <project_config_file_name> [-c <concurrent_connections>]')
            sys.exit()
        elif opt in ("-p", "--project"):
            config_file = arg
        elif opt in ("-c", "--connections"):
            concurrent_connections = int(arg)



#################
# Get one requested json
async def fetch(session, url):
    global delay_requests

    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                await asyncio.sleep(0.2)
                # if(delay_requests):
                    # await asyncio.sleep(delay_per_request)
                    # delay_requests = False
                return await resp.json(content_type=None)
            elif resp.status == 429:
                write_temp()
                raise ValueError(f">>> Too many concurrent connections, try -c parameter to limit them. Failed at -- {len(tokens)} -- tokens")
            else:
                write_temp()
                print("Status", resp.status, "on token", url)
                pass
    except aiohttp.ClientConnectorError as e:
        write_temp()
        print('Connection Error', str(e))


#################
# Dump json into temp file to not lose progress
def write_temp():
    global tokens

    # Sort metadata
    if(sorting_key != "" and len(tokens) > 0):
        tokens = sorted(tokens, key=sort_by_id)

    with open(filename + '_temp.json', 'a') as outf:
        json.dump(tokens, outf)


#################
# Async request for each token
async def fetch_concurrent(tokens_ids):
    loop = asyncio.get_event_loop()
    connector = aiohttp.TCPConnector(limit_per_host=concurrent_connections)
    client = aiohttp.ClientSession(connector=connector)

    try:
        async with client as session:
            tasks = []

            for id in tokens_ids:
                token_url = base_url + str(id)
                tasks.append(loop.create_task(fetch(session, token_url)))

            for result in asyncio.as_completed(tasks):
                token = await result
                if(token is not None): 
                    tokens.append(token)
                    if(len(tokens) % 100 == 0):
                        delay_requests = True
                        print("Got", len(tokens), "tokens")
                        
    except aiohttp.ClientConnectorError as e:
        write_temp()
        print('Connection Error', str(e))



#################
# Sorts the metadata json by id of the token
# (Request async makes the initial list unsorted)
def sort_by_id(elem):
    return elem[sorting_key]

#################
# PROCESS
#################

duration = time.time()
delay_per_request = 3
config_file = ""
concurrent_connections = 50
delay_requests = False

if __name__ == "__main__":
    main(sys.argv[1:])

if(config_file == ""):
    print('usage: get_nft_meta.py -p <project_config_file>')
    sys.exit()

# Set vars
tokens = []
with open("projects/config/" + config_file + ".json", "r") as project_file:
    project = json.load(project_file)

    base_url = project['base_url']
    tokens_ids = range(int(project['first_token']), int(project['total_supply']))
    filename = 'projects/exports/' + project['export_filename']
    sorting_key = project['sorting_key']

# Invoque async requests
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(fetch_concurrent(tokens_ids))

# Sort metadata
if(sorting_key != "" and len(tokens) > 0):
    tokens = sorted(tokens, key=sort_by_id)

# Dump json into export file
with open(filename, 'w') as outf:
    json.dump(tokens, outf)

# Log duration
duration = time.time() - duration
print("[", len(tokens), "] tokens' metadata processed in >>>", duration, "seconds. \nFind the exported file in", filename)

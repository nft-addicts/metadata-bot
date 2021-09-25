# This is still a WIP -custom script for every project, but easy to translate to
# a config file or cli parameters (like asking for a list of rarity traits, the json key, etc)

#todo: sort by rarity score
#todo: get config file and get rarity traits from there

import json

filtered_tokens = []
rares = []
opensea_base_url = "https://opensea.io/assets/0xeb113c5d09bfc3a7b27a75da4432fb3484f90c6a/"

with open("projects/exports/kinesis_metadata.json", "r") as read_file:
    tokens = json.load(read_file)

for token in tokens:
    rarity_score = 0
    id = int(token["tokenID"])

    try:
        # Assign score for rare traits
        for trait in token["traits"]:
            if((trait["trait_type"] == "Halo" or trait["trait_type"] == "Rainbow" or trait["trait_type"] == "Pulsating") and trait["value"] == "True"):
                if(trait["trait_type"] == "Halo" and trait["value"] == "True"):
                    rarity_score +=1
                if(trait["trait_type"] == "Rainbow" and trait["value"] == "True"):
                    rarity_score +=1
                if(trait["trait_type"] == "Pulsating" and trait["value"] == "True"):
                    rarity_score +=1

        # Get only usable attributes
        token_metadata = {
            "id": token["tokenID"],
            "name": token["name"],
            "image": token["image"],
            "rarity_score": str(rarity_score),
            "animation_url": token["animation_url"],
            "opensea_url": opensea_base_url + token["tokenID"],
            "traits": token["traits"]
        }
        filtered_tokens.append(token_metadata)

        # Separate the rares
        if(rarity_score > 0):
            rares.append(token_metadata)

    except KeyError:
        continue

# Get only usable data into a file
with open("filtered_data_3.json", "w") as write_file:
    json.dump(filtered_tokens, write_file)

# Get only the rares
with open("rares_3.json", "w") as write_file:
    json.dump(rares, write_file)

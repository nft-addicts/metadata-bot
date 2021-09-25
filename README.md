# nft_metadata

get_nft_meta.py is the original script.

get_nft_meta_limited.py is an attempt to solve the limit on concurrent connections on some servers. I think it would be best done with scrapy.

nft_filter_data.py filters the result of one of the previous scripts, but it's still manually created.

Projects config files should be created in projects/config as a json file
Projects metadata is saved to projects/exports

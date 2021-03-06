import os
import io
import time
import argparse
import traceback
import logging
import hashlib
import requests
from PIL import Image
import flickrapi

# api key and license selection
import config
# large : longest edge = 1024
size = 'b'


def scrap(tags=None, tag_mode='all', text=None, maximum=500, output_folder="out"):
    assert(not (tags is None and text is None))
    assert(not (tags is not None and text is not None))
    assert(tag_mode in ['any', 'all'])
    assert(os.path.exists(output_folder))
    max_digits = len(str(maximum+1))

    flickr = flickrapi.FlickrAPI(config.api_key, config.api_secret)

    # https://www.flickr.com/services/api/flickr.photos.search.html
    if tags is not None:
        photos = flickr.walk(tag_mode='all', tags=tags, per_page=500, sort='relevance', license=config.license)
    else:
        photos = flickr.walk(text=text, per_page=500, sort='relevance', license=config.license)

    for index, photo in zip(range(maximum), photos):
        print(f"{index+1:0{max_digits}d}", photo.get('title'))

        # https://www.flickr.com/services/api/misc.urls.html
        url = f"https://live.staticflickr.com/{photo.get('server')}/{photo.get('id')}_{photo.get('secret')}_{size}.jpg"

        try:
            # get image
            img_data = requests.get(url).content
            img = Image.open(io.BytesIO(img_data))
            # check for corruption
            img.getdata()
            # save image
            with open(f"{output_folder}/{index+1:0{max_digits}d}_{photo.get('id')}.jpg", 'wb') as file:
                file.write(img_data)
        except Exception as e:
            logging.error(traceback.format_exc())

        # Limit QPS to 3600 / hour
        time.sleep(1.0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--text', help='search by text')
    group.add_argument('--tags', help='search by tags')
    parser.add_argument('-m', dest='maximum', required=True, help='maximum number of images to download')
    parser.add_argument('-o', dest='output', required=True, help='output folder')
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    print(args)

    if args.tags is not None:
        scrap(tags=args.tags, tag_mode='all', text=None, maximum=int(args.maximum), output_folder=args.output)
    else:
        scrap(tags=None, tag_mode='all', text=args.text, maximum=int(args.maximum), output_folder=args.output)

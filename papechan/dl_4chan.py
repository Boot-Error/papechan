import requests
import argparse
import sys
import subprocess
from tqdm import tqdm

from PIL import Image

FCHAN_THREADS = "https://a.4cdn.org/{board}/threads.json"
FCHAN_SINGLET = "https://a.4cdn.org/{board}/thread/{thread_id}.json"
FCHAN_IMG_URL = "https://i.4cdn.org/{board}/{tim}{ext}"

def safe_run(func):

    def func_wrapper(*args, **kwargs):

        try:
           return func(*args, **kwargs)

        except Exception as e:

            print(e)
            sys.exit(1)

    return func_wrapper

@safe_run
def get_all_threads_from_board(board):

    print("[+] Fetching board info on {}".format(board))
    r = requests.get(FCHAN_THREADS.format(board=board))
    if r.status_code != 200:
        print("[x] failed to fetch board info")
        sys.exit(1)

    data = r.json()

    threads = []
    for page in data:
        for thread in page['threads']:
            threads.append(thread["no"])

    return threads

@safe_run
def get_all_images_from_thread(board, thread):

    # print("[+] Fetching thread {} info from {}".format(thread, board))
    r = requests.get(FCHAN_SINGLET.format(board=board, thread_id=thread))
    if r.status_code != 200:
        print("[x] Failed to fetch thread info")
        sys.exit(1)

    data = r.json()

    images = []
    for post in data.get('posts'):
        if post.get('filename'):
            tim = post['tim']
            ext = post['ext']
            wid = post['w']
            hgt = post['h']

            url = FCHAN_IMG_URL.format(board=board, tim=tim, ext=ext)

            images.append({
                    "url": url,
                    "w": wid,
                    "h": hgt})

    return images


def filter_minsize(image):

    """ filter to check minimum resolution """

    min_w, min_h = (1920, 1080)

    w = image['w']
    h = image['h']

    return ((w >= min_w and h >= min_h) or (w >= min_h and h >= min_w))

@safe_run
def filter_images(images, filters):

    return filter(lambda im: all(
        map(lambda f: f(im), filters)), images)


def create_url_list(images):

    url_list_file = "/tmp/image_urls.txt"
    with open(url_list_file, "w") as f:
        f.write('\n'.join([img['url'] for img in images]))

    return url_list_file

def download_all_images(images, script_name, outdir, isbatch=False):

    envs = {"OUTDIR": outdir}
    if isbatch:
        fname = create_url_list(images)
        envs.setdefault("IMAGE_URLS_FILE", fname)

    subprocess.run(['./download.sh'], shell=True, env=envs)


def download(args):

    threads = get_all_threads_from_board(args.board)

    print("[+] Fetching images from all threads")
    images = []
    for t in tqdm(threads):
        images.extend(get_all_images_from_thread(args.board, t))

    print("[+] Collected {} images".format(len(images)))

    filtered_images = filter_images(images, [filter_minsize])
    download_all_images(filtered_images, args.script, args.outdir,
            isbatch=args.isbatch)


def fchan_download():

    parser = argparse.ArgumentParser(
            description="4chan-img-dl - 4chan image aggregator with smart options")

    parser.add_argument("-b", "--board", help="4chan board to download images from")
    parser.add_argument("-s", "--script", help="download script to run")
    parser.add_argument("-B", "--isbatch", action='store_true', help="sent a file with url of all images for the script to batch download")
    parser.add_argument("-O", "--outdir", help="directory to download the images")


    args = parser.parse_args()
    download(args)

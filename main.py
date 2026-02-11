import logging
import os
import time

from modules.html2mu.html2mu import convert_html_to_markdown, webpage_to_micron
from modules.nomadapi import NomadAPI
from modules.nomadapi.app import Config, create_rns_dest
from modules.nomadapi.handlers import Request, render_template

app = NomadAPI(
    Config(
        templates_dir='pages'
    )
)

@app.request('/page/index.mu')
def index(r: Request):
    return render_template('index.mu', dict())

@app.request('/page/links.mu')
def links(r: Request):
    return render_template('links.mu', dict())

def log_usage(id, url, t0):
    formatted_time = time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime())
    print(f"{formatted_time}: {id=} {url=}, {time.time() - t0:.2f}s")

    log_dir = os.getenv('LOGS_PATH', '/app/teapot/logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'usage_log.csv')

    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            f.write('timestamp,identity,url,duration\n')

    with open(log_file, 'a') as f:
        f.write(f'"{formatted_time}","{id}","{url}",{time.time() - t0:.2f}\n')


@app.request('/page/web.mu')
def web(r: Request):
    if r.has_param('url'):
        id = r.get_remote_identity() if r.remote_identity else None
        url = r.get_param('url')
        if url.startswith('http://') or url.startswith('https://'):
            pass
        else:
            url = 'https://' + url  # default to https

        t0 = time.time()
        try:
            mu = webpage_to_micron(url)
        except Exception as e:
            mu = f"error: {str(e)}"

            # Log the full stack trace for debugging
            logging.exception(f"Error processing URL {url} for identity {id}", exc_info=e)

        log_usage(id, url, t0)
        return mu
    else:
        return 'no url provided'

@app.request('/page/browser.mu')
def browser(r: Request):
    return render_template('browser.mu', dict())

if __name__ == '__main__':
    assert os.getenv("RNS_CONFIGDIR") is not None
    dst, identity = create_rns_dest(os.getenv("RNS_CONFIGDIR"), os.getenv("NODE_IDENTITY_PATH"))

    ANNOUNCE_NAME = os.getenv("ANNOUNCE_NAME", "teapot-dev")
    app.scheduler.every(10).minutes.do(
        lambda: logging.getLogger("announce").debug(
            "announce with data %s", ANNOUNCE_NAME
        )
        or dst.announce(ANNOUNCE_NAME.encode("utf-8"))
    )

    app.register_handlers(dst)
    app.run()

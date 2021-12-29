import re
import os
from flask import Flask, render_template, request
from utils import REGEX, get_youtube_extract
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def _index():
    if 'POST' in request.method:
        youtube_url = request.form.get('youtube_url')
        if re.match(REGEX, youtube_url):
            user_dict = get_youtube_extract(youtube_url)
            audio = user_dict['audio_formats']
            return render_template('result.html',
                                   audio_dict=audio,
                                   thumbnail=user_dict['thumbnail'],
                                   video_dict=user_dict['video_formats'],
                                   video_title=user_dict['title'],
                                   )

    return render_template('home.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get(
        "PORT", 5000), use_reloader=True, threaded=True)

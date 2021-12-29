
import yt_dlp


# ℹ️ See the docstring of yt_dlp.postprocessor.common.PostProcessor
class MyCustomPP(yt_dlp.postprocessor.PostProcessor):
    # ℹ️ See docstring of yt_dlp.postprocessor.common.PostProcessor.run
    def run(self, info):
        self.to_screen('Doing stuff')
        return [], info


def user_sanitize_info(info):
    user_dict = {
        'audio_formats': [],
        'video_formats': [],
        'thumbnail': info['thumbnail'],
        'duration': info['duration'],
        'title': info['title']
    }
    for formats in info['formats']:
        if 'none' in formats['video_ext'] and 'none' != formats['audio_ext']:
            user_dict['audio_formats'].append(
                {
                    'format_name': formats['format'],
                    'url': formats['url'],
                    'audio_ext': formats['audio_ext'],
                    'format_note': formats['format_note']

                }
            )
        if 'none' in formats['audio_ext'] and 'none' != formats['video_ext']:
            user_dict['video_formats'].append(
                {
                    'format_name': formats['format'],
                    'url': formats['url'],
                    'video_ext': formats['video_ext'],
                    'resolution': formats['resolution'],
                    'format_note': formats['format_note']
                }
            )
    return user_dict


def format_selector(ctx):
    """ Select the best video and the best audio that won't result in an mkv.
    This is just an example and does not handle all cases """

    # formats are already sorted worst to best
    formats = ctx.get('formats')[::-1]

    # acodec='none' means there is no audio
    best_video = next(f for f in formats
                      if f['vcodec'] != 'none' and f['acodec'] == 'none')

    # find compatible audio extension
    audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
    # vcodec='none' means there is no video
    best_audio = next(f for f in formats if (
        f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

    yield {
        # These are the minimum required fields for a merged format
        'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
        'ext': best_video['ext'],
        'requested_formats': [best_video, best_audio],
        # Must be + separated list of protocols
        'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
    }


def get_youtube_extract(url: str):
    ydl_opts = {
        'format': format_selector,
        'postprocessors': [{
            'key': 'FFmpegMetadata',
            'add_chapters': True,
            'add_metadata': True,
        }],


    }

    # Add custom headers
    yt_dlp.utils.std_headers.update({'Referer': 'https://www.google.com'})

    # ℹ️ See the public functions in yt_dlp.YoutubeDL for for other available functions.
    # Eg: "ydl.download", "ydl.download_with_info_file"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.add_post_processor(MyCustomPP())
        info = ydl.extract_info(url, download=False)
        # ℹ️ ydl.sanitize_info makes the info json-serializable
        sanitize_info = ydl.sanitize_info(info)
        # f.write(json.dumps(sanitize_info))
        user_sanitize = user_sanitize_info(sanitize_info)
        return user_sanitize


info = get_youtube_extract('https://www.youtube.com/watch?v=_XYHjf25GPc')

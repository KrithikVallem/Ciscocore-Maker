from flask import Flask, request, render_template
from urllib.parse import unquote
from string import ascii_uppercase
import time, os, random

app = Flask(__name__)


@app.route('/')
def index():
  b_a = request.args.get('b_a', '6300')
  highpass = request.args.get('highpass', '100')
  lowpass = request.args.get('lowpass', '3000')

  encoded_url = request.args.get('youtube_url', "")
  if encoded_url:
    try:
      yt_url = unquote(encoded_url)
      output_filename = generate_compressed_audio(yt_url, b_a, highpass, lowpass)
    except:
      return '<a href="/">Something went wrong :( Please try again</a>'
  else:
    yt_url = ""
    output_filename = ""

  return render_template(
    'index.html',
    youtube_url=yt_url,
    output_filename=output_filename,
    b_a=b_a,
    highpass=highpass,
    lowpass=lowpass
  )


# generates an mp3 file in the directory
# returns name of output file
def generate_compressed_audio(youtube_url, b_a, highpass, lowpass):
  webm_name = 'ifi'
  wav_name = 'output'
  output_filename = get_output_filename()

  # Kuwar's script
  # I removed the .exe after yt-dlp and ffmpeg and added -y option (overwrite=yes) to ffmpeg
  # I used Replit packages to install yt-dlp and ffmpeg
  # I added pkgs.ffmpeg_5 to the replix.nix hidden file
  # I made the output mp3 go to the static folder bc Flask prefers it that way
  
  # Update Oct 31, 2023:
  # Fixed error where yt-dlp no longer downloaded certain videos
  # https://github.com/yt-dlp/yt-dlp/issues/7811
  # Fix was upgrading yt-dlp to latest version with this command in shell:
  # poetry add yt-dlp@2023.07.06

  script = '; '.join([
    f'yt-dlp "{youtube_url}" -o "{webm_name}" --merge-output-format webm',
    f'ffmpeg -y -i "{webm_name}.webm" -map a -c:a g723_1 -ar 8000 -ac 1 -b:a {b_a} -filter:a "highpass=f={highpass}, lowpass=f={lowpass}" "{wav_name}.wav"',
    f'ffmpeg -y -i "{wav_name}.wav" -map a -q:a 9 "static/output/{output_filename}"',
    f'rm "{wav_name}.wav"',
    f'rm "{webm_name}.webm"',
  ])

  _ = os.system(script)
  
  return "output/" + output_filename


# returns output filename
# also deletes oldest files if there's too many
def get_output_filename():
  folder_path = 'static/output'
  max_files = 5
  
  # sort files by name (they are named based on timestamp of creation)
  all_output_files = sorted(os.listdir(folder_path))
  num_files_to_delete = max(0,len(all_output_files) - max_files + 1)
  oldest_files = all_output_files[:num_files_to_delete]
  for file in oldest_files:
    os.remove(f'{folder_path}/{file}')

  # name new file based on current timestamp + a random sequence to avoid
  # situation where 2 files are created at once
  timestamp = int(time.time())
  letters = ''.join(random.sample(ascii_uppercase, 5))
  return f"{timestamp}_{letters}.mp3"
    
  


app.run(host='0.0.0.0', port=81)

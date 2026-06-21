# roborock-s5-valetudo-voice-change
Guide and scripts for changing the voice on your Roborock S5 (gen2) to anything you want

This guide assumes that you've successfully installed [Valetudo](https://valetudo.cloud/) on your S5 and have the private key needed to log in to your robot using ssh. It also
assumes you are using [Cartesia](https://play.cartesia.ai/) as the text-to-speech tool. Note: You need Pro subscription to use the Instant Voice Clone feature, which
at the time of writing costs 5$ a month. This guide is written with Linux in mind and assumes you have the necessary tools installed. If you don't know how to apply
this guide to your specific environment, you should probably not be fiddling around and risking bricking your device.

[valetudo-voice-pack-generator](https://github.com/pando85/valetudo-voice-pack-generator) was the inspiration for this guide. I originally intended to use that,
but decided it was too much of a hassle to train a voice model and opted to use an existing tool (Cartesia). ```get_sounds_list.py``` is actually an almost
direct copy from that project. Other scripts have been lazily vibed with Gemini.


## 1. Clone the repo
``` 
git clone https://github.com/jesmak/roborock-s5-valetudo-voice-change.git
cd roborock-s5-valetudo-voice-change
```

## 2. Login to your robot using ssh and your private key
```
ssh -i /location/of/private/key root@ROBOT_IP
```

Figure out the location of the audio files on your robot. On my device, the location was ```/opt/rockrobo/resources/sounds/en```

## 3. Backup current audio folder and prepare the new one
```
cd /opt/rockrobo/resources/sounds
mv ./en en_bak
mkdir en
cp ./en_bak/sound* en
cp ./en_bak/di* en
```
In addition to audio files, the original folder contains ```sound.ver``` and ```sound.info```. Not sure if the robot uses these or not, but doesn't hurt to copy them back. 
Amongst the audio files there's ```di.wav``` and ```ding.wav``` that are just sound effects and should also be copied back, unless you want to replace these with your own
versions too of course.

## 4. Logout from the robot and copy the audio files to your local pc
```
exit
mkdir wav
scp -O -r -i /location/of/private/key root@ROBOT_IP:/opt/rockrobo/resources/sounds/en_bak/*.wav ./wav
rm wav/di*
```
```di.wav``` and ```ding.wav``` are removed above as faster-whisper just creates gibberish of them

## 5. Create a python virtual env and transform wav files to text
```
mkdir text
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 ./get_sounds_list.py
```

## 6. Combine the separate text files to a single JSON
```
chmod +x ./txt_to_json.sh
./txt_to_json.sh
```

## 7. Change the text content however you want
The above bash script generates a ```prompts.json``` that contains the robot's current speech patterns in text format.
Edit the file however you see fit. What I did was I uploaded the JSON file to Gemini, told it to translate the values to my language and speech style of choice, and then I just
replaced the contents of ```prompts.json``` with this output from Gemini.

## 8. Transform the new text prompts back to audio using Cartesia
First edit ```wav_generate.py``` and set your Cartesia API key, language code and the voice ID you want to use. You can use a voice you've created with Cartesia's Instant Voice
feature, or any of the pre-existing voice models.

```
python3 ./wav_generate.py
```

## 9. Remove metadata from the generated wav files
S5 is picky, so this has to be done
```
mkdir -p cleaned_wav
for f in new_wav/*.wav; do
    filename=$(basename "$f")
    ffmpeg -i "$f" -acodec pcm_s16le -ar 16000 -ac 1 -map_metadata -1 -fflags +bitexact "cleaned_wav/$filename"
done
```

## 10. Copy the cleaned audio files back to the robot
```
scp -O -r -i /location/of/private/key ./cleaned_wav/*.wav root@ROBOT_IP:/opt/rockrobo/resources/sounds/en
```

## 11. Reboot your robot
If everything was done correctly, it should now use your new audio files.

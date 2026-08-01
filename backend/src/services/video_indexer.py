import os
import time
import logging

import requests
import yt_dlp

from azure.identity import DefaultAzureCredential

logger = logging.getLogger("video-indexer")


from dotenv import load_dotenv
load_dotenv(override=True)

class VideoIndexerService:

    def __init__(self):
        self.account_id = os.getenv("AZURE_VI_ACCOUNT_ID")
        self.location = os.getenv("AZURE_VI_LOCATION")
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.account_name = os.getenv("AZURE_VI_NAME", "troy-vid-indexer")
        self.credential = DefaultAzureCredential()

    def get_access_token(self):
        '''
        Generates an ARM access token
        '''
        try :
            token_object = self.credential.get_token("https://management.azure.com/.default")
            return token_object.token
        except Exception as e:
            logger.error(f"Failed to get Azure ARM token :{e}")
            raise

    def get_account_token(self, arm_access_token):
        '''
        Exchanges and gets the token to get access of video indexer account.
        '''

        url = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}"
            f"/resourceGroups/{self.resource_group}"
            f"/providers/Microsoft.VideoIndexer/accounts/{self.account_name}"
            f"/generateAccessToken?api-version=2025-04-01"
        )
        #2024-01-01

        headers = {"Authorization" : f"Bearer {arm_access_token}"}
        payload = {"permissionType" : "Contributor", "scope" : "Account"}
        response = requests.post(url, headers = headers, json = payload)

        if response.status_code != 200:
            raise Exception(f"Failed to get VI Account token :  {response.text}")
        return response.json().get("accessToken")

            
    def download_youtube_video(self, url : str, output_path="temp_video.mp4") -> str:
        logger.info(f"Downloadiong yt video : {url}")

        ydlp_opts = {
            "format" : 'best',
            "outtmpl" : output_path,
            'quiet' : False,
            'no_warnings' : False,
            'extractor_args' : {'youtube' : {'player_client' : ['android', 'web']}},
            "http_headers" : {
                'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36'
            }
        }

        # If deployed on cloud (Render/AWS), YouTube blocks data center IPs. 
        # Using an exported cookies.txt bypasses this.
        if os.path.exists("cookies.txt"):
            logger.info("Found cookies.txt in root directory! Injecting into yt-dlp.")
            ydlp_opts['cookiefile'] = "cookies.txt"
        else:
            logger.warning("No cookies.txt file found. yt-dlp may fail with a bot detection error on cloud servers.")

        try :
            with yt_dlp.YoutubeDL(ydlp_opts) as ydl:
                ydl.download([url])
            logger.info("Video Download complete")
            return output_path
        except Exception as e:
            raise Exception(f"YT video download failed : {e}")

        
    def upload_video(self, video_path : str, video_name : str) -> str:
        arm_token = self.get_access_token()
        vi_token = self.get_account_token(arm_access_token=arm_token)

        api_url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos"

        params = {
            "accessToken" : vi_token,
            "name" : video_name,
            "privacy" : "Private",
            "indexingPreset":"Default"
        }

        logger.info(f"Uploading the file {video_path} to Azureee...")

        with open(video_path, 'rb') as video_file:
            files = {'file' : video_file}
            response = requests.post(api_url, params=params, files=files)
        if(response.status_code !=200):
            raise Exception(f"Azure Upload Failed : {response.text}")
        return response.json().get('id')

    def wait_for_processing(self, video_id) -> str:
        logger.info(f"Waiting for the video to proeceess : {video_id}")

        while True:
            arm_token = self.get_access_token()
            vi_token = self.get_account_token(arm_token)

            url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos/{video_id}/Index"

            params = {"accessToken" : vi_token}
            response = requests.get(url, params=params)
            data = response.json()

            state = data.get('state')

            if state == "Processed":
                return data
            elif state == "Failed":
                raise Exception("Video Indexing Failed in Azure")
            elif state == "Quarantined":
                raise Exception("Video Quarantined - Copyright or policy Failure")

            logger.info(f"waiting for  30 seconds ..... Status {state}")
            time.sleep(30)

    def extract_data(self, vi_json) -> str:
        transcript_lines = []
        for v in vi_json.get("videos", []):
            for insight in v.get("insights", {}).get("transcript", []):
                transcript_lines.append(insight.get("text"))

        ocr_lines = []

        for v in vi_json.get("videos", []):
            for insight in v.get("insights", {}).get("ocr", []):
                ocr_lines.append(insight.get("text"))

        
        return {
            "transcript" : " ".join(transcript_lines),
            "ocr_text" : ocr_lines,
            "video_metadata" : {
                "duration" : vi_json.get("summarizedInsights", {}).get("duration", 0),
                "platform" : "youtube"
            }
        }
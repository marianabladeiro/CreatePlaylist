import json
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import requests
import youtube_dl

from spotify import spotify_token, spotify_user_id


"""
-> Login youtube
-> grab liked videos
-> create Spotify playlist
-> add liked songs into the playlist
"""


class CreatePlaylist:

	def __init__(self):
		self.youtube_client = self.youtubeLogIn()
		self.all_song_info = {}

	#this function logs into youtube, using the API data youtube
	def youtubeLogIn(self):
		os.environ["OUATHLIB_INSECURE_TRANSPORT"] = "1" #disable in production
		api_name = "youtube"
		api_version = "v3"
		client_file = "client_secret.json"

		#create an API client
		scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
		flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_file, scopes)
		credentials = flow.run_console()

		youtube_client = googleapiclient.discovery.build(api_name, api_version, credentials=credentials)
		return youtube_client


	#gets liked videos, using a dictionary to gather song info
	def getLikedVideos(self):
		request = self.youtube_client.videos().list(part = "snippet, contentDetails, statistics", myRating="like")
		answer = request.execute()

		#some important info of the videos
		for item in answer["items"]:
			v_title = item["snippet"]["title"]
			youtube_Url = "https://www.youtube.com/watch?v={}".format(item["id"])

			video = youtube_dl.YoutubeDL({}).extract_info(youtube_Url, download=False)
			song_name = video["track"]
			singer = video["artist"]

			#save info and skip if missing
			if song_name is not None and singer is not None:
				self.all_song_info[v_title] = {
					"youtube_Url": youtube_Url,
					"song_name": song_name,
					"artist": singer,
					"spotify_uri": self.getSpotify(song_name, singer)

				}



	#create a new Playlist on Spotify, returns the playlist id
	def createPlaylist(self):
		request = json.dumps({
				"name": "Liked Videos - Youtube",
				"description": "Liked Videos",
				"public": True
			})

		query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)
		answer = requests.post(query, data = request, headers = { 
														"Content-Type": "application/json",
														"Authorization": "Bearer {}".format(spotify_token)

			})
		answer_json = response.json()
		return answer_json["id"]

	#this function searchs for the song
	def getSpotify(self, song_name, singer):
		query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(song_name, artist)
		response = requests.get(query, headers= {
										"Content-Type": "application/json",
										"Authorization": "Bearer {}".format(spotify_token)
									}
		)

		answer_json = response.json()
		songs = answer_json["tracks"]["items"]

		uri = songs[0]["uri"] #first song
		return uri

		
	# add the liked songs into a new playlist
	def addSong(self):
		#add to dic
		self.getLikedVideos()

		#collect uri
		uris = [info["spotify_uri"]
			for song, info in self.all_song_info.items()]

		#new playlist
		playlist_id = self.createPlaylist()

		#add songs to playlist
		request_data = json.dumps(uris)

		query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            playlist_id)

		answer = request.post(query, data = request_data, headers= {
																"Content-Type": "application/json",
																"Authorization": "Bearer {}".format(spotify_token)
			}
		)


		answer_json = response.json()
		return answer_json


if __name__ == '__main__':
	cp = CreatePlaylist()
	cp.addSong()


    	



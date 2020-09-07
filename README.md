# SpotifyPlaylistDeconstructor

Takes a spotify playlist via url or key and converts it to another service.  

For desired services you will need to get access to that particular services api for oauth keys.  For spotify copy your client id and secret key to config.cfg; For youtube you will need to download your oath2 json file and direct clients_secrets_file to it in main.py

Currently only Youtube is implemented and there is an api quota limiting basic users to 66 songs a day.  This is reflected in the code and this program will only copy the first 66 songs in the playlist.

Apple music integration is dependent on when Apple developer program stops being so faulty and actually processes my account

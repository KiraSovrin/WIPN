# Spotify Now Playing App

A simple app that displays the currently playing song on Spotify, along with album art and playback controls.

## Requirements

- Python 3.x
- Spotipy
- dotenv
- requests

## Setup

To set up your environment, you need to create a `.env` file with your Spotify API credentials. Follow these steps:

### 1. Clone the repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/KiraSovrin/WIPN.git
```

### 2. Create a `.env` file

Create a `.env` file in the root of the project directory (where `main.py` is located). This file will store your sensitive API credentials.

#### 2.1 Obtain Your Spotify API Credentials

To get your credentials, follow these steps:

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. If you don't already have a Spotify Developer account, sign up for one.
3. Once logged in, click **Create an App**.
4. Fill out the necessary fields (App name, description, etc.).
5. After creating the app, you will be given a **Client ID** and **Client Secret**. These are the credentials you'll use to authenticate with the Spotify API.
6. For the **Redirect URI**, you'll need to specify a valid URI that Spotify can redirect to after authentication. For local development, you can use `http://localhost:8888/callback` (you can change this to something else later if needed).

   To add a Redirect URI:
   - Go to the **Edit Settings** of your app in the Spotify Developer Dashboard.
   - Add `http://localhost:8888/callback` (or another URI you plan to use) under **Redirect URIs**.

#### 2.2 Add the Credentials to the `.env` File

Create a `.env` file with the following content:

```ini
SPOTIPY_CLIENT_ID=<your-client-id>
SPOTIPY_CLIENT_SECRET=<your-client-secret>
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
```


# sirius - An alternative backend for your Little Printer

![CloudBerg Little Printer](https://i.vimeocdn.com/video/222115839_1280x720.jpg)

This repository is a fork of [genmon/sirius](https://github.com/genmon/sirius).

### Interesting links

Before everything else, you might want to understand how to update your CloudBerg Little Printer to use it with Sirius. It seems that before you just had to give your CloudBerg Bridge MAC address and someone pushed the update on your device. Now, it appears that the only option to update your CloudBerg Bridge to use it with Sirius is to root your device. The following links might help you :

  * [Updating the Bridge](https://github.com/genmon/sirius/wiki/Updating-the-Bridge)
  * [Rooting Your BERG Cloud Bridge](http://pipt.github.io/2013/04/15/rooting-berg-cloud-bridge.html)
  * [Getting Little Printer online](http://joerick.me/hardware/2017/03/09/little-printer)
  * [Installing Sirius on Mac / Linux / Raspberry Pi](https://gist.github.com/hako/f8944cfa7b8fb8115f6d)

### Installation

Install and run Sirius on macOS:

```
git clone https://github.com/cubeghost/sirius
cd sirius

cp sample.env .env

virtualenv env
pip install -r requirements.txt

wget https://chromedriver.storage.googleapis.com/2.42/chromedriver_mac64.zip
unzip chromedriver_mac64.zip
mv chromedriver /usr/local/bin

./manage.py db upgrade head

gunicorn -k flask_sockets.worker manage:app -b 0.0.0.0:5002 -w 1
```
~~or use Docker Compose, just type:~~  i haven't updated this yet, sorry

```
docker-compose up
```

Navigate browser to http://127.0.0.1:5002/

You should configure your BergCloud Bridge to point to your Sirius instance.

If you want, you can create a systemd service, feel free to update this skeleton to fit your needs:

```
[Unit]
Description=Sirius, webapp for Little Printer

[Service]
WorkingDirectory=/home/berg/sirius
ExecStart=/home/berg/.local/bin/gunicorn -k flask_sockets.worker manage:app -b 0.0.0.0:5002 -w 1
User=berg

[Install]
WantedBy=multi-user.target
```

### Using the external API

If you want to print messages from your application, you can use the external API.


#### With curl

```bash
curl \
  --data '{"message": "<h1>hello friend!</h1>"}' \
  http://127.0.0.1:5000/external_api/v1/printer/1/print_html?api_key=<key>
```


### Environment variables

The server can be configured with the following variables:

```
TWITTER_CONSUMER_KEY=...
TWITTER_CONSUMER_SECRET=...
FLASK_CONFIG=...
SECRET_KEY=...
```

## Sirius Architecture

### Layers

The design is somewhat stratified: each layer only talks to the one
below and above. The ugliest bits are how database and protocol loop
interact.

```
UI / database
----------------------------
protocol_loop / send_message
----------------------------
encoders / decoders
----------------------------
websockets
----------------------------
```

### Information flow (websockets)

The entry point for the bridge is in `sirius.web.webapp`. Each new
websocket connection spawns a gevent thread (specified by running the
flask_sockets gunicorn worker) which runs
`sirius.protocol.protocol_loop.accept` immediately. `accept` registers
the websocket/bridge_address mapping in a global dictionary; it then
loops forever, decoding messages as they come in.


### Claim codes

Devices are associated with an account when a user enters a "claim
code". This claim code contains a "hardware-xor" which is derived via
a lossy 3-byte hash from the device address. The XOR-code for a device
is always the same even though the address changes!

The claim codes are meant to be used "timely", i.e. within a short
window of the printer reset. If there are multiple, conflicting claim
codes we always pick the most recently created code.

We are also deriving this hardware xor when a device calls home with
an "encryption_key_required". In that case we connect the device to
the claim code via the hardware-xor and send back the correct
encryption key.

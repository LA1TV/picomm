# PiComms
Digital Audio over IP comms system

## Developer Setup

Requires Pipenv for python deps
`cd rasbpi && pipenv install`

Running the Client
`cd rasbpi && pipenv run python3 src/app.py`

##Topic "comms/connect"
Send a json payload with the host and port to retrive audio from.
`{ "host": "0.0.0.0", "port": "5001" }`
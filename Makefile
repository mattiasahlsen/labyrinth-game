.PONY: client server

run:
	python client/client.py

run-server:
	python server/server.py
client3:
	python3 client/client.py
server3:
	python3 server/server.py "server"
backup3:
	python3 server/server.py "backup"

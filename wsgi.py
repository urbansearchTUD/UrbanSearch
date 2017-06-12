from urbansearch.server.main import Server

if __name__ == "__main__":
    s = Server(run=False)
    s.app.run()

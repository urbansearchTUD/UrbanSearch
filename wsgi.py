from urbansearch.server.main import Server

s = Server(run=False)
app = s.app

if __name__ == "__main__":
    app.run()

from src import init_flask, run_config, debug

app = init_flask()

if __name__ == '__main__':
    if debug:
        app.run(**run_config)
    else:
        from waitress import serve
        serve(app, **run_config)

def get_logs():
    log_file_path = "logs/log"
    try:
        with open(log_file_path, "r") as log_file:
            log_contents = log_file.read()
        return log_contents, 200, {'Content-Type': 'text/plain'}
    except FileNotFoundError:
        return {"error": "Log file not found"}, 404
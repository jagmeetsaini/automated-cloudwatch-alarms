import logging

def configure_logger(file_name, logs_level):
    log_level = getattr(logging, logs_level.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError(f"Invalid logging level: {logs_level}")

    logger = logging.getLogger(file_name)
    logger.setLevel(log_level)
    
    # Remove any existing handlers to avoid duplicate logging
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
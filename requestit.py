import argparse
import logging
import requests
import time

LOG_FORMAT = "[%(levelname)s] %(message)s"
LOG_DEBUG_FORMAT = "[%(threadName)s-%(filename)s-%(funcName)s-%(lineno)s | %(levelname)s] %(message)s"

log = logging.getLogger(__name__)

def save_progress(x, y, **kwargs):

    with open(kwargs['progress'],'w') as fd:
        progress_line = f"{x} {y}"
        log.debug(f"Saving {x} {y}")
        fd.write(progress_line)


def run(args, **kwargs):
    progress_line = ''
    with open(kwargs['progress'],'r') as fd:
        progress_line = fd.read().strip()  

    if(len(progress_line) == 0):
        progress_line = "0 0"

    current_x = int(progress_line.split(' ')[0])
    current_y = int(progress_line.split(' ')[1])
    progress_set = False
    finished = False

    try:
        fail_message = "Sorry, the page you requested does not exist!"
        target_url = "https://account.venmo.com/u/"

        first_list = kwargs['firstnames'].readlines()
        last_list = kwargs['lastnames'].readlines()

        i = 0
        log.info(f"Starting at {current_x}:{current_y}")

        for x in range(current_x, len(first_list)):
            for y in range(current_y, len(last_list)):
                

                if finished:
                    log.info("Already iteratred through all elements")
                    return
                current_x = x
                current_y = y

                f = first_list[x]
                l = last_list[y]

                cur_name = f.strip().lower() + l.strip().lower()
                full_url = target_url + cur_name
                headers = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36',
                }


                r = requests.get(full_url,headers=headers)

                if(r.status_code != 200):
                    log.debug(f"Account does not exist: ignoring {cur_name}")
                    log.error(r.status_code)
                    log.debug(r.text[0:50])
                    log.debug(full_url)
                else:
                    kwargs["validaccounts"].write(cur_name + "\n")
                        
                time.sleep(0.2)
                i += 1
                if not i % 1000:
                    log.info(i)

                if y == len(last_list) - 1:
                    current_y = 0
                
                if x == len(first_list) - 1:
                    finished = True

    except KeyboardInterrupt as e:
        save_progress(current_x, current_y, **kwargs)
        log.info("Saving progress...")

    except Exception as e:
        save_progress(current_x, current_y, **kwargs)
        log.error("Unknown exception - saving progress")
        log.exception(e)
    

class SymbolFormatter(logging.Formatter):
    symbols = ["x", "!", "-", "+", "DBG"]
    
    def format(self, record):
        symbol_record = logging.makeLogRecord(vars(record))
		
        for index, symbol in enumerate(self.symbols):
            if record.levelno >= (len(self.symbols) - index) * 10:
                symbol_record.levelname = symbol
                break
			
        return super(SymbolFormatter, self).format(symbol_record)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--firstnames", type=argparse.FileType('r'), default="", help="File containing first names")
    parser.add_argument("--lastnames", type=argparse.FileType('r'), default="", help="File containing last names")
    parser.add_argument("--validaccounts", type=argparse.FileType('a+'), default="0.0.0.0", help="Right endpoint host")
    parser.add_argument("--progress", type=str, default="", help="File containing the stopping x and y values")
    parser.add_argument("--debug", action="store_true", default=False, help="Show debug information")
    parser.add_argument("--logging", type=str, help="Log file")
    args = parser.parse_args()
    kwargs = vars(args)

    log.setLevel(logging.DEBUG)
	
    formatter = logging.Formatter(LOG_DEBUG_FORMAT) if args.debug else SymbolFormatter(LOG_FORMAT)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if args.debug else logging.INFO)
    handler.setFormatter(formatter)
    log.addHandler(handler)
	
    if args.logging:
        file_handler = logging.FileHandler(args.logging)
        file_handler.setLevel(logging.DEBUG if args.debug else logging.INFO)
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)

    try:
        run(args, **kwargs)
    except KeyboardInterrupt:
        log.debug("keyboard interrupt")
    except AssertionError as e:
        log.error(e)
    except Exception as e:
        log.debug("Unknown exception")
        log.exception(e)
		

if __name__ == "__main__":
    main()
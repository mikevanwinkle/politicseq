from termcolor import colored, cprint

def info(msg):
  cprint(msg, 'yellow')
  
def success(msg):
  cprint(msg, 'green')
  
def error(msg):
  cprint(msg, 'grey', 'on_red')
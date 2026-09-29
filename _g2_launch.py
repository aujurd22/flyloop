import os, sys
os.environ['FLYLOOP_PORT']='49174'
os.environ['FLYLOOP_PORT_MATCHED']='49175'
os.environ['FLYLOOP_PORT_EPI']='49176'
os.environ['FLYLOOP_NOISE_EPS']='0.25'
os.environ['FLYLOOP_ARMS']='FULL,MATCHED,EPISODIC'
os.environ['FLYLOOP_MATCH_MIN_FRAC']='0.6'
os.environ['FLYLOOP_BOOK_CAP']='13'
os.environ['FLYLOOP_BOOK_MODE']='perrule'
os.environ['FLYLOOP_PREDSET']='RSI0G2'
os.chdir(r'D:\djr82\flyloop')
sys.argv = ['supervisor', '--run-dir', r'D:\djr82\flyloop\runs\rsi0_g2_20260930_0029', '--duration-h', '2.5']
from flyloop.supervisor import main
main()
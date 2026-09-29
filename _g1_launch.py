import os, sys
os.environ['FLYLOOP_NOISE_EPS']='0.25'
os.environ['FLYLOOP_ARMS']='FULL,MATCHED,EPISODIC'
os.environ['FLYLOOP_MATCH_MIN_FRAC']='0.6'
os.environ['FLYLOOP_BOOK_CAP']='13'
os.environ['FLYLOOP_PREDSET']='RSI0'
os.chdir(r'D:\djr82\flyloop')
sys.argv = ['supervisor', '--run-dir', r'D:\djr82\flyloop\runs\rsi0_g1_20260929_1259', '--duration-h', '2']
from flyloop.supervisor import main
main()

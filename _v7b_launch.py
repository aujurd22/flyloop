import os, sys
os.environ['FLYLOOP_WAVE_AMP']='2'
os.environ['FLYLOOP_ARMS']='FULL,MATCHED,EPISODIC'
os.chdir(r'D:\djr82\flyloop')
sys.argv = ['supervisor', '--run-dir', r'D:\djr82\flyloop\runs\v7b_20260929_0447', '--duration-h', '2']
from flyloop.supervisor import main
main()

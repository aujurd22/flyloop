import os, sys
os.environ['FLYLOOP_PORT']='60668'
os.environ['FLYLOOP_PORT_MATCHED']='60669'
os.environ['FLYLOOP_PORT_EPI']='60671'
os.environ['FLYLOOP_NOISE_EPS']='0.25'
os.environ['FLYLOOP_ARMS']='FULL,FULL-RAW,EPISODIC'
os.environ['FLYLOOP_PREDSET']='V7C'
os.chdir(r'D:\djr82\flyloop')
sys.argv = ['supervisor', '--run-dir', r'D:\djr82\flyloop\runs\v7c_20260929_1940', '--duration-h', '2.5']
from flyloop.supervisor import main
main()
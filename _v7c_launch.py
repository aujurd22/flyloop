import os, sys
os.environ['FLYLOOP_PORT']='49177'
os.environ['FLYLOOP_PORT_MATCHED']='49178'
os.environ['FLYLOOP_PORT_EPI']='49179'
os.environ['FLYLOOP_NOISE_EPS']='0.25'
os.environ['FLYLOOP_ARMS']='FULL,FULL-RAW,EPISODIC'
os.environ['FLYLOOP_PREDSET']='V7C'
os.chdir(r'D:\djr82\flyloop')
sys.argv = ['supervisor', '--run-dir', r'D:\djr82\flyloop\runs\v7c_20260930_0029', '--duration-h', '2.5']
from flyloop.supervisor import main
main()
import os, sys
os.environ['FLYLOOP_PORT']='56885'
os.environ['FLYLOOP_PORT_MATCHED']='56886'
os.environ['FLYLOOP_PORT_EPI']='56887'
os.environ['FLYLOOP_NOISE_EPS']='0.25'
os.environ['FLYLOOP_ARMS']='FULL,FULL-RAW,EPISODIC'
os.environ['FLYLOOP_PREDSET']='V7C'
os.chdir(r'D:\djr82\flyloop')
sys.argv = ['supervisor', '--run-dir', r'D:\djr82\flyloop\runs\v7c_20260929_1618', '--duration-h', '2.5']
from flyloop.supervisor import main
main()
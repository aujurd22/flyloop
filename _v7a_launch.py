import os, sys
os.environ['FLYLOOP_NOISE_EPS']='0.25'
os.environ['FLYLOOP_ARMS']='FULL-RAW,MATCHED-VER'
os.environ['FLYLOOP_PREDSET']='V7A'
os.chdir(r'D:\djr82\flyloop')
sys.argv = ['supervisor', '--run-dir', r'D:\djr82\flyloop\runs\v7a_20260929_0242', '--duration-h', '2']
from flyloop.supervisor import main
main()

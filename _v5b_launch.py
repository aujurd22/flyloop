import os, sys
os.environ['FLYLOOP_NOISE_EPS']='0.25'
os.chdir(r'D:\djr82\flyloop')
sys.argv = ['supervisor', '--run-dir', r'D:\djr82\flyloop\runs\v5b_20260928_1848', '--duration-h', '2']
from flyloop.supervisor import main
main()

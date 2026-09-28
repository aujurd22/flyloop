import os, sys
os.environ['FLYLOOP_NOISE_EPS']='0.25'
os.environ['FLYLOOP_MATCH_MIN_FRAC']='0.6'
os.chdir(r'D:\djr82\flyloop')
sys.argv = ['supervisor', '--run-dir', r'D:\djr82\flyloop\runs\v6t_20260928_2159', '--duration-h', '2']
from flyloop.supervisor import main
main()

import pickle
import argparse

parser = argparse.ArgumentParser(description="inflate training data")
parser.add_argument('path', type=str, help='path to file to inflate')
args = parser.parse_args()

f = open(args.path, 'rb')
while True:
	try:
		print pickle.load(f)
	except (EOFError):
		break
f.close()

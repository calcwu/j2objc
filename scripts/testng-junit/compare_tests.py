import sys

def main():
  if len(sys.argv) != 3:
    print('usage: compare_tests.py <master-tc-test-file> <branch-tc-test-file>')
    sys.exit(1)

  master_file = sys.argv[1]
  branch_file = sys.argv[2]
  print("master_file: ", master_file)
  print("branch_file: ", branch_file)
  master_tests = convert(master_file)
  branch_tests = convert(branch_file)

  for key in master_tests:
    master_count = master_tests[key]
    branch_count = branch_tests.get(key)
    if master_count != branch_count:
      print("{} expected {}, but got {}".format(key, master_count, branch_count))

def convert(file):
  data = {}
  with open(file) as f:
    lines = f.readlines()
    for line in lines:
      line = line.strip()
      if 'Passed' in line and line.endswith('Test'):
        tokens = line.strip().split(' ')
        last = len(tokens) - 1
        passed_count = tokens[last-12]
        skipped_count = tokens[last-8]
        failed_count = tokens[last-4]
        test_name = tokens[last]
        data[test_name] = "P{}_S{}_F{}".format(passed_count, skipped_count, failed_count)

  return data


if __name__ == '__main__':
  sys.exit(main())

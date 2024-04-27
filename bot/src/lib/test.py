import subprocess

output = subprocess.Popen(['ginza', 'てすと'], stdout=subprocess.PIPE, shell=True).communicate()[0]
print(output)
import argparse
import os
import subprocess
from pathlib import Path
import re

git_list = frozenset(('rvx_git_install', 'rvx_util','rvx_dev_util','rvx_tools','rvx_ssw','rvx_synthesizer_binary','rvx_hwlib','rvx_binary'))

class BitbucketInfo():
	def __init__(self, cwd:Path):
		self.info_path = Path(__file__).parent.resolve() / 'bitbucket_info.mh'
		self.username = None
		self.is_ssh_access = None
		self.is_wrong_info = True
		if self.info_path.is_file():
			info = self.info_path.read_text().split('\n')
			if len(info)==2:
				username = info[0].split('=')
				is_ssh_access = info[1].split('=')
				if len(username)!=2:
					pass
				elif len(is_ssh_access)!=2:
					pass
				elif username[0]!='BB_USERNAME':
					pass
				elif is_ssh_access[0]!='BB_SSH_ACCESS':
					pass
				else:
					self.username = username[1]
					if is_ssh_access[1]=='True':
						self.is_ssh_access = True
					else:
						self.is_ssh_access = False
					self.is_wrong_info = False

	def generate(self):
		self.username = input('username of bitbucket: ')
		while 1:
			self.is_ssh_access = input('do you access bitbucket using SSH? (yes/no):')
			if self.is_ssh_access=='yes':
				self.is_ssh_access = True
				break
			elif self.is_ssh_access=='no':
				self.is_ssh_access = False
				break
			elif not self.is_ssh_access:
				self.is_ssh_access = False
				break
			else:
				print('wrong answer!')
		self.is_wrong_info = False
		info = f'BB_USERNAME={self.username}'
		info += '\n'
		info += f'BB_SSH_ACCESS={self.is_ssh_access}'
		self.info_path.write_text(info)

class GitRepo():
	def __init__(self, bitbucket_info:BitbucketInfo, path:Path):
		self.bitbucket_info = bitbucket_info
		self.path = path.resolve()
		if self.path.is_dir():
			contents = subprocess.check_output('git remote -v', shell=True, cwd=self.path).decode()
			self.git_name = re.compile(r'\brvx_[a-zA-Z0-9_]+\.git\b').findall(contents)[0]
		else:
			self.git_name = None
	
	def get_remote_addr(self):
		if self.bitbucket_info.is_ssh_access:
			git_addr = f'git@bitbucket.org:kyuseung_han/{self.git_name}.git'
		else:
			git_addr = f'https://{self.bitbucket_info.username}@bitbucket.org/kyuseung_han/{self.git_name}.git'
		return git_addr

	def download(self, git_name:str):
		if bitbucket_info.is_wrong_info:
			print('wrong bitbucket info!')
		elif not self.path.is_dir():
			self.git_name = git_name
			git_addr = self.get_remote_addr()
			subprocess.run(args=[f'git clone {git_addr}'], shell=True, cwd=self.path.parent)
			if self.path.name!=self.git_name:
				subprocess.run(args=[f'mv {self.path.name} {self.git_name}'], shell=True, cwd=self.path.parent)

	def update(self):
		if self.path.is_dir():
			subprocess.run(args=['git pull origin master'], shell=True, cwd=self.path)
			
	def set_repo(self):
		if self.path.is_dir():
			git_addr = self.get_remote_addr()
			subprocess.run(args=[f'git remote set-url origin {git_addr}'], shell=True, cwd=self.path)
			subprocess.run(args=[f'git remote set-url --push origin {git_addr}'], shell=True, cwd=self.path)

if __name__ == '__main__':
	# argument
	parser = argparse.ArgumentParser(description='RVX git install')
	parser.add_argument('-cmd', '-c', nargs='+', help='command')
	parser.add_argument('-cwd', help='cwd')
	args = parser.parse_args()

	is_gui_mode = False
	if not args.cmd:
		is_gui_mode = True
	elif args.cmd[0]=='gui':
		is_gui_mode = True
	cmd_list = args.cmd

	if not args.cwd:
		cwd = Path('.')
	else:
		cwd = Path(args.cwd)
	cwd = cwd.resolve()

	bitbucket_info = BitbucketInfo(cwd)

	while 1:
		if is_gui_mode:
			while 1:
				cmd = input('[cmd]: ')
				if ' ' in cmd:
					print('No space for cmd')
				else:
					break
			cmd_list = [cmd]

		#
		for cmd in cmd_list:
			cmd_config = cmd.split('.')
			target = cmd_config[0]
			if len(cmd_config) >=2:
				action = cmd_config[1]
			else:
				action = None
			if target=='exit':
				is_gui_mode = False
				break
			elif target=='git_config':
				subprocess.run(args=['git config --global core.editor vim'], shell=True, cwd=cwd)
				subprocess.run(args=['git config --global credential.helper \'cache --timeout=864000\''], shell=True, cwd=cwd)
			elif target=='git_kshan':
				subprocess.run(args=['git config --global user.name \"Kyuseung Han\"'], shell=True, cwd=cwd)
				subprocess.run(args=['git config --global user.email han@etir.re.kr'], shell=True, cwd=cwd)
			elif target=='bitbucket' or target=='bb':
				bitbucket_info.generate()
			elif target in git_list:
				if bitbucket_info.is_wrong_info:
					print('wrong bitbucket info!')
				elif (not action) or action=='install':
					git_repo = GitRepo(bitbucket_info,cwd/target)
					git_repo.download(target)
				elif action=='update':
					git_repo = GitRepo(bitbucket_info,cwd/target)
					git_repo.update()
				elif action=='set_repo':
					git_repo = GitRepo(bitbucket_info,cwd/target)
					git_repo.set_repo()
			elif target=='update':
				if bitbucket_info.is_wrong_info:
					print('wrong bitbucket info!')
				else:
					for git_dir in cwd.glob('rvx_*'):
						if git_dir.is_dir() and git_dir.name in git_list:
							GitRepo(bitbucket_info,git_dir).update()
			elif target=='set_repo':
				if bitbucket_info.is_wrong_info:
					print('wrong bitbucket info!')
				else:
					for git_dir in cwd.glob('rvx_*'):
						if git_dir.is_dir() and git_dir.name in git_list:
							GitRepo(bitbucket_info,git_dir).set_repo()
			else:
				print(f'wrong target: {target}')
		#
		if not is_gui_mode:
			break

import platform
import argparse
import os
import subprocess
from pathlib import Path
import re

is_linux = (platform.system()=='Linux')
is_windows = not is_linux
python_cmd = 'python3' if is_linux else 'python'

git_list = frozenset(('rvx_init', 'rvx_util','rvx_dev_util','rvx_tools','rvx_ssw','rvx_synthesizer_binary','rvx_hwlib','rvx_binary'))

def execute_shell_cmd(cmd:str, cwd:Path):
  subprocess.run(args=[cmd], shell=True, cwd=cwd)

def get_shell_output(cmd:str, cwd:Path):
  return subprocess.check_output(cmd, shell=True, cwd=cwd).decode()

def make_executable(path:Path):
  if path.is_file():
    if is_linux:
      execute_shell_cmd(f'chmod +x {path.name}', path.parent)

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
    self.git_name = ''

    if self.path.is_dir():
      contents = get_shell_output('git remote -v', self.path)
      candidate_list = re.compile(r'(\brvx_[a-zA-Z0-9_]+).git\b').findall(contents)
      if candidate_list:
        self.git_name = candidate_list[0]
      if self.path.name!=self.git_name:
        print(f'Mismatch between directory name and remote repository! {self.path}')
    else:
      self.git_name = None
  
  def get_remote_addr(self, is_ssh_access:bool):
    if is_ssh_access:
      git_addr = f'git@bitbucket.org:kyuseung_han/{self.git_name}.git'
    else:
      git_addr = f'https://{self.bitbucket_info.username}@bitbucket.org/kyuseung_han/{self.git_name}.git'
    return git_addr

  def download(self, git_name:str):
    if bitbucket_info.is_wrong_info:
      print('wrong bitbucket info!')
    elif not self.path.is_dir():
      self.git_name = git_name
      git_addr = self.get_remote_addr(self.bitbucket_info.is_ssh_access)
      execute_shell_cmd(f'git clone {git_addr}', cwd=self.path.parent)
      if self.path.name!=self.git_name:
        execute_shell_cmd(f'mv {self.path.name} {self.git_name}', cwd=self.path.parent)

  def update(self):
    if self.path.is_dir():
      git_info_dir = self.path / '.git'
      if git_info_dir.exists():
        execute_shell_cmd('git pull origin master', cwd=self.path)
      
  def __set_repo(self, is_ssh_access:bool):
    if self.path.is_dir():
      git_addr = self.get_remote_addr(is_ssh_access)
      execute_shell_cmd(f'git remote set-url origin {git_addr}', cwd=self.path)
      execute_shell_cmd(f'git remote set-url --push origin {git_addr}', cwd=self.path)
      execute_shell_cmd('git remote -v', cwd=self.path)
  
  def set_repo(self):
    git_addr = self.__set_repo(self.bitbucket_info.is_ssh_access)
  
  def set_repo_ssh(self):
    git_addr = self.__set_repo(True)
  
  def set_repo_https(self):
    git_addr = self.__set_repo(False)
  
  def change_repo(self):
    if self.path.is_dir():
      self.git_name = input('changed git name: ')
      self.set_repo()

if __name__ == '__main__':
  # argument
  parser = argparse.ArgumentParser(description='RVX init')
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
        execute_shell_cmd('git config --global credential.helper \'cache --timeout=864000\'', cwd=cwd)

      elif target=='git_config_reset':
        execute_shell_cmd('git config --unset credential.helper', cwd=cwd)

      elif target=='git_kshan':
        execute_shell_cmd('git config --global core.editor vim', cwd=cwd)
        execute_shell_cmd('git config --global user.name \"Kyuseung Han\"', cwd=cwd)
        execute_shell_cmd('git config --global user.email han@etir.re.kr', cwd=cwd)

        execute_shell_cmd('git config --global color.branch auto', cwd=cwd)
        execute_shell_cmd('git config --global color.diff auto', cwd=cwd)
        execute_shell_cmd('git config --global color.interactive auto', cwd=cwd)
        execute_shell_cmd('git config --global color.status auto', cwd=cwd)

      elif target=='date':
        execute_shell_cmd('sudo rdate -s time.bora.net', cwd=cwd)

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
        elif action=='reinstall':
          pass
          '''
          @echo "git clone "$(shell git config --get remote.origin.url) > reinstall
          @chmod +x reinstall
          @mv reinstall ../
          '''
        else:
          assert 0, cmd

      elif target=='update':
        if bitbucket_info.is_wrong_info:
          print('wrong bitbucket info!')
        else:
          GitRepo(bitbucket_info,cwd).update()
          for git_dir in cwd.glob('rvx_*'):
            if git_dir.is_dir():
              GitRepo(bitbucket_info,git_dir).update()

      elif target=='set_repo':
        if bitbucket_info.is_wrong_info:
          print('wrong bitbucket info!')
        else:
          if not action:
            GitRepo(bitbucket_info,cwd).set_repo()
          elif action=='auto':
            GitRepo(bitbucket_info,cwd).set_repo()
          elif action=='ssh':
            GitRepo(bitbucket_info,cwd).set_repo_ssh()
          elif action=='https':
            GitRepo(bitbucket_info,cwd).set_repo_https()
          else:
            print(f'wrong action: {action}')

      elif target=='set_repo_sub':
        if bitbucket_info.is_wrong_info:
          print('wrong bitbucket info!')
        else:
          for git_dir in cwd.glob('rvx_*'):
            if git_dir.is_dir():
              GitRepo(bitbucket_info,git_dir).set_repo()

      elif target=='change_repo':
        if bitbucket_info.is_wrong_info:
          print('wrong bitbucket info!')
        else:
          GitRepo(bitbucket_info,cwd).change_repo()

      elif target=='update_script':
        rvx_init_dir = Path('.') / 'rvx_init'
        if is_linux:
          cmd_list = []
          cmd_list.append(f'make clean')
          cmd_list.append(f'git checkout .')
          cmd_list.append(f'git pull origin master')
          cmd_list.append(f'git submodule init')
          cmd_list.append(f'git submodule update')
          update_script_file = cwd / 'update.sh'
          update_script_file.write_text('\n'.join(cmd_list))
          make_executable(update_script_file)

      else:
        print(f'wrong target: {target}')
    #
    if not is_gui_mode:
      break


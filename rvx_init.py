import platform
import argparse
import os
import subprocess
from pathlib import Path
import re

is_linux = (platform.system()=='Linux')
is_windows = not is_linux
python_cmd = 'python3' if is_linux else 'python'

def execute_shell_cmd(cmd:str, cwd:Path):
  subprocess.run(args=[cmd], shell=True, cwd=cwd)

def get_shell_output(cmd:str, cwd:Path):
  return subprocess.check_output(cmd, shell=True, cwd=cwd).decode()

def get_git_name(path:Path):
  assert path.is_dir(), path
  result = get_git_url(path)
  re_git_name = memorize(reexp_identifier) + r'\.git\b'
  repo_name = re.findall(re_git_name,result, re.DOTALL)[0]
  return repo_name

github_set = frozenset('rvx_bi')

def generate_url(host:str, is_ssh_access:bool, repo_name:str):
  if host=='bitbucket':
    if is_ssh_access:
      url = f'git@bitbucket.org:kyuseung_han/{repo_name}.git'
    else:
      url = f'https://bitbucket.org/kyuseung_han/{repo_name}.git'
  elif host=='github':
    if is_ssh_access:
      url = f'git@github.com:rvx-etri/{repo_name}.git'
    else:
      url = f'https://github.com/rvx-etri/{repo_name}.git'
  else:
    assert 0, host
  return url

def set_url_to_repo(repo_name:str, url:str, path:Path):
  dotgit_path = path / '.git'
  assert dotgit_path.exists(), path
  if dotgit_path.is_dir():
    execute_shell_cmd(f'git remote set-url origin {url}', cwd=path)
  elif dotgit_path.is_file():
    execute_shell_cmd(f'git config -f .gitmodules submodule.{repo_name}.url \"{url}\"', cwd=path.parent)
  else:
    assert 0

def clone_repo(url:str, parent_path:Path):
  execute_shell_cmd(f'git clone {url}', cwd=parent_path)

if __name__ == '__main__':
  # argument
  parser = argparse.ArgumentParser(description='RVX init')
  parser.add_argument('-cmd', '-c', nargs='+', help='command')
  parser.add_argument('-cwd', help='cwd')
  args = parser.parse_args()

  assert args.cwd
  assert args.cmd

  cwd = Path(args.cwd)
  cwd = cwd.resolve().absolute()

  cmd_list = args.cmd

  for cmd in cmd_list:
    cmd_config = cmd.split('.')
    target = cmd_config[0]
    if len(cmd_config) >=2:
      action = cmd_config[1]
    else:
      action = None

    if 0:
      pass
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

    elif target.startswith('rvx_'):
      if 0:
        pass
      elif action=='bitbucket':
        url = generate_url('bitbucket', 0, target)
        repo_path = cwd / target
        if repo_path.is_dir():
          set_url_to_repo(target, url, repo_path)
        else:
          clone_repo(utl, cwd)
      elif action=='bitbucket_ssh':
        url = generate_url('bitbucket', 1, target)
        repo_path = cwd / target
        if repo_path.is_dir():
          set_url_to_repo(target, url, repo_path)
        else:
          clone_repo(utl, cwd)
      elif action=='github':
        url = generate_url('github', 0, target)
        repo_path = cwd / target
        if repo_path.is_dir():
          set_url_to_repo(target, url, repo_path)
        else:
          clone_repo(utl, cwd)
      elif action=='github_ssh':
        url = generate_url('github', 1, target)
        repo_path = cwd / target
        if repo_path.is_dir():
          set_url_to_repo(target, url, repo_path)
        else:
          clone_repo(utl, cwd)
      else:
        assert 0, action
    elif target=='update_rvx_repo':
      for rvx_repo in cwd.glob('rvx_*'):
        if rvx_repo.is_dir():
          execute_shell_cmd('git pull origin master', rvx_repo)
    else:
      print(f'wrong target: {target}')

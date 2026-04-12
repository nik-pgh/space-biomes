---
sidebar_position: 1
---

# Local Setup

## Environment Setup

To run Biomes locally, you'll need to have 64GB of memory.

Note that this repo supports dev containers so a quick way to setup your environment is to skip this section and [start a codespace](#github-codespaces). Read on for manual instructions.

- Install the Node version manager (https://github.com/nvm-sh/nvm).

  ```bash
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.4/install.sh | bash

  # Restart console

  nvm install v20
  nvm use v20
  ```

- Install [yarn](https://yarnpkg.com/)
  ```bash
  npm install -g yarn
  ```
- Install [Git LFS](https://git-lfs.github.com/) before cloning the repo or the binary files will have erroneous contents.
  - On Ubuntu,
    ```bash
    sudo apt-get install git-lfs
    ```
  - On MacOS,
    ```bash
    brew install git-lfs
    ```
- Install [Python version >=3.9,<=3.10](https://www.python.org/)
- Install [clang version >= 14](https://clang.llvm.org/)
- Install [Bazel](https://bazel.build/install)
  ```bash
  npm install -g @bazel/bazelisk
  ```
- Clone repo
  ```bash
  git clone https://github.com/ill-inc/biomes-game.git
  ```
- Run `git lfs pull` to ensure that the LFS files are up-to-date.
- Bootstrap the repo-managed Python environment. This keeps Biomes on a repeatable interpreter and avoids drifting onto `/usr/bin/python3`, which can report broken include paths for Bazel and pybind11 on macOS.
  ```bash
  brew install python@3.10
  ./scripts/with_biomes_python.sh ./.biomes/python3.10/bin/python -m pip install -r requirements.txt
  ```

  The supported local Python toolchain is:

  - interpreter: `/opt/homebrew/bin/python3.10`
  - managed venv path: `./.biomes/python3.10`

  `./b ...` now uses that managed venv automatically. The helper compares the managed venv's resolved base executable against the selected Python 3.10 executable, so repeated `./b ...` or `./scripts/with_biomes_python.sh ...` invocations do not recreate the venv just because Homebrew exposes both `/opt/homebrew/bin/python3.10` and `/opt/homebrew/opt/python@3.10/bin/python3.10`.
- Install [Redis 7.0.8](https://redis.io/)
  ```bash
  curl -s https://download.redis.io/releases/redis-7.0.8.tar.gz | tar xvz -C ${HOME} \
    && make -j`nproc` -C ${HOME}/redis-7.0.8 \
    && sudo make install -C ${HOME}/redis-7.0.8 \
    && rm -rf ${HOME}/redis-7.0.8
  ```

## Run Biomes

- In the Biomes repository directory,
  ```bash
  ./b data-snapshot run
  ```

  If you want to run Python commands directly, do it through the helper so they resolve the same interpreter and venv as `./b`:

  ```bash
  ./scripts/with_biomes_python.sh python -m pip --version
  ./scripts/with_biomes_python.sh python ./scripts/b/bootstrap.py data-snapshot run
  ```
- Visit `http://localhost:3000`.

## Coding Environment

- The recommended code editor is [VSCode](https://code.visualstudio.com/).

## Developing inside a container

If you want to jump right in with a ready-to-go dev environment (enabling you to skip all of the "Environment setup" steps above), you can take advantage of VS Code's "Developing inside a Container" feature. See [.devcontainer/README.md](https://github.com/ill-inc/biomes-game/blob/main/.devcontainer/README.md) for instructions on how to set that up.

### GitHub Codespaces

Building off the "Developing inside a container" support, you can also start
up a [GitHub Codespace](https://github.com/features/codespaces) in this repository by [clicking here](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=677467268&skip_quickstart=true). Make sure to choose "16-core" or better for "Machine type" (which should come with the required 64GB of memory). If you create a codespace, you should always open it in VS Code, _not_ a browser, so that you can access the dev server at `localhost:3000`, which a lot of the system is expecting.

## Common problems and solutions

### `yarn install` fails while compiling `segfault-handler`

This is an environment blocker, not a reconstruction blocker. If you are on Node 22 or another unsupported major, switch back to Node 20 and retry:

```bash
nvm install v20
nvm use v20
yarn install
```

Or on Homebrew-managed macOS setups:

```bash
brew install node@20 python@3.10
BIOMES_NODE_BIN="$(brew --prefix node@20)/bin/node" ./scripts/with_node20.sh yarn install
./scripts/with_biomes_python.sh python -m pip install -r requirements.txt
```

### `./b ...` or `pip install ./voxeloo` uses the wrong Python on macOS

If native builds pick up `/usr/bin/python3` from Command Line Tools, Bazel and pybind11 can fail because that interpreter reports include paths that do not exist on disk. Check the active toolchain:

```bash
/usr/bin/python3 - <<'PY'
import sysconfig
print(sysconfig.get_path("include"))
PY
./scripts/with_biomes_python.sh python - <<'PY'
import sysconfig
print(sysconfig.get_path("include"))
PY
```

The second command should resolve into `./.biomes/python3.10` backed by Homebrew Python 3.10. If you need to recreate the managed venv intentionally, remove `./.biomes/python3.10` and rerun any `./b ...` command.

### Port 3000 is already in use

This is also an environment blocker. Check what is listening before starting the web server:

```bash
yarn check:local-env
lsof -nP -iTCP:3000 -sTCP:LISTEN
```

If another local process is using the default port, either stop it:

```bash
lsof -ti tcp:3000 | xargs kill
```

or run the direct Next.js web server on a different port:

```bash
PORT=3100 yarn next dev
```

If you use the full `./b ...` local stack, keep in mind that many scripts and docs assume the main web entrypoint stays on `http://localhost:3000`.


### Discord error on startup

Disable Discord web hooks by adding:

```
discordHooksEnabled: false
```

to [biomes.config.dev.yaml](https://github.com/ill-inc/biomes-game/blob/main/biomes.config.dev.yaml).

### Error when using social logins (Twitch/Discord/Google)

Social logins will not work if you don't have access to the required API keys. Hence, they will not work for the local build, and should not be used.

### Invalid asset paths

Not found (404) errors of the form "Could not find `<asset-path>/<name>-<hash>.<extension>`" are often caused by having out of date assets, from a previous `./b data-snapshot run`.

To fix this, run:

```bash
./b data-snapshot uninstall
./b data-snapshot pull
```

to fetch the most up to date assets.

### Fails on login, or while creating an account

Don't use social login. Rather, create a new account using the developer workflow shown below.

- From `http://localhost:3000`, click "login".
  <img width="800px" alt="Login" src="/img/create-account-1.png" />
  <br/>
- From the login dialog, select "Login with Dev".
  <br/>
  <img width="400px" alt="Developer Login" src="/img/create-account-2.png" />
  <br/>
- From the developer login, "Create [a] New Account".
  <br/>
  <img width="400px" alt="Create account" src="/img/create-account-3.png" />
  <br/>
- This will prompt the intro scene.
  <br/>
  <img width="600px" alt="Enter game" src="/img/create-account-4.png" />

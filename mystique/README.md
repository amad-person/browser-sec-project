# Running Mystique in 2023

### Bug: While building Mystique, gclient can't find Python 2. 

Error message: 

```bash
/opt/depot_tools/gclient: line 22: exec: python: not found
```

Fix: Use updated Dockerfile

```dockerfile
FROM ubuntu:xenial

RUN apt-get update && \
	apt-get install -y vim git build-essential lsb sudo python && \
	apt-get clean

RUN ln -sf /usr/bin/python

RUN echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections
ADD build.tar.gz /opt/
RUN echo "N" | /opt/build/install-build-deps.sh && apt-get clean

RUN useradd builder -u 1000 -s /bin/bash -d /home/builder && \
	mkdir -p /home/builder && \
	cp /root/.bashrc /home/builder && \
	cp /root/.profile /home/builder && \
	chown -R builder:builder /home/builder

RUN cd /opt && \
	git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git && \
	chown -R builder:builder /opt/depot_tools

ADD patches /opt/patches
ADD args.gn /opt/
ADD do_build.sh /
```

### Bug: While building Mystique, ffmpeg (one of the third party dependencies) installation throws an error.

Error message: 

```bash
Error: Command 'git checkout --force --quiet cf2d534bf049984bf179d09488c5c86735ddbc1d' returned non-zero exit status 128 in /mnt/chromium/src/third_party/ffmpeg
fatal: reference is not a tree: cf2d534bf049984bf179d09488c5c86735ddbc1d
```

Fix: Force rebuild ffmpeg with correct commit hash

1. Remove `chromium/src/third_party/ffmpeg`
1. Run `git clean -f` in `chromium/src/`
1. Comment out `git reset --hard HEAD &&` in `mystique/do_build.sh`. You have to keep the `git checkout $CHROMIUM_COMMIT` still.
1. Go to `chromium/src/DEPS` and replace the ffmpeg version in the file with the following commit hash: `719c15aa9ad6983200b78e5dbc17443f649c8af9`
1. Rebuild docker image.
1. Restart Mystique build.

### Bug: Mystique's Chromium version (2016) doesn't support Apple Silicon.

Error message:

```bash
Hook '/usr/bin/python src/build/landmines.py' took 97.92 secs

________ running '/usr/bin/python src/tools/remove_stale_pyc_files.py src/android_webview/tools src/build/android src/gpu/gles2_conform_support src/infra src/ppapi src/printing src/third_party/catapult src/third_party/closure_compiler/build src/third_party/WebKit/Tools/Scripts src/tools' in '/mnt/chromium'

________ running '/usr/bin/python src/build/download_nacl_toolchains.py --mode nacl_core_sdk sync --extract' in '/mnt/chromium'
Traceback (most recent call last):
[OMITTED FOR BREVITY]
AssertionError: Unrecognized arch machine: aarch64
Error: Command '/usr/bin/python src/build/download_nacl_toolchains.py --mode nacl_core_sdk sync --extract' returned non-zero exit status 1 in /mnt/chromium
```

Fix: Build without nacl

1. Update Dockerfile with build flags

```dockerfile
ADD args.gn /opt/
RUN echo 'enable_nacl = false' >> /opt/args.gn
RUN echo 'nacl_clang = false' >> /opt/args.gn
```

1. Remove the following hook from `src/DEPS`

```
  {
    # This downloads binaries for Native Client's newlib toolchain.
    # Done in lieu of building the toolchain from scratch as it can take
    # anywhere from 30 minutes to 4 hours depending on platform to build.
    'name': 'nacltools',
    'pattern': '.',
    'action': [
        'python',
        'src/build/download_nacl_toolchains.py',
        '--mode', 'nacl_core_sdk',
        'sync', '--extract',
    ],
  },
```
Rebuild the docker image after making these changes, and run the build script.

### Bug: More Apple Silicon issues

```bash
________ running '/usr/bin/python src/build/linux/sysroot_scripts/install-sysroot.py --running-as-hook' in '/mnt/chromium'
Unrecognized host arch: aarch64
Error: Command '/usr/bin/python src/build/linux/sysroot_scripts/install-sysroot.py --running-as-hook' returned non-zero exit status 1 in /mnt/chromium
```

Fix: :(

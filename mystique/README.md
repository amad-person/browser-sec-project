# Running Mystique in 2023

### Bug: While building Mystique, gclient can't find Python 2. 

Error message: 

```bash
/opt/depot_tools/gclient: line 22: exec: python: not found
```

Fix: Updated Dockerfile

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

Fix: Force rebuild ffmpeg

1. Remove `chromium/src/third_party/ffmpeg`
1. Run `git clean -f` in `chromium/src/`
1. Restart build process.

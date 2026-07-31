FROM ubuntu:24.04

RUN <<EOF
apt-get update
apt-get install -y python3 python3-pip
ln -s /usr/bin/python3 /usr/bin/python
EOF

COPY . /stitch

WORKDIR /stitch

RUN <<EOF
pip install -r requirements.txt --break-system-packages
rm requirements.txt
mkdir models
EOF